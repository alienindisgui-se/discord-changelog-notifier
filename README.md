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

1. Copy `.env.example` to `.env`
2. Fill in your API keys and test data
3. Run: `python main.py`

### Debug Mode

Set `DEBUG_LOOP_ALL_PRS="true"` in `.env` to loop through all PRs in the test repository for debugging.

## License

MIT License - feel free to use in your projects.
