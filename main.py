import json
import random
import time
from fetcher   import fetch_tweets
from generator import generate_quote
from poster    import post_quote_tweet
from memory    import load_seen, save_seen, mark_seen
from config    import MAX_POSTS_PER_RUN

def load_accounts() -> dict:
    with open("accounts.json") as f:
        return json.load(f)

def run():
    print("=" * 55)
    print("  Twitter Quote Agent — CUSTOM ACCOUNT MODE")
    print("=" * 55)

    # 1. Load custom accounts
    accounts = load_accounts()
    print(f"[main] Monitoring {len(accounts)} highly-specialized accounts.")

    # 2. Load memory
    seen = load_seen()
    print(f"[main] Memory: {len(seen)} tweets already seen")

    # 3. Fetch latest tweets
    tweets = fetch_tweets(accounts)
    if not tweets:
        print("[main] No tweets fetched. Exiting.")
        return

    # 4. Filter already-seen tweets
    new_tweets = [t for t in tweets if t["id"] not in seen]
    print(f"[main] New unseen tweets: {len(new_tweets)}")
    if not new_tweets:
        print("[main] Nothing new to process. Exiting.")
        save_seen(seen)
        return

    # Mark all as seen immediately so we don't process them again next run
    for t in new_tweets:
        mark_seen(t["id"], seen)

    # 5. Group by author and pick exactly 2 per account
    from collections import defaultdict
    tweets_by_author = defaultdict(list)
    for t in new_tweets:
        tweets_by_author[t["author"]].append(t)
        
    final_candidates = []
    for author, author_tweets in tweets_by_author.items():
        # take up to 2 tweets for this specific account
        final_candidates.extend(author_tweets[:2])

    # Shuffle the final list so we don't post back-to-back for the same account
    random.shuffle(final_candidates)

    print(f"[main] Target for this run: {len(final_candidates)} highly-curated quote tweets.")

    # 6. Generate and post
    posted = 0
    for tweet in final_candidates:
        print(f"\n[main] 🎯 Generating quote for @{tweet['author']}")

        quote = generate_quote(tweet)
        if not quote:
            print("[main] Generation failed, skipping.")
            continue

        # MASSIVE anti-spam delay: 2 to 4 minutes between posts! 
        # This makes 16 tweets take about 45 minutes to post, making it look 100% human.
        delay = random.randint(120, 240)
        print(f"[main] Sleeping {delay}s to mimic human typing and avoid spam filters...")
        time.sleep(delay)

        success = post_quote_tweet(quote, tweet["id"], tweet["author"])
        if success:
            posted += 1
            print(f"[main] ✅ Posted {posted}/{len(final_candidates)}")

    # 7. Save memory
    save_seen(seen)
    print(f"\n[main] Done. {posted} quote tweet(s) posted this run.")
    print("=" * 55)

if __name__ == "__main__":
    run()
