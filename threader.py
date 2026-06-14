import json
import random
import os
import urllib.request
import urllib.parse
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

THREAD_PROMPT = """You are a Twitter expert with 15 years of experience in viral documentary content.

Create a Twitter thread on a fascinating, true, real-world documentary topic from India or the USA.
It must be a real story (geopolitics, crime, untold history, massive corporate failures, etc).
Do NOT write about movies. Write about REAL events.

Follow these exact rules:

TONE:
- Neutral & Analytical
- No sides taken
- Poetic/Emotional where needed

STRUCTURE:
Tweet 1 (Hook): Start with shocking fact, create curiosity instantly, at least 4 lines long, end with 🧵
Tweet 2-8 (Build & Reveal): EACH tweet must be detailed and AT LEAST 4 full lines of text. Do NOT write tiny one-line tweets. Go deep into the narrative, the twists, and the universal lessons. Provide rich context.
Last Tweet (CTA): Neutral closing thought, subtle RT request, at least 4 lines long.

STRICT TWEET RULES:
✅ Max 2-3 hashtags only
✅ EVERY single tweet MUST contain at least one relevant emoji 🚨
✅ EVERY single tweet MUST be at least 4 lines long (about 200-250 characters each). No tiny one-liners!

OUTPUT FORMAT:
You MUST output EXACTLY a valid JSON array of objects. Do NOT wrap it in markdown. Do not add any text before or after the JSON.
Each object represents one tweet.
If a tweet needs an image (especially Tweet 1 and 6), provide a `wikipedia_search_term` which is the exact title of a Wikipedia article that has a real photo of the event/person (e.g., "Taj_Mahal", "Bhopal_disaster", "Apollo_11"). Otherwise, leave it empty.
[
  {
    "text": "Text of the tweet",
    "wikipedia_search_term": "Exact_Wikipedia_Article_Title"
  }
]
"""

def fetch_wikipedia_image(title: str) -> str:
    if not title: return None
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1000"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "thumbnail" in page_data:
                    img_url = page_data["thumbnail"]["source"]
                    # Download image with proper User-Agent to bypass Wikipedia's 403 block
                    filename = f"temp_img_{random.randint(1000,9999)}.jpg"
                    req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req_img) as response, open(filename, 'wb') as out_file:
                        out_file.write(response.read())
                    return filename
    except Exception as e:
        print(f"[threader] Failed to fetch Wikipedia image for {title}: {e}")
    return None

def generate_thread() -> list:
    print("\n[threader] 🧵 Generating trending documentary thread...")
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": THREAD_PROMPT}],
                max_tokens=2000,
                temperature=0.7
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            
            thread_data = json.loads(raw)
            
            print(f"[threader] ✅ Successfully generated {len(thread_data)}-tweet thread.")
            for i, t in enumerate(thread_data, 1):
                wiki_term = t.get("wikipedia_search_term", "")
                img_path = fetch_wikipedia_image(wiki_term)
                t["image_path"] = img_path
                
                print(f"--- TWEET {i} ---")
                print(t["text"])
                if img_path:
                    print(f"[IMAGE ATTACHED: {img_path} from Wikipedia: {wiki_term}]")
                print()
                
            return thread_data

        except json.JSONDecodeError as e:
            print(f"[threader] Warning: LLM returned invalid JSON (attempt {attempt+1}/3). Retrying...")
        except Exception as e:
            print(f"[threader] Error generating thread: {e}")
            return []
            
    print("[threader] ❌ Failed to generate valid thread after 3 attempts.")
    return []

if __name__ == "__main__":
    import poster
    print("Testing full thread generation AND posting...")
    thread_data = generate_thread()
    if thread_data:
        poster.post_thread(thread_data)
