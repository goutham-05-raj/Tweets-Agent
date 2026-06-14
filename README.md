# Autonomous AI Twitter Agency 🤖🐦

A fully autonomous, self-running AI Twitter Agent deployed on AWS. 

Unlike standard Twitter API bots that get banned instantly or have extreme rate limits, this agent uses a **headless robotic browser (Playwright)** to physically log into Twitter, navigate the timeline, click buttons, upload images, and type text exactly like a real human.

## Features ✨
- **Robotic Browser Automation**: Uses Playwright to natively interact with the Twitter UI, bypassing API bans.
- **Groq AI Integration**: Generates highly context-aware, deep, massive paragraph responses.
- **Multi-Account Personas**: Scans the timelines of different target accounts (like Elon Musk) and responds with specific, unique prompt personas.
- **Wikipedia Image Downloader**: Scrapes Wikipedia to find historical images related to trending topics and uploads them natively to Twitter threads.
- **Synchronized Threading**: Automatically replies to itself to build massive, multi-part viral threads.
- **Cloud Deployed**: Runs 24/7 on an AWS EC2 instance using a background `tmux` process.

## How it Works 🛠️
1. The script wakes up on a defined daily schedule using `schedule`.
2. It uses `fetcher.py` to read timelines without using official APIs.
3. It passes tweet text to `generator.py` to hit the Groq LLM API.
4. `poster.py` takes control of the browser, clicks the native Twitter UI elements, attaches any downloaded media, and posts the tweet.

*Note: All API keys and environment variables have been securely ignored.*
