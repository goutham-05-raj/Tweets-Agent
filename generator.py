import re
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, BRAND_VOICE, NICHE

client = Groq(api_key=GROQ_API_KEY)

VIRAL_QUOTE_PROMPT = """You are India's most notorious Twitter ghostwriter.
You write quotes that get talked about, screenshotted, and argued about for days.
You understand desi Twitter culture deeply — the humor, the drama, the trolling.

Niche: {niche}
Voice: {voice}

Original tweet by @{author}:
\"\"\"{text}\"\"\"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT INSTRUCTIONS FOR THIS SPECIFIC ACCOUNT:
{account_prompt}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ABSOLUTE RULES:
1. Write a substantial, deep, and detailed response. Do not write short 1-liners. Make it a full paragraph (up to Twitter Premium lengths if needed).
2. MATCH THE REQUIRED INSTRUCTIONS EXACTLY.
3. No hashtags unless specified. No boring corporate speak.
4. Sound like a real sharp human, not a bot.
5. Generate EXACTLY ONE perfect tweet.
6. DO NOT output any prefixes like "VERSION 1:" or "Tweet:". JUST output the raw text of the tweet itself.
"""

def extract_best(raw: str) -> str:
    # Aggressively strip any LLM prefixes
    clean = re.sub(r'(?i)^(VERSION \d:?\s*|\[BEST\]:?\s*|Tweet:?\s*|Quote:?\s*)', '', raw.strip())
    clean = clean.strip('"').strip("'")
    return clean

def generate_quote(tweet: dict) -> str | None:
    try:
        prompt = VIRAL_QUOTE_PROMPT.format(
            niche=NICHE,
            voice=BRAND_VOICE,
            author=tweet["author"],
            text=tweet["text"],
            account_prompt=tweet.get("prompt", "Write a viral, engaging quote tweet.")
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.8
        )
        raw = response.choices[0].message.content.strip()

        print(f"\n[generator] 🎯 Generating for @{tweet['author']}")
        
        best = extract_best(raw)
        
        print(f"✅ POSTING: {best}\n")
        return best

    except Exception as e:
        print(f"[generator] Error: {e}")
        return None
