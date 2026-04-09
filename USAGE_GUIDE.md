# Usage Guide: AI Discord Release Notes Action

This guide explains how to use the AI Discord Release Notes composite action in your GitHub projects to automatically generate and send release notes to Discord when PRs are merged.

## Overview

The action summarizes pull request changes using AI (Gemini or Groq) and sends formatted release notes to a Discord webhook. It categorizes changes into improvements, bug fixes, work in progress, and known issues.

## Prerequisites

1. **Discord Webhook**: Create a Discord webhook URL for your target channel
2. **AI API Key**: Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **GitHub Repository**: The action must be published or accessible to your target repositories

## Step 1: Publish the Action

### Option A: Publish to GitHub Marketplace (Recommended)

1. Ensure this repository is public
2. Create a release with a tag (e.g., `v1.0.0`)
3. The action will be available at: `username/discord-changelog-notifier@v1.0.0`

### Option B: Use from Private Repository

1. Make sure the action repository is accessible to your target repositories
2. Use the full repository path: `owner/repo@ref`

## Step 2: Configure Repository Secrets

In each repository where you want to use this action, add the following secrets:

### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `DISCORD_WEBHOOK` | Discord webhook URL | Create webhook in Discord channel settings |
| `GEMINI_API_KEY` | Gemini API key | Get from [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GITHUB_TOKEN` | GitHub token | Use `${{ secrets.GITHUB_TOKEN }}` (auto-provided) |

### Adding Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its corresponding value

## Step 3: Create Workflow File

Create a workflow file in your target repository at `.github/workflows/discord-release-notes.yml`:

### Basic Configuration (English)

```yaml
name: Discord Release Notes

on:
  pull_request:
    types:
      - closed
    branches:
      - main
      - master

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

### Swedish Language Configuration

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
          language: 'sv'  # Swedish language output
```

### Multi-Branch Configuration

```yaml
name: Discord Release Notes

on:
  pull_request:
    types:
      - closed

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
          language: ''  # Empty for English
```

## Step 4: Customize Trigger Events

The action can be triggered on various events. Here are common configurations:

### On PR Merge to Main Branch Only

```yaml
on:
  pull_request:
    types:
      - closed
    branches:
      - main
```

### On Any PR Merge

```yaml
on:
  pull_request:
    types:
      - closed
```

### On Release Creation

```yaml
on:
  release:
    types:
      - published
```

### Manual Trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      pr_number:
        description: 'PR number to generate notes for'
        required: true
```

## Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `discord_webhook` | Yes | - | Discord webhook URL |
| `ai_api_key` | Yes | - | Gemini API key for AI summarization |
| `github_token` | Yes | - | GitHub token (use `${{ secrets.GITHUB_TOKEN }}`) |
| `language` | No | `''` | Output language: `''` for English, `'sv'` for Swedish |

## Troubleshooting

### Action Not Running

- Verify the workflow file is in `.github/workflows/`
- Check that the trigger conditions match your PR events
- Ensure the action repository is accessible

### Discord Not Receiving Messages

- Verify the webhook URL is correct
- Check Discord channel permissions for the webhook
- Review GitHub Actions logs for errors

### API Key Errors

- Ensure the Gemini API key is valid and has quota
- Check that the secret is correctly named in your repository
- Verify the secret is not accidentally exposed in logs

### Permission Issues

- Ensure the workflow has permissions to read repository content
- Add permissions to your workflow if needed:

```yaml
permissions:
  contents: read
  pull-requests: read
```

## Advanced Configuration

### Using Groq Instead of Gemini

The action automatically falls back to Groq if Gemini fails. To use Groq exclusively, you can modify the action or add `GROQ_API_KEY` as a secret.

### Custom Categories

To customize the categorization logic, modify the `CATEGORIES` dictionary in `config.py` and the keyword matching in `utils.py`.

### Rate Limiting

If you have many PRs merging quickly, consider adding a delay or rate limiting to avoid hitting API limits.

## Example: Complete Workflow with Permissions

```yaml
name: Discord Release Notes

on:
  pull_request:
    types:
      - closed
    branches:
      - main

permissions:
  contents: read
  pull-requests: read

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
          language: ''
```

## Support

For issues or questions:
- Check the GitHub Actions logs for detailed error messages
- Review the action repository for updates
- Ensure all secrets are properly configured
