import os
import json
import codecs
import requests
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

def is_high_demand_error(error_message):
    """Check if error is due to high demand/temporary unavailability."""
    high_demand_indicators = [
        "high demand",
        "temporary",
        "try again later",
        "503",
        "UNAVAILABLE"
    ]
    error_str = str(error_message).lower()
    return any(indicator in error_str for indicator in high_demand_indicators)

def generate_ai_summary(pr_data, lang):
    """Tries AI providers sequentially with proper fallback logic."""
    # Define provider order for fallback (capability-based)
    providers = []
    
    # Add available providers in priority order (Groq first, then Gemini as fallback)
    if GROQ_API_KEY:
        providers.append(("groq_1", lambda provider_pr_data, provider_lang: generate_groq_summary(provider_pr_data, provider_lang, "groq_1")))
        providers.append(("groq_2", lambda provider_pr_data, provider_lang: generate_groq_summary(provider_pr_data, provider_lang, "groq_2")))
        providers.append(("groq_3", lambda provider_pr_data, provider_lang: generate_groq_summary(provider_pr_data, provider_lang, "groq_3")))
    if GEMINI_API_KEY:
        providers.append(("gemini_1", lambda provider_pr_data, provider_lang: generate_gemini_summary(provider_pr_data, provider_lang, "gemini_1")))
        providers.append(("gemini_2", lambda provider_pr_data, provider_lang: generate_gemini_summary(provider_pr_data, provider_lang, "gemini_2")))
        providers.append(("gemini_3", lambda provider_pr_data, provider_lang: generate_gemini_summary(provider_pr_data, provider_lang, "gemini_3")))
    
    # If no providers available, use fallback
    if not providers:
        logging.info("No AI providers configured, using fallback categorization...")
        return generate_fallback_summary(pr_data, lang)
    
    # Try each provider sequentially
    for provider_name, provider_func in providers:
        try:
            logging.info("Trying AI provider: {} ({})".format(provider_name, AI_MODELS[provider_name]))
            return provider_func(pr_data, lang)
        except Exception as e:
            error_str = str(e)
            logging.error("AI provider ({}) failed: {}".format(provider_name, e))
            
            # If it's a high demand error, try next provider
            if is_high_demand_error(error_str):
                remaining_providers = [p for p in providers if p[0] != provider_name]
                if remaining_providers:
                    logging.warning("High demand error detected, trying next provider...")
                    continue
                else:
                    logging.warning("All providers exhausted due to high demand, using keyword fallback...")
                    return generate_fallback_summary(pr_data, lang)
            else:
                # For other errors, try next provider
                remaining_providers = [p for p in providers if p[0] != provider_name]
                if remaining_providers:
                    logging.warning("Trying next provider...")
                    continue
                else:
                    logging.warning("All AI providers failed, using keyword fallback...")
                    return generate_fallback_summary(pr_data, lang)
    
    # If we get here, all providers failed
    logging.warning("All AI providers failed, using keyword fallback...")
    return generate_fallback_summary(pr_data, lang)

def generate_gemini_summary(pr_data, lang, provider_name="gemini_1"):
    """Uses Gemini to categorize PR data into a strict JSON format."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = create_ai_prompt(pr_data, lang, JSON_SCHEMA_TEMPLATE)
    # logging.info(f"AI Prompt (Gemini):\n{prompt}")
    
    response = client.models.generate_content(
        model=AI_MODELS[provider_name],
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
        model_display = AI_MODELS[provider_name]
        return parsed_response, model_display
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse Gemini JSON response: {e}")
        logging.error(f"Response text was: {repr(response.text)}")
        logging.error(f"Cleaned response was: {repr(cleaned_response)}")
        raise e

def generate_groq_summary(pr_data, lang, provider_name="groq_1"):
    """Uses Groq to categorize PR data into a strict JSON format."""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = create_ai_prompt(pr_data, lang, JSON_SCHEMA_TEMPLATE)
        
        response = client.chat.completions.create(
            model=AI_MODELS[provider_name],
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Log the raw response for debugging
        logging.info("Raw Groq response: {}".format(response.choices[0].message.content))
        
        model_display = AI_MODELS[provider_name]
        return json.loads(response.choices[0].message.content), model_display
    
    except Exception as e:
        logging.error("Groq service unavailable ({}), falling back...".format(e))
        raise

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

def send_to_discord(ai_data, repo_name, lang, ai_model=None):
    """Formats the data according to the strict template and sends the Webhook."""
    lang_key = 'sv' if lang == 'sv' else 'en'
    
    embeds = []
    
    for key, config in CATEGORIES.items():
        items = ai_data.get(key, [])
        if items:
            # Format with bullet points, starting with newline
            description = "\n" + "\n".join([f"• {item}" for item in items])
            
            # Title format: "Förbättringar" (no repo name in title)
            title = f"{config[lang_key]}"
            
            embeds.append(create_discord_embed(title, description, config["color"]))
    
    content = f"**{get_formatted_date(lang_key).replace('**', '')} - {repo_name}**"
    
    # Add model as footer embed if available
    if ai_model:
        embeds.append(create_discord_embed("", "model: {}".format(ai_model), 0x581845))  # Dark purple
    
    # If no embeds (and no model embed), log warning and don't send webhook
    if not embeds:
        logging.warning("No embeds generated - AI returned empty categories. PR data: {}".format(pr_data))
        logging.warning("Skipping Discord webhook due to empty content")
        return
    
    payload = {
        "content": content,
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
        send_to_discord(ai_data, pr_data['repo'], LANGUAGE, ai_model)
        logging.info(f"Completed PR #{pr_number}")
            
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        exit(1)