"""Utility functions for Discord changelog notifier."""

from typing import Dict, List, Any
from config import LANGUAGE_CODES


def get_language_text(lang_key: str, sv_text: str, en_text: str) -> str:
    """Get localized text based on language code."""
    return sv_text if lang_key == LANGUAGE_CODES["sv"] else en_text


def create_ai_prompt(pr_data: Dict[str, Any], lang: str, schema_template: str) -> str:
    """Create AI prompt with standardized schema for a non-technical audience."""
    lang_inst = "Swedish" if lang == LANGUAGE_CODES["sv"] else "English"
    
    # Handle missing fields gracefully
    repo = pr_data.get('repo', 'Unknown')
    branch = pr_data.get('branch', 'Unknown')
    title = pr_data.get('title', 'Unknown')
    description = pr_data.get('description', 'No description')
    commits = pr_data.get('commits', [])
    
    return f"""
    Analyze the following Pull Request data and summarize the core changes for a NON-TECHNICAL audience.
    Output the results strictly in {lang_inst}.
    
    CRITICAL RULES:
    1. MAX 1 SHORT SENTENCE PER BULLET POINT. Be punchy and direct. Never use semicolons or long compound sentences.
    2. Focus ONLY on the concrete impact on the end-user or the service. What is the actual value?
    3. NO technical terms, NO explanations of how it was coded, NO details about specific UI tweaks (like "bold text" or "yellow to red colors").
    4. MAXIMUM 3 bullet points per category. Only pick the absolute most important changes. Drop the rest.
    
    EXAMPLES OF GOOD VS BAD OUTPUT:
    BAD: Systemet är nu mer pålitligt; det hanterar fel bättre genom att stoppa på ett ordnat sätt om det inte kan hämta information, och det har blivit bättre på att undvika blockeringar från YouTube för att säkerställa kontinuerlig spårning.
    GOOD: Tjänsten är nu mycket stabilare och har bättre skydd mot att blockeras av YouTube.
    
    BAD: Meddelanden om borttagna kommentarer är nu tydligare och mer informativa. De använder en tydligare varningssymbol, visar andelen borttagna kommentarer i fetstil och ändrar färg baserat på raderingsgraden.
    GOOD: Aviseringarna är uppdaterade för att vara tydligare och mer informativa vid en första anblick.
    
    BAD: Det kraschade ibland när det stötte på felaktiga video-ID:n; detta har korrigerats så att det nu ignorerar dåliga ID:n utan problem.
    GOOD: Rättade en bugg som kunde få systemet att krascha vid felaktiga videolänkar.

    Repository: {repo}
    Branch: {branch}
    Title: {title}
    Description: {description}
    Commits: {commits}
    
    Respond ONLY with a JSON object using this exact schema. If a category has no items that fit the criteria, leave the array empty. Do not include bullet points characters in the text, just the raw text.
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
