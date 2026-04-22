import os
import json
import requests
import random
import logging
from datetime import datetime
from github import Github, Auth
import google.genai as genai
from groq import Groq
from dotenv import load_dotenv
from config import (
    AI_MODELS,
    LANGUAGE_CODES,
    CATEGORIES,
    LOG_DIR_DEFAULT,
    HTTP_SUCCESS_CODES,
    JSON_SCHEMA_TEMPLATE
)
from utils import (
    create_ai_prompt,
    process_category_keywords,
    create_discord_embed,
    get_next_log_number
)

# Load env vars for local testing (.env file)
load_dotenv()

# Set up logging with unique timestamped files
log_dir = os.getenv("LOG_DIR", LOG_DIR_DEFAULT)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create sequential log file for each run
date_prefix = datetime.now().strftime("%Y%m%d")
log_number = get_next_log_number(log_dir, date_prefix)
log_file = os.path.join(log_dir, f"{date_prefix}_{log_number}.log")

# Configure handlers with UTF-8 encoding
file_handler = logging.FileHandler(log_file, mode="w", encoding='utf-8')
stream_handler = logging.StreamHandler()
try:
    stream_handler.stream.reconfigure(encoding='utf-8')
except AttributeError:
    # Fallback for older Python versions
    import codecs
    stream_handler.stream = codecs.getwriter('utf-8')(stream_handler.stream.buffer)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        file_handler,
        stream_handler
    ]
)

LANGUAGE = os.getenv("LANGUAGE", "").lower().strip()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TEST_MODE = os.getenv("TEST_MODE", "") # 'pr' for local testing or empty for CI

