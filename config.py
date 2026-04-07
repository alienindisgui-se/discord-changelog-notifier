"""Configuration constants for Discord changelog notifier."""

# Updated for April 2026 production API strings
AI_MODELS = {
    # Google's current stable workhorse for free tier
    "gemini": "gemini-2.5-flash", 
    
    # Meta's Llama 4 Scout on Groq (Corrected API ID)
    "groq": "meta-llama/llama-4-scout-17b-16e-instruct"
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

# Mock Data Configuration
MOCK_DATA = {
    "repo": "mock-repo-tracker",
    "branch": "feature/new-api",
    "title": "Update API and fix crashes",
    "description": "Added auto-compression for videos. Fixed a bug where big files crashed the app. We are currently working on a shared config loader.",
    "commits": ["fix: memory leak", "feat: added 10mb limit", "chore: update deps"]
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
