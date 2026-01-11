# Twitter Digest

A free, GitHub Actions-powered tool that generates a daily digest website of tweets from people you follow, with AI-powered summaries using Gemini 2.5 Flash.

## Features

- 📡 **RSS-based fetching** via Nitter instances (no Twitter API needed)
- 🤖 **AI-powered summaries** using Gemini 2.5 Flash
- 🌐 **GitHub Pages hosting** - free static site with all your digests
- ⏰ **Automated daily updates** via GitHub Actions
- 🔄 **Fallback handling** for Nitter instances and Gemini API

## Setup

### 1. Fork/Clone the Repository

```bash
git clone https://github.com/yourusername/twitter-digest.git
cd twitter-digest
```

### 2. Configure Twitter Handles

Edit `config/config.yaml` to add the Twitter handles you want to track:

```yaml
handles:
  - "naval"
  - "paulg"
  - "elonmusk"
```

### 3. Add Gemini API Key

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Description |
|-------------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey)) |

### 4. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Under "Build and deployment", select **GitHub Actions** as the source

### 5. Run the Workflow

Either wait for the scheduled run (7:00 AM UTC daily) or trigger manually:

1. Go to Actions → Twitter Digest
2. Click "Run workflow"

Your digest will be available at `https://yourusername.github.io/twitter-digest/`

## Adjust Schedule

The workflow runs daily at 7:00 AM UTC by default. Edit `.github/workflows/twitter-digest.yml`:

```yaml
schedule:
  - cron: "0 7 * * *"  # 7:00 AM UTC daily
```

Use [crontab.guru](https://crontab.guru/) for custom schedules.

## Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY="your-api-key"

# Run
python -m twitter_digest.main

# Open the result
open docs/index.html
```

## Custom AI Prompt

Customize the Gemini prompt in `config/config.yaml`:

```yaml
gemini_prompt: |
  You are an expert analyst. For each Twitter account:
  1. Summarize the key points
  2. Explain any technical terms
  3. Provide relevant context
```

## Project Structure

```
twitter-digest/
├── .github/workflows/
│   └── twitter-digest.yml    # GitHub Actions workflow
├── config/
│   └── config.yaml           # Configuration
├── docs/                     # Generated site (GitHub Pages)
├── twitter_digest/
│   ├── main.py               # Entry point
│   ├── config_loader.py      # Config loading
│   ├── nitter_client.py      # RSS fetching
│   ├── gemini_client.py      # AI summarization
│   └── html_builder.py       # HTML generation
├── requirements.txt
└── README.md
```

## Troubleshooting

### No tweets found
- Nitter instances may be down. Add more to `config.yaml`
- Check if handles are valid and public

### Gemini API errors
- Verify your API key
- Check usage limits at [AI Studio](https://aistudio.google.com/)

### Pages not updating
- Check Actions tab for errors
- Ensure Pages is set to deploy from "GitHub Actions"

## License

MIT