def get_formatted_date(lang):
    now = datetime.now()
    if lang == LANGUAGE_CODES["sv"]:
        months = ["", "januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]
        return f"**{now.day} {months[now.month]} {now.year}**"
    return f"**{now.strftime('%B %d, %Y')}**"

def get_pr_data():
    """Fetches PR data depending on the environment (CI, Local PR)."""
    gh = Github(auth=Auth.Token(GITHUB_TOKEN))
    
    if TEST_MODE == "pr":
        repo_name = os.getenv("TEST_REPO") # e.g., "username/repo"
        if not repo_name:
            raise ValueError("TEST_REPO environment variable is required when TEST_MODE='pr'")
        repo = gh.get_repo(repo_name)
        
        # Single PR mode
        pr_number_str = os.getenv("TEST_PR_NUMBER")
        if not pr_number_str:
            raise ValueError("TEST_PR_NUMBER environment variable is required when TEST_MODE='pr'")
        pr_number = int(pr_number_str)
        pr = repo.get_pull(pr_number)
    else:
        # Running in GitHub Actions
        with open(os.getenv("GITHUB_EVENT_PATH"), 'r') as f:
            event = json.load(f)
        repo_name = os.getenv("GITHUB_REPOSITORY")
        pr_number = event['pull_request']['number']
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

    repo_short_name = repo_name.split('/')[-1]
    commits = [c.commit.message for c in pr.get_commits()]
    
    return [{
        "repo": repo_short_name,
        "branch": pr.head.ref,
        "title": pr.title,
        "description": pr.body or "No description provided.",
        "commits": commits,
        "pr_number": pr.number
    }]

def generate_ai_summary(pr_data, lang):
    """Randomly selects between Gemini and Groq AI providers."""
    providers = []
    
    # Add available providers to list
    if GEMINI_API_KEY:
        providers.append(("gemini", generate_gemini_summary))
    if GROQ_API_KEY:
        providers.append(("groq", generate_groq_summary))
    
    # If no providers available, use fallback
    if not providers:
        logging.info("No AI providers configured, using fallback categorization...")
        return generate_fallback_summary(pr_data, lang)
    
    # Try providers in order: Gemini first, then Groq
    # Try providers in order: Groq first, then Gemini
    for provider_name, provider_func in providers:
        try:
            logging.info(f"Using AI provider: {provider_name} ({AI_MODELS[provider_name]})")
            return provider_func(pr_data, lang)
        except Exception as e:
            logging.error(f"Selected AI provider ({provider_name}) failed: {e}")
            # Try other providers if available
            other_providers = [p for p in providers if p[0] != provider_name]
            if other_providers:
                fallback_name, fallback_func = random.choice(other_providers)
                logging.warning(f"Falling back to: {fallback_name}")
                try:
                    return fallback_func(pr_data, lang)
                except Exception as fallback_e:
                    logging.error(f"Fallback provider ({fallback_name}) also failed: {fallback_e}")
        
        # If all providers fail, use keyword fallback
        logging.warning("All AI providers failed, using keyword fallback...")
        return generate_fallback_summary(pr_data, lang)

def generate_gemini_summary(pr_data, lang):
    """Uses Gemini to categorize PR data into a strict JSON format."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = create_ai_prompt(pr_data, lang, JSON_SCHEMA_TEMPLATE)
    # logging.info(f"AI Prompt (Gemini):\n{prompt}")
    
    response = client.models.generate_content(
        model=AI_MODELS["gemini"],
        contents=prompt
    )
    
    # Log the raw response for debugging
    logging.info(f"Raw Gemini response: {response.text}")
    
    if not response.text or response.text.strip() == "":
        logging.error("Gemini returned empty response")
        raise ValueError("Empty response from Gemini")
    
    # Strip markdown code blocks if present
    cleaned_response = response.text
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]  # Remove ```json
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # Remove ```
    
    try:
        parsed_response = json.loads(cleaned_response)
        return parsed_response, "Gemini 2.5 Flash"
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse Gemini JSON response: {e}")
        logging.error(f"Response text was: {repr(response.text)}")
        logging.error(f"Cleaned response was: {repr(cleaned_response)}")
        raise e

def generate_groq_summary(pr_data, lang):
    """Uses Groq to categorize PR data into a strict JSON format."""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = create_ai_prompt(pr_data, lang, JSON_SCHEMA_TEMPLATE)
        
        response = client.chat.completions.create(
            model=AI_MODELS["groq"],
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content), "Groq Llama 4 Scout"
    
    except Exception as e:
        logging.error(f"Groq service unavailable ({e}), falling back...")
        return generate_fallback_summary(pr_data, lang)

def generate_fallback_summary(pr_data, lang):
    """Fallback categorization when AI service is unavailable."""
    title = pr_data['title'].lower()
    description = pr_data['description'].lower()
    commits = [c.lower() for c in pr_data['commits']]
    
    all_text = f"{title} {description} {' '.join(commits)}"
    
    # Process categories using utility functions
    improvements = process_category_keywords(
        all_text, ['feat', 'add', 'new', 'improve', 'enhance', 'update'],
        lang,
        {"sv": "Nya funktioner och förbättringar tillagda", "en": "New features and improvements added"}
    )
    
    bug_fixes = process_category_keywords(
        all_text, ['fix', 'bug', 'issue', 'error', 'crash', 'resolve'],
        lang,
        {"sv": "Buggfixar implementerade", "en": "Bug fixes implemented"}
    )
    
    wip = process_category_keywords(
        all_text, ['wip', 'work in progress', 'todo', 'in progress'],
        lang,
        {"sv": "Arbete pågår", "en": "Work in progress"}
    )
    
    known_issues = process_category_keywords(
        all_text, ['known issue', 'problem', 'limitation'],
        lang,
        {"sv": "Kända problem identifierade", "en": "Known issues identified"}
    )
    
    # If no categorization found, use title as improvement
    if not improvements and not bug_fixes and not wip and not known_issues:
        improvements.append(pr_data['title'])
    
    return {
        "improvements": improvements,
        "wip": wip,
        "bug_fixes": bug_fixes,
        "known_issues": known_issues
    }, "Keyword-based Fallback"

def send_to_discord(ai_data, repo_name, lang):
    """Formats the data according to the strict template and sends the Webhook."""
    lang_key = 'sv' if lang == 'sv' else 'en'
    
    embeds = []
    
    for key, config in CATEGORIES.items():
        items = ai_data.get(key, [])
        if items:
            # Format with bullet points, starting with newline
            description = "\n" + "\n".join([f"• {item}" for item in items])
            
            # Title format: "🚀 Förbättringar" (no repo name in title)
            title = f"{config[lang_key]}"
            
            embeds.append(create_discord_embed(title, description, config["color"]))
    
    payload = {
        "content": f"**{get_formatted_date(lang_key).replace('**', '')} - {repo_name}**",
        "embeds": embeds,
        "attachments": []
    }
    
    # Log payload for debugging
    formatted_payload = json.dumps(payload, indent=2, ensure_ascii=False)
    # Replace escaped newlines with actual newlines for better readability
    formatted_payload = formatted_payload.replace('\\n', '\n')
    logging.info("Payload to send:\n" + formatted_payload)
    
    if WEBHOOK_URL:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code in HTTP_SUCCESS_CODES:
            logging.info("Successfully sent to Discord!")
        else:
            logging.error(f"Failed to send webhook. Status: {response.status_code}, Response: {response.text}")
    else:
        logging.warning("No DISCORD_WEBHOOK set. Skipping actual network request.")

if __name__ == "__main__":
    logging.info(f"Starting release notes generation (Mode: {TEST_MODE or 'CI'})...")
    try:
        pr_data = get_pr_data()[0]  # Get the single PR from the list
        pr_number = pr_data.get('pr_number', 'N/A')
        logging.info(f"Processing PR #{pr_number}: {pr_data['title']}")
        
        ai_summary = generate_ai_summary(pr_data, LANGUAGE)
        ai_data, ai_model = ai_summary  # Fix tuple unpacking
        send_to_discord(ai_data, pr_data['repo'], LANGUAGE)
        logging.info(f"Completed PR #{pr_number}")
            
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        exit(1)