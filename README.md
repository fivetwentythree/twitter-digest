# Twitter Digest

A free, GitHub Actions-powered tool that generates a daily digest website of tweets from people you follow, with AI-powered summaries using Gemini 2.5 Flash.

## Features

- 🐦 **Twitter API v2** - Direct access to tweets (free tier: 100 requests/month)
- 🤖 **AI-powered summaries** using Gemini 2.5 Flash
- 🌐 **GitHub Pages hosting** - free static site with all your digests
- ⏰ **Automated daily updates** via GitHub Actions
- 🎨 **Dark theme** - GitHub-inspired design

## Setup

### 1. Fork/Clone the Repository

```bash
git clone https://github.com/yourusername/twitter-digest.git
cd twitter-digest
```

### 2. Get Twitter API Access (Free)

1. Go to [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
2. Create a new Project and App
3. Go to "Keys and Tokens" → Generate **Bearer Token**

### 3. Get Gemini API Key (Free)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"

### 4. Configure Twitter Handles

Edit `config/config.yaml`:

```yaml
handles:
  - "naval"
  - "paulg"
  - "elonmusk"
```

### 5. Add GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

| Secret | Description |
|--------|-------------|
| `TWITTER_BEARER_TOKEN` | Your Twitter API Bearer Token |
| `GEMINI_API_KEY` | Your Google Gemini API key |

### 6. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Under "Build and deployment", select **GitHub Actions** as the source

### 7. Run the Workflow

Either wait for the scheduled run (7:00 AM UTC daily) or trigger manually:
1. Go to Actions → Twitter Digest
2. Click "Run workflow"

Your digest will be available at `https://yourusername.github.io/twitter-digest/`

## Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-gemini-key"
export TWITTER_BEARER_TOKEN="your-twitter-bearer-token"

# Run
python -m twitter_digest.main

# View result
open docs/index.html
```

## Customization

### Adjust Schedule

Edit `.github/workflows/twitter-digest.yml`:

```yaml
schedule:
  - cron: "0 7 * * *"  # 7:00 AM UTC daily
```

### Custom AI Prompt

Add to `config/config.yaml`:

```yaml
gemini_prompt: |
  Your custom prompt here...
```

## Twitter API Free Tier Limits

- 100 requests per month
- ~10 tweets per user lookup
- Works great for small lists (5-10 handles)

For larger lists, consider Twitter API Basic ($100/month) or Pro.

## License

MIT
