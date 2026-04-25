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
    1. CONSUMER IMPACT ("Speed, Visual, Content"): Only summarize changes that affect the end user. Translate technical jargon into clear, casual benefits based on these three pillars:
       - Speed & Efficiency: Faster performance, shorter intervals, reduced overhead, or bug fixes. (e.g., "Tjänsten är nu snabbare och stabilare.")
       - Visual & Display: Changes to Discord visuals, layout, or how the final text output reads.
       - Content & Scope: Expanded tracking, new accounts added, longer data storage, or new features.
    2. OBJECTIVE TONE: ZERO personal pronouns. Do not use "vi", "vår", "du", "dig", "din", or "vårt". (e.g., Use "Nu visas..." instead of "Du kan nu se...").
    3. STRICT LIMITS: Maximum 2 short sentences per bullet point. Maximum 3 bullet points per category.

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


def create_discord_embed(title: str, description: str, color: int, footer: str = None) -> Dict[str, Any]:
    """Create a Discord embed with standard structure."""
    embed = {
        "title": title,
        "description": description,
        "color": color
    }
    if footer:
        embed["footer"] = {"text": footer}
    return embed


def get_next_log_number(log_dir: str, date_prefix: str) -> int:
    """Find the next available log number for the given date."""
    log_number = 1
    while True:
        log_file = os.path.join(log_dir, f"{date_prefix}_{log_number}.log")
        if not os.path.exists(log_file):
            return log_number
        log_number += 1


def strip_markdown_code_blocks(text: str) -> str:
    """Strip markdown code block delimiters from text."""
    from config import MARKDOWN_JSON_START, MARKDOWN_END
    cleaned = text
    if cleaned.startswith(MARKDOWN_JSON_START):
        cleaned = cleaned[len(MARKDOWN_JSON_START):]
    if cleaned.endswith(MARKDOWN_END):
        cleaned = cleaned[:-len(MARKDOWN_END)]
    return cleaned


def format_bullet_points(items: List[str]) -> str:
    """Format items as bullet points."""
    from config import BULLET_POINT
    return "\n" + "\n".join([f"{BULLET_POINT}{item}" for item in items])
