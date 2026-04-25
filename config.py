"""Configuration constants for Discord changelog notifier."""

# Updated for April 2026 production API strings
AI_MODELS = {
    # Gemini models (strongest to weakest, all free tier)
    "gemini_1": "gemini-2.5-pro",
    "gemini_2": "gemini-2.5-flash",
    "gemini_3": "gemini-2.5-flash-lite",
    
    # Groq models (strongest to weakest, all free tier)
    "groq_1": "llama-3.3-70b-versatile",
    "groq_2": "meta-llama/llama-4-scout-17b-16e-instruct",
    "groq_3": "google/gemma-2-9b-it"
}

# Language Configuration
LANGUAGE_CODES = {
    "sv": "sv",
    "en": "en"
}

# HTTP Configuration
HTTP_SUCCESS_CODES = [200, 204]

# Embed Color Configuration
EMBED_COLORS = {
    "improvements": 3066993,
    "wip": 15844367,
    "bug_fixes": 15158332,
    "known_issues": 16705372
}

# Category Configuration
CATEGORIES = {
    "improvements": {"en": "🚀 Improvements", "sv": "🚀 Förbättringar", "color": EMBED_COLORS["improvements"]},
    "wip": {"en": "🚧 Work in Progress", "sv": "🚧 Pågående arbete", "color": EMBED_COLORS["wip"]},
    "bug_fixes": {"en": "🛠️ Bug Fixes", "sv": "🛠️ Buggfixar", "color": EMBED_COLORS["bug_fixes"]},
    "known_issues": {"en": "⚠️ Known Issues", "sv": "⚠️ Kända problem", "color": EMBED_COLORS["known_issues"]}
}


# Logging Configuration
LOG_DIR_DEFAULT = "logs"

# JSON Schema Template
JSON_SCHEMA_TEMPLATE = """{{
    "improvements": ["item 1", "item 2"],
    "wip": [],
    "bug_fixes": [],
    "known_issues": []
}
}"""
