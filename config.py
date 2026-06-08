"""Configuration constants for Discord changelog notifier."""

# Updated for April 2026 production API strings
# Least-expensive models: keep 1 Gemini and 1 Groq option for provider fallback.
AI_MODELS = {
    # Gemini (cheapest first)
    "gemini_2": "gemini-2.5-flash-lite",

    # Groq (cheapest first)
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

# String Constants
ENCODING_UTF8 = "utf-8"
TEST_MODE_PR = "pr"
MARKDOWN_JSON_START = "```json"
MARKDOWN_END = "```"
BULLET_POINT = "• "
MODEL_EMBED_COLOR = 0x581845
DEFAULT_DESCRIPTION = "No description provided."
FALLBACK_MODEL_NAME = "Keyword-based Fallback"

# Environment Variable Names
ENV_DISCORD_WEBHOOK = "DISCORD_WEBHOOK"
ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
ENV_GROQ_API_KEY = "GROQ_API_KEY"
ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ENV_TEST_MODE = "TEST_MODE"
ENV_LANGUAGE = "LANGUAGE"
ENV_LOG_DIR = "LOG_DIR"
ENV_TEST_REPO = "TEST_REPO"
ENV_TEST_PR_NUMBER = "TEST_PR_NUMBER"
ENV_GITHUB_EVENT_PATH = "GITHUB_EVENT_PATH"
ENV_GITHUB_REPOSITORY = "GITHUB_REPOSITORY"
