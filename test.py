"""
Run this on GitHub Actions to diagnose exactly what's failing.
Add this file to your repo, then in tweet.yml change:
  run: python main.py
to:
  run: python test.py
Run once, see the diagnosis, then switch back to main.py
"""

import os
import httpx
import feedparser
import re

print("\n" + "="*55)
print("  FULL SYSTEM DIAGNOSIS")
print("="*55)

# ── TEST 1: Environment variables ─────────────────────────
print("\n[TEST 1] Checking secrets/env vars...")
keys = {
    "GROQ_API_KEY":    os.getenv("GROQ_API_KEY"),
    "X_API_KEY":       os.getenv("X_API_KEY"),
    "X_API_SECRET":    os.getenv("X_API_SECRET"),
    "X_ACCESS_TOKEN":  os.getenv("X_ACCESS_TOKEN"),
    "X_ACCESS_SECRET": os.getenv("X_ACCESS_SECRET"),
    "BRAND_VOICE":     os.getenv("BRAND_VOICE"),
    "NICHE":           os.getenv("NICHE"),
}
all_keys_ok = True
for k, v in keys.items():
    if v:
        print(f"  ✅ {k} = {v[:6]}...")
    else:
        print(f"  ❌ {k} = MISSING")
        all_keys_ok = False

# ── TEST 2: Nitter fetch ──────────────────────────────────
print("\n[TEST 2] Testing Nitter RSS fetch...")
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.adminforge.de",
    "https://nitter.perennialte.ch",
]
working_instance = None
for instance in NITTER_INSTANCES:
    try:
        r = httpx.get(f"{instance}/elonmusk/rss", timeout=8)
        if r.status_code == 200 and "<rss" in r.text:
            print(f"  ✅ Working instance: {instance}")
            working_instance = instance
            break
        else:
            print(f"  ❌ {instance} → HTTP {r.status_code}")
    except Exception as e:
        print(f"  ❌ {instance} → {e}")

if working_instance:
    feed = feedparser.parse(httpx.get(f"{working_instance}/elonmusk/rss", timeout=8).text)
    tweets_found = len(feed.entries)
    print(f"  ✅ Fetched {tweets_found} entries from @elonmusk")
    if tweets_found > 0:
        sample = feed.entries[0]
        text = re.sub(r'<[^>]+>', '', sample.get("summary", "")).strip()
        print(f"  ✅ Sample tweet: {text[:100]}...")
else:
    print("  ❌ NO working Nitter instance found!")

# ── TEST 3: Groq API ──────────────────────────────────────
print("\n[TEST 3] Testing Groq API...")
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'GROQ WORKS' and nothing else."}],
        max_tokens=10
    )
    result = response.choices[0].message.content.strip()
    print(f"  ✅ Groq response: {result}")
except Exception as e:
    print(f"  ❌ Groq failed: {e}")

# ── TEST 4: X API posting ─────────────────────────────────
print("\n[TEST 4] Testing X API posting...")
try:
    import tweepy
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET")
    )
    # Post a real test tweet
    response = client.create_tweet(text="🤖 Agent test tweet — system is live and working! #AI")
    tweet_id = response.data["id"]
    print(f"  ✅ TEST TWEET POSTED: https://twitter.com/i/web/status/{tweet_id}")
except tweepy.TweepyException as e:
    print(f"  ❌ X API posting failed: {e}")
    print("  👉 Fix: Go to developer.twitter.com → your app → Settings → App permissions → change to Read AND Write")
except Exception as e:
    print(f"  ❌ Unexpected error: {e}")

print("\n" + "="*55)
print("  DIAGNOSIS COMPLETE")
print("="*55 + "\n")
