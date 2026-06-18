import os
import re
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

# Apidojo blocks queries with maxItems < 50 and returns {"noResults": true}
# We request 50 to bypass this, but our main.py will still only process the newest ones.
FETCH_LIMIT = 50

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_tweets(accounts: dict) -> list:
    all_tweets = []
    
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        raise ValueError("❌ CRITICAL ERROR: APIFY_API_TOKEN is missing from GitHub Secrets! You must add it in Settings -> Secrets -> Actions")

    print("[fetcher] 🚀 Starting Apify tweet-scraper for all accounts...")
    
    client = ApifyClient(apify_token)

    for username, prompt in accounts.items():
        print(f"[fetcher] Fetching @{username}...")
        
        # Prepare the Actor input for quacker/twitter-scraper
        run_input = {
            "handles": [username],
            "tweetsDesired": FETCH_LIMIT,
            "profilesDesired": 1
        }

        # Run the Actor and wait for it to finish
        run = client.actor("quacker/twitter-scraper").call(run_input=run_input)

        if isinstance(run, dict):
            dataset_id = run.get("defaultDatasetId")
        else:
            dataset_id = getattr(run, "defaultDatasetId", None) or getattr(run, "default_dataset_id", None)

        # Fetch results from the run's dataset
        tweets = []
        for item in client.dataset(dataset_id).iterate_items():
            text = clean_text(item.get("full_text", item.get("text", "")))
            
            if len(text) < 20:
                continue
            
            # Make sure it's from the actual user and not a retweet
            # quacker outputs author info under "user" object
            user_obj = item.get("user", {})
            if isinstance(user_obj, dict):
                author = user_obj.get("screen_name", user_obj.get("name", ""))
            else:
                author = item.get("author", item.get("username", ""))
                
            if username.lower() not in author.lower():
                continue

            tweets.append({
                "id": item.get("id_str", item.get("id", "unknown")),
                "author": username,
                "prompt": prompt,
                "text": text[:500],
                "likes": item.get("favorite_count", item.get("likeCount", 0)),
                "retweets": item.get("retweet_count", item.get("retweetCount", 0)),
                "engagement": 0,
                "url": item.get("url", f"https://x.com/{username}/status/{item.get('id_str', '')}")
            })

        print(f"[fetcher] 🎯 @{username}: {len(tweets)} tweets fetched")
        all_tweets.extend(tweets)

    print(f"\n[fetcher] Total: {len(all_tweets)} tweets fetched")
    return all_tweets
