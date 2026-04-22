# AI Discord Release Notes

A GitHub composite action that automatically summarizes pull request changes using AI and sends formatted release notes to Discord.

## Features

- 🤖 AI-powered summarization (Gemini/Groq)
- 📝 Automatic categorization (improvements, bug fixes, WIP, known issues)
- 🌍 Multi-language support (English/Swedish)
- 🎨 Beautiful Discord embed formatting
- 🔄 Automatic fallback to keyword-based categorization

## Quick Start

### 1. Add Repository Secrets

In your target repository, add these secrets:

- `DISCORD_WEBHOOK` - Your Discord webhook URL
- `GEMINI_API_KEY` - Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Create Workflow File

Create `.github/workflows/discord-release-notes.yml`:

**That's it!** The action automatically detects the PR from GitHub Actions. No additional configuration needed.

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
          ai_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          language: ''  # Empty for English, 'sv' for Swedish
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `discord_webhook` | Yes | - | Discord webhook URL |
| `ai_api_key` | Yes | - | Gemini API key |
| `github_token` | Yes | - | GitHub token (use `${{ secrets.GITHUB_TOKEN }}`) |
| `language` | No | `''` | Output language: `''` for English, `'sv'` for Swedish |

## Documentation

For detailed setup instructions, advanced configurations, and troubleshooting, see [USAGE_GUIDE.md](USAGE_GUIDE.md).

## Development

### Local Testing

For testing changes to the action itself:

1. Copy `.env.example` to `.env` in this repository
2. Fill in your API keys and test data:
   - `GITHUB_TOKEN` - Your GitHub personal access token
   - `TEST_REPO` - Repository to test with (e.g., "owner/repo")
   - `TEST_PR_NUMBER` - PR number to test with
   - `DISCORD_WEBHOOK` - Your Discord webhook (optional)
   - `GEMINI_API_KEY` - Your Gemini API key (optional)
3. Run: `python main.py`

**Note:** The `.env` file is only needed for local development of this action. Target repositories using this action don't need any `.env` file.

## License

MIT License - feel free to use in your projects.
