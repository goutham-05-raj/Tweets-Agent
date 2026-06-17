import os
import re
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

FETCH_LIMIT = 5

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_tweets(accounts: dict) -> list:
    all_tweets = []
    
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        print("[fetcher] ❌ WARNING: APIFY_API_TOKEN in .env is missing!")
        return []

    print("[fetcher] 🚀 Starting Apify tweet-scraper for all accounts...")
    
    client = ApifyClient(apify_token)

    for username, prompt in accounts.items():
        print(f"[fetcher] Fetching @{username}...")
        try:
            # Prepare the Actor input
            run_input = {
                "twitterHandles": [username],
                "maxItems": FETCH_LIMIT,
                "sort": "Latest"
            }

            # Run the Actor and wait for it to finish
            run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)

            # Fetch results from the run's dataset
            tweets = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                text = clean_text(item.get("text", ""))
                
                if len(text) < 20:
                    continue
                
                # Make sure it's from the actual user and not a retweet
                author = item.get("author", {}).get("userName", "")
                if username.lower() not in author.lower():
                    continue

                tweets.append({
                    "id": item.get("id", "unknown"),
                    "author": username,
                    "prompt": prompt,
                    "text": text[:500],
                    "likes": item.get("likeCount", 0),
                    "retweets": item.get("retweetCount", 0),
                    "engagement": 0,
                    "url": item.get("url", f"https://x.com/{username}")
                })

            print(f"[fetcher] 🎯 @{username}: {len(tweets)} tweets fetched")
            all_tweets.extend(tweets)

        except Exception as e:
            print(f"[fetcher] Error @{username}: {e}")

    print(f"\n[fetcher] Total: {len(all_tweets)} tweets fetched")
    return all_tweets
