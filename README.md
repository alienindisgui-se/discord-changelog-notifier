# AI Discord Release Notes

![AI Powered](https://img.shields.io/badge/AI%20Powered-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Repo Size](https://img.shields.io/github/repo-size/alienindisgui-se/discord-changelog-notifier?style=for-the-badge&color=blue)
![License](https://img.shields.io/github/license/alienindisgui-se/discord-changelog-notifier?style=for-the-badge&color=green)

A GitHub composite action that automatically summarizes pull request changes using AI and sends formatted release notes to Discord.

## Features

- 🤖 AI-powered summarization with 6 models (Gemini/Groq)
- � Sequential fallback across multiple AI models
- �📝 Automatic categorization (improvements, bug fixes, WIP, known issues)
- 🌍 Multi-language support (English/Swedish)
- 🎨 Beautiful Discord embed formatting with model display
- �️ Automatic fallback to keyword-based categorization
- 🧪 Comprehensive test suite with mock and real PR testing

## Quick Start

### 1. Add Repository Secrets

In your target repository, add these secrets:

- `DISCORD_WEBHOOK` - Your Discord webhook URL
- `GEMINI_API_KEY` - Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `GROQ_API_KEY` - Groq API key from [Groq Console](https://console.groq.com/)

### 2. Create Workflow File

Create `.github/workflows/discord-release-notes.yml`:

```yaml
name: Discord Release Notes

on:
  pull_request:
    types:
      - closed
    branches:
      - main

jobs:
  release-notes:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Send Release Notes to Discord
        uses: alienindisgui-se/discord-changelog-notifier@v1.0.0
        with:
          discord_webhook: ${{ secrets.DISCORD_WEBHOOK }}
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          groq_api_key: ${{ secrets.GROQ_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          language: ''  # Empty for English, 'sv' for Swedish
```

## AI Model Configuration

The action uses 6 AI models with automatic sequential fallback:

**Groq Models (Priority 1-3):**
1. `llama-3.3-70b-versatile` (strongest)
2. `meta-llama/llama-4-scout-17b-16e-instruct`
3. `google/gemma-2-9b-it`

**Gemini Models (Priority 4-6):**
4. `gemini-2.5-pro` (strongest)
5. `gemini-2.5-flash`
6. `gemini-2.5-flash-lite`

If a model fails (e.g., high demand error), the action automatically tries the next model in the sequence.

## Testing

### Test Runner

The project includes a comprehensive test runner (`test_runner.py`) that supports:

- **Mock data testing** - 8 predefined test cases covering all scenarios
- **Real repository testing** - Fetch actual closed PRs from any GitHub repository
- **AI model testing** - Test specific models or all 6 models
- **Discord webhook output** - All tests send actual webhooks for visual verification

#### Test Runner Commands

**Basic mock data testing:**
```bash
python test_runner.py
```

**Test specific AI model:**
```bash
python test_runner.py --model groq_1
python test_runner.py --model gemini_2
```

**Test all 6 AI models:**
```bash
python test_runner.py --test-all-models
```

**Test real repository PRs:**
```bash
python test_runner.py --repo alienindisgui-se/discord-changelog-notifier
```

**Test real PRs with limit:**
```bash
python test_runner.py --repo alienindisgui-se/discord-changelog-notifier --limit 5
```

**Test real PRs with specific model:**
```bash
python test_runner.py --repo alienindisgui-se/discord-changelog-notifier --model groq_1
```

**Test real PRs with all models:**
```bash
python test_runner.py --repo alienindisgui-se/discord-changelog-notifier --test-all-models
```

**Test with English language:**
```bash
python test_runner.py --language en
```

**Comprehensive example (most options):**
```bash
python test_runner.py --repo alienindisgui-se/discord-changelog-notifier --limit 10 --test-all-models --language en
```

#### Available Test Cases (Mock Data)

1. `improvements_only` - Only improvements
2. `bug_fixes_only` - Only bug fixes
3. `mixed_categories` - Mixed improvements and fixes
4. `wip_only` - Work in progress
5. `known_issues` - Known issues documented
6. `empty_description` - Empty PR description
7. `long_description` - Extensive documentation
8. `all_categories` - All categories combined

### Local Testing

For testing the main script with a specific PR:

1. Copy `.env.example` to `.env` in this repository
2. Fill in your API keys and test data:
   - `GITHUB_TOKEN` - Your GitHub personal access token
   - `TEST_REPO` - Repository to test with (e.g., "owner/repo")
   - `TEST_PR_NUMBER` - PR number to test with
   - `DISCORD_WEBHOOK` - Your Discord webhook
   - `GEMINI_API_KEY` - Your Gemini API key
   - `GROQ_API_KEY` - Your Groq API key
   - `TEST_MODE` - Set to `pr` for local testing
3. Run: `python main.py`

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `discord_webhook` | Yes | - | Discord webhook URL |
| `gemini_api_key` | No | - | Gemini API key |
| `groq_api_key` | No | - | Groq API key |
| `github_token` | Yes | - | GitHub token (use `${{ secrets.GITHUB_TOKEN }}`) |
| `language` | No | `''` | Output language: `''` for English, `'sv'` for Swedish |

## Discord Output Format

The Discord webhook sends:
- **Content**: Date and repository name
- **Embeds**: Categorized changes (improvements, bug fixes, WIP, known issues)
- **Model Embed**: Dark purple embed showing the AI model used (e.g., `**model:** llama-3.3-70b-versatile`)

## Documentation

For detailed setup instructions, advanced configurations, and troubleshooting, see [USAGE_GUIDE.md](USAGE_GUIDE.md).

## License

MIT License - feel free to use in your projects.
