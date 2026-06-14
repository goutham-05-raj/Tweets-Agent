import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

actors = [
    "epctex/twitter-scraper",
    "curious_coder/twitter-scraper",
    "apidojo/tweet-scraper-lite",
    "microworlds/x-scraper",
    "lucas/twitter-scraper",
    "heavies/twitter-scraper",
    "apify/twitter-scraper-lite"
]

print("Hunting for a free Apify scraper that actually returns tweets...")

for actor in actors:
    try:
        print(f"Trying {actor}...")
        run = client.actor(actor).call(run_input={"searchTerms": ["hello"], "maxItems": 1, "tweetsDesired": 1})
        status = run.get("status") if isinstance(run, dict) else run.status
        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id
        
        # Check if it actually scraped something
        items = list(client.dataset(dataset_id).iterate_items())
        
        if status == "SUCCEEDED" and len(items) > 0:
            print(f"✅ REAL SUCCESS: {actor} fetched {len(items)} tweets!")
            break
        else:
            print(f"❌ Failed or returned empty. (Status: {status}, Items: {len(items)})")
    except Exception as e:
        print(f"❌ Blocked or broken.")
