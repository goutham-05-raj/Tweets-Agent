import time
import re
import os
from dotenv import load_dotenv

load_dotenv()

FETCH_LIMIT = 5

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_user_tweets(username: str, prompt: str) -> list:
    from playwright.sync_api import sync_playwright
    tweets = []
    
    auth_token = os.getenv("TWITTER_AUTH_TOKEN")
    if not auth_token or "ENCRYPTED_VALUE" in auth_token:
        print("[fetcher] ❌ WARNING: TWITTER_AUTH_TOKEN in .env is missing or encrypted!")
        return []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            
            context.add_cookies([{
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/",
                "secure": True,
                "httpOnly": True
            }])
            
            page = context.new_page()
            page.goto(f"https://x.com/{username}", wait_until="domcontentloaded")
            
            try:
                page.wait_for_selector('[data-testid="tweet"]', timeout=15000)
            except:
                print(f"[fetcher] Timeout or no tweets found for @{username}")
                browser.close()
                return []
                
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            
            articles = page.query_selector_all('[data-testid="tweet"]')
            
            for article in articles:
                text_el = article.query_selector('[data-testid="tweetText"]')
                text = clean_text(text_el.inner_text()) if text_el else ""
                
                if len(text) < 20:
                    continue
                    
                user_info = article.query_selector('[data-testid="User-Name"]')
                if user_info and username.lower() not in user_info.inner_text().lower():
                     continue 

                tweet_id = "unknown"
                url_el = article.query_selector('a[href*="/status/"]')
                if url_el:
                    href = url_el.get_attribute('href')
                    if href:
                        tweet_id = href.split('/')[-1]

                tweets.append({
                    "id":         tweet_id, 
                    "author":     username,
                    "prompt":     prompt,
                    "text":       text[:500],
                    "likes":      0,
                    "retweets":   0,
                    "engagement": 0,
                    "url":        f"https://x.com{href}" if url_el else f"https://x.com/{username}"
                })
                
                if len(tweets) >= FETCH_LIMIT:
                    break
                    
            browser.close()
    except Exception as e:
        print(f"[fetcher] Error @{username}: {e}")

    return tweets

import random

def fetch_tweets(accounts: dict) -> list:
    all_tweets = []

    for username, prompt in accounts.items():
        tweets = fetch_user_tweets(username, prompt)
        print(f"[fetcher] 🎯 @{username}: {len(tweets)} tweets fetched")
        all_tweets.extend(tweets)
        # Random delay between accounts to prevent IP bans
        delay = random.randint(5, 12)
        print(f"[fetcher] Sleeping {delay}s...")
        time.sleep(delay)

    print(f"\n[fetcher] Total: {len(all_tweets)} tweets fetched")
    return all_tweets
