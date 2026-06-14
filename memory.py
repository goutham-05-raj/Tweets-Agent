import json
import os

MEMORY_FILE = "seen_tweets.json"

def load_seen() -> set:
    """Load all previously seen tweet IDs."""
    if not os.path.exists(MEMORY_FILE):
        return set()
    with open(MEMORY_FILE) as f:
        data = json.load(f)
    return set(data)

def save_seen(seen: set):
    """Save seen tweet IDs back to file.
    Keeps only the last 5000 to avoid the file growing forever.
    """
    ids = list(seen)[-5000:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(ids, f)

def mark_seen(tweet_id: str, seen: set):
    """Add a tweet ID to the seen set."""
    seen.add(tweet_id)
