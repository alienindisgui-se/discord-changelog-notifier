import os
import json
import requests
import random
import logging
from datetime import datetime
from github import Github
import google.genai as genai
from groq import Groq
from dotenv import load_dotenv

# Load env vars for local testing (.env file)
load_dotenv()

# Set up logging with unique timestamped files
log_dir = os.getenv("LOG_DIR", "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create sequential log file for each run
date_prefix = datetime.now().strftime("%Y%m%d")
log_number = 1

# Find next available log number
while True:
    log_file = os.path.join(log_dir, f"{date_prefix}_{log_number}.log")
    if not os.path.exists(log_file):
        break
    log_number += 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w"),  # Use 'w' mode for new file each run
        logging.StreamHandler()
    ]
)

LANGUAGE = os.getenv("LANGUAGE", "").lower().strip()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TEST_MODE = os.getenv("TEST_MODE", "") # 'mock', 'pr', or empty for CI

# --- Configuration & Templates ---
CATEGORIES = {
    "improvements": {"en": "🚀 Improvements", "sv": "🚀 Förbättringar", "color": 3066993},
    "wip": {"en": "🚧 Work in Progress", "sv": "🚧 Pågående arbete", "color": 15844367},
    "bug_fixes": {"en": "🛠️ Bug Fixes", "sv": "🛠️ Buggfixar", "color": 15158332},
    "known_issues": {"en": "⚠️ Known Issues", "sv": "⚠️ Kända problem", "color": 16705372}
}

