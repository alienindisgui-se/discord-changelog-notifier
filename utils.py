"""Utility functions for Discord changelog notifier."""

from typing import Dict, List, Any
from config import LANGUAGE_CODES


def get_language_text(lang_key: str, sv_text: str, en_text: str) -> str:
    """Get localized text based on language code."""
    return sv_text if lang_key == LANGUAGE_CODES["sv"] else en_text


def create_ai_prompt(pr_data: Dict[str, Any], lang: str, schema_template: str) -> str:
    """Create AI prompt with standardized schema."""
    lang_inst = "Swedish" if lang == LANGUAGE_CODES["sv"] else "English"
    
    # Handle missing fields gracefully
    repo = pr_data.get('repo', 'Unknown')
    branch = pr_data.get('branch', 'Unknown')
    title = pr_data.get('title', 'Unknown')
    description = pr_data.get('description', 'No description')
    commits = pr_data.get('commits', [])
    
    return f"""
    Analyze the following Pull Request data and categorize the changes.
    Output the results strictly in {lang_inst}.
    Write short, professional bullet points.
    
    Repository: {repo}
    Branch: {branch}
    Title: {title}
    Description: {description}
    Commits: {commits}
    
    Respond ONLY with a JSON object using this exact schema. If a category has no items, leave the array empty. Do not include bullet points characters in the text, just the raw text.
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
    import os
    log_number = 1
    while True:
        log_file = os.path.join(log_dir, f"{date_prefix}_{log_number}.log")
        if not os.path.exists(log_file):
            return log_number
        log_number += 1
