# Twitter Quote Tweet Agent

Monitors 20 Twitter accounts, scores their tweets with AI, and posts quality quote tweets automatically. 100% free.

## Stack
- **twikit** — scrapes tweets (no API key needed)
- **Groq** — free LLM for scoring + writing (Llama 3.3 70B)
- **tweepy** — posts via X free API tier
- **GitHub Actions** — free 24/7 scheduler

## Setup (one time)

### Step 1 — Get your API keys

**Groq (free)**
1. Go to https://console.groq.com
2. Sign up → API Keys → Create key
3. Copy it

**X API (free)**
1. Go to https://developer.twitter.com
2. Sign in → Create a project + app
3. Go to your app → Keys and Tokens
4. Generate: API Key, API Secret, Access Token, Access Token Secret
5. Make sure your app has Read + Write permissions

### Step 2 — Set up the repo

1. Fork or create a new GitHub repo
2. Upload all these files to it
3. Go to repo Settings → Secrets and variables → Actions
4. Add these secrets one by one:
   - TWITTER_USERNAME
   - TWITTER_EMAIL
   - TWITTER_PASSWORD
   - GROQ_API_KEY
   - X_API_KEY
   - X_API_SECRET
   - X_ACCESS_TOKEN
   - X_ACCESS_SECRET
   - BRAND_VOICE  (e.g. "bold, direct, no fluff")
   - NICHE        (e.g. "AI automation and making money online")

### Step 3 — Edit your accounts

Open accounts.json and replace the 20 usernames with the accounts you want to monitor.

### Step 4 — Test locally first

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your real keys in .env
python main.py
```

### Step 5 — Go live

Push everything to GitHub. The Actions workflow runs automatically every 4 hours.
You can also trigger it manually: GitHub repo → Actions tab → Quote Tweet Agent → Run workflow.

## File structure

```
twitter-agent/
├── main.py          # Orchestrator — runs the full pipeline
├── fetcher.py       # Scrapes tweets from 20 accounts via twikit
├── analyzer.py      # Scores tweets using Groq LLM
├── generator.py     # Picks strategy + writes quote tweet
├── poster.py        # Posts to X via tweepy
├── memory.py        # Tracks seen tweet IDs in seen_tweets.json
├── config.py        # All settings in one place
├── accounts.json    # List of 20 Twitter usernames to monitor
├── seen_tweets.json # Auto-updated — do not edit manually
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── tweet.yml  # GitHub Actions cron config
```

## Tuning

- Change `SCORE_THRESHOLD` in config.py to post more (lower) or fewer (higher) quotes
- Change `MAX_POSTS_PER_RUN` to control how many tweets per 4-hour window
- Edit the prompts in analyzer.py and generator.py to match your niche/voice