def get_formatted_date(lang):
    now = datetime.now()
    if lang == 'sv':
        months = ["", "januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]
        return f"**{now.day} {months[now.month]} {now.year} – Uppdateringar**"
    return f"**{now.strftime('%B %d, %Y')} – Updates**"

def get_pr_data():
    """Fetches PR data depending on the environment (CI, Local Mock, Local PR)."""
    if TEST_MODE == "mock":
        return {
            "repo": "mock-repo-tracker",
            "branch": "feature/new-api",
            "title": "Update API and fix crashes",
            "description": "Added auto-compression for videos. Fixed a bug where big files crashed the app. We are currently working on a shared config loader.",
            "commits": ["fix: memory leak", "feat: added 10mb limit", "chore: update deps"]
        }

    gh = Github(GITHUB_TOKEN)
    
    if TEST_MODE == "pr":
        repo_name = os.getenv("TEST_REPO") # e.g., "username/repo"
        pr_number = int(os.getenv("TEST_PR_NUMBER"))
        repo = gh.get_repo(repo_name)
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
    
    return {
        "repo": repo_short_name,
        "branch": pr.head.ref,
        "title": pr.title,
        "description": pr.body or "No description provided.",
        "commits": commits
    }

def generate_ai_summary(pr_data, lang):
    """Randomly selects between Gemini and Groq AI providers."""
    providers = []
    
    # Add available providers to list
    if GROQ_API_KEY:
        providers.append(("groq", generate_groq_summary))
    if GEMINI_API_KEY:
        providers.append(("gemini", generate_gemini_summary))
    
    # If no providers available, use fallback
    if not providers:
        logging.info("No AI providers configured, using fallback categorization...")
        return generate_fallback_summary(pr_data, lang)
    
    # Try providers in order: Groq first, then Gemini
    for provider_name, provider_func in providers:
        try:
            logging.info(f"Using AI provider: {provider_name}")
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
    
    lang_inst = "Swedish" if lang == 'sv' else "English"
    
    prompt = f"""
    Analyze the following Pull Request data and categorize the changes.
    Output the results strictly in {lang_inst}.
    Write short, professional bullet points.
    
    Repository: {pr_data['repo']}
    Branch: {pr_data['branch']}
    Title: {pr_data['title']}
    Description: {pr_data['description']}
    Commits: {pr_data['commits']}
    
    Respond ONLY with a JSON object using this exact schema. If a category has no items, leave the array empty. Do not include bullet points characters in the text, just the raw text.
    {{
        "improvements": ["item 1", "item 2"],
        "wip": [],
        "bug_fixes": [],
        "known_issues": []
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return json.loads(response.text), "Gemini 2.0 Flash"

def generate_groq_summary(pr_data, lang):
    """Uses Groq to categorize PR data into a strict JSON format."""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        lang_inst = "Swedish" if lang == 'sv' else "English"
        
        prompt = f"""
        Analyze the following Pull Request data and categorize the changes.
        Output the results strictly in {lang_inst}.
        Write short, professional bullet points.
        
        Repository: {pr_data['repo']}
        Branch: {pr_data['branch']}
        Title: {pr_data['title']}
        Description: {pr_data['description']}
        Commits: {pr_data['commits']}
        
        Respond ONLY with a JSON object using this exact schema. If a category has no items, leave the array empty. Do not include bullet points characters in the text, just the raw text.
        {{
            "improvements": ["item 1", "item 2"],
            "wip": [],
            "bug_fixes": [],
            "known_issues": []
        }}
        """
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content), "Groq Llama 3.1 8B"
    
    except Exception as e:
        logging.error(f"Groq service unavailable ({e}), falling back...")
        return generate_fallback_summary(pr_data, lang)

def generate_fallback_summary(pr_data, lang):
    """Fallback categorization when AI service is unavailable."""
    title = pr_data['title'].lower()
    description = pr_data['description'].lower()
    commits = [c.lower() for c in pr_data['commits']]
    
    improvements = []
    bug_fixes = []
    wip = []
    known_issues = []
    
    # Simple keyword-based categorization
    all_text = f"{title} {description} {' '.join(commits)}"
    
    if any(keyword in all_text for keyword in ['feat', 'add', 'new', 'improve', 'enhance', 'update']):
        if lang == 'sv':
            improvements.append("Nya funktioner och förbättringar tillagda")
        else:
            improvements.append("New features and improvements added")
    
    if any(keyword in all_text for keyword in ['fix', 'bug', 'issue', 'error', 'crash', 'resolve']):
        if lang == 'sv':
            bug_fixes.append("Buggfixar implementerade")
        else:
            bug_fixes.append("Bug fixes implemented")
    
    if any(keyword in all_text for keyword in ['wip', 'work in progress', 'todo', 'in progress']):
        if lang == 'sv':
            wip.append("Arbete pågår")
        else:
            wip.append("Work in progress")
    
    if any(keyword in all_text for keyword in ['known issue', 'problem', 'limitation']):
        if lang == 'sv':
            known_issues.append("Kända problem identifierade")
        else:
            known_issues.append("Known issues identified")
    
    # If no categorization found, use title as improvement
    if not improvements and not bug_fixes and not wip and not known_issues:
        if lang == 'sv':
            improvements.append(pr_data['title'])
        else:
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
            # Format with bullet points
            description = "\n".join([f"• {item}" for item in items])
            
            # Title format: "🚀 Förbättringar: repo-name" (matching your example)
            title = f"{config[lang_key]}: {repo_name}" if key in ["improvements", "bug_fixes"] else config[lang_key]
            
            embeds.append({
                "title": title,
                "description": description,
                "color": config["color"]
            })
    
    payload = {
        "content": get_formatted_date(lang_key),
        "embeds": embeds,
        "attachments": []
    }
    
    # Log payload for debugging
    logging.info("Payload to send:\n" + json.dumps(payload, indent=2, ensure_ascii=True))
    
    if WEBHOOK_URL:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            logging.info("Successfully sent to Discord!")
        else:
            logging.error(f"Failed to send webhook. Status: {response.status_code}, Response: {response.text}")
    else:
        logging.warning("No DISCORD_WEBHOOK set. Skipping actual network request.")

if __name__ == "__main__":
    logging.info(f"Starting release notes generation (Mode: {TEST_MODE or 'CI'})...")
    try:
        pr_data = get_pr_data()
        ai_summary, ai_model = generate_ai_summary(pr_data, LANGUAGE)
        send_to_discord(ai_summary, pr_data['repo'], LANGUAGE)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        exit(1)