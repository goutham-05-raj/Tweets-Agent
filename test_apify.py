import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

actors_to_test = [
    "quacker/twitter-scraper",
    "shanes/tweet-scraper",
    "gentle_cloud/twitter-tweets-scraper",
    "curious_coder/twitter-scraper",
    "apify/twitter-scraper-lite",
    "epctex/twitter-scraper"
]

for actor in actors_to_test:
    print(f"Testing {actor}...")
    try:
        run = client.actor(actor).call(run_input={"searchTerms": ["hello"], "maxItems": 1})
        print(f"{actor} SUCCEEDED. Status: {run.get('status')}")
    except Exception as e:
        print(f"{actor} FAILED: {e}")
