"""Utility functions for Discord changelog notifier."""

import os
from typing import Dict, List, Any
from config import LANGUAGE_CODES


def get_language_text(lang_key: str, sv_text: str, en_text: str) -> str:
    """Get localized text based on language code."""
    return sv_text if lang_key == LANGUAGE_CODES["sv"] else en_text


def create_ai_prompt(pr_data: Dict[str, Any], lang: str, schema_template: str) -> str:
    """Create AI prompt focused on objective user value without personal pronouns."""
    lang_inst = "Swedish" if lang == LANGUAGE_CODES["sv"] else "English"
    
    # Handle missing fields gracefully
    repo = pr_data.get('repo', 'Unknown')
    branch = pr_data.get('branch', 'Unknown')
    title = pr_data.get('title', 'Unknown')
    description = pr_data.get('description', 'No description')
    commits = pr_data.get('commits', [])
    
    return f"""
    Analyze the following Pull Request and summarize changes for a general, non-technical audience.
    Output language: {lang_inst}.

    STRICT LOGIC RULES:
    1. NO PERSONAL PRONOUNS: Do not use words like "vi", "vår", "du", "dig", "din" or "vårt". Use a neutral, objective tone. 
       - Instead of "Vi har förbättrat...", use "Förbättrad..." or "Systemet har blivit...".
       - Instead of "Du kan nu se...", use "Nu visas...".
    2. LENGTH: MAX 2 SHORT SENTENCES per bullet point. 
    3. THE "COMMON PERSON" TRANSLATION: Translate technical tasks into clear, casual benefits:
       - Scraping/Efficiency -> "Tjänsten är nu snabbare och använder mindre resurser."
       - Anti-bot/Detection -> "Skyddet mot att blockeras av externa plattformar har stärkts."
       - History/Storage -> "Historik sparas nu i 4 dagar istället för 3 för en bättre överblick."
       - Prompt changes -> "AI-sammanfattningarna har finjusterats för att bli mer lättlästa."
       - Code cleanup -> "Systemet har städats upp för att möjliggöra smidigare uppdateringar."
    4. PRODUCT FOCUS: Mention changes that affect the final text output, Discord visuals, or the scope of tracking.
    5. LIMIT: Maximum 3 bullet points per category.

    DATA TO ANALYZE:
    Repository: {repo}
    Branch: {branch}
    Title: {title}
    Description: {description}
    Commits: {commits}
    
    Respond ONLY with a JSON object using this exact schema. If a category is empty, return []. 
    No markdown bullet points in the JSON strings.
    {schema_template}
    """


def process_category_keywords(all_text: str, keywords: List[str], lang: str, message_template: Dict[str, str]) -> List[str]:
    """Process category keywords and return appropriate messages."""
    if any(keyword in all_text for keyword in keywords):
        return [get_language_text(lang, message_template["sv"], message_template["en"])]
    return []


def create_discord_embed(title: str, description: str, color: int) -> Dict[str, Any]:
    """Create a Discord embed with standard structure."""
    return {
        "title": title,
        "description": description,
        "color": color
    }


def get_next_log_number(log_dir: str, date_prefix: str) -> int:
    """Find the next available log number for the given date."""
    log_number = 1
    while True:
        log_file = os.path.join(log_dir, f"{date_prefix}_{log_number}.log")
        if not os.path.exists(log_file):
            return log_number
        log_number += 1
