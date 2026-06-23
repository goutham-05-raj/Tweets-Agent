import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

def post_quote_tweet(quote_text: str, original_tweet_id: str, author: str = "x") -> bool:
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        raise ValueError("❌ CRITICAL ERROR: APIFY_API_TOKEN is missing from GitHub Secrets! You must add it in Settings -> Secrets -> Actions")
        
    auth_token = os.getenv("TWITTER_AUTH_TOKEN")
    
    if not auth_token:
        print("[poster] ❌ WARNING: TWITTER_AUTH_TOKEN is missing!")
        return False
        
    if original_tweet_id == "unknown":
        print("[poster] ❌ Cannot quote tweet an unknown ID. Skipping.")
        return False
        
    client = ApifyClient(apify_token)
    
    # Twitter natively creates a quote tweet if you just paste the URL of the tweet at the end
    tweet_url = f"https://x.com/{author}/status/{original_tweet_id}"
    full_text = f"{quote_text}\n\n{tweet_url}"
    
    print(f"[poster] ⏳ Sending tweet to Apify Actor for posting...")
    
    run_input = {
        "tweetText": full_text,
        "postingMethod": "browser",
        "twitterAuthToken": auth_token
    }
    
    # Run the Actor and wait for it to finish
    run = client.actor("pixelated_pulse/twitter-poster").call(run_input=run_input)
    
    if isinstance(run, dict):
        status = run.get("status")
    else:
        status = getattr(run, "status", None)
        
    if run and status == "SUCCEEDED":
        print("[poster] ✅ Apify successfully posted the quote tweet!")
        return True
    
    print(f"[poster] ❌ Run failed or timed out: {status}")
    return False
