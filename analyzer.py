import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, NICHE, SCORE_THRESHOLD

client = Groq(api_key=GROQ_API_KEY)

CATEGORY_CONTEXT = {
    "roast": "This is a ROAST TARGET. Find hypocrisy, irony, absurdity. Score sarcasm and spice VERY HIGH.",
    "spicy": "This gets SPICY treatment. Find the most controversial, divisive angle. Score spice HIGH.",
    "support": "This gets FULL SUPPORT. Find the best angle to validate and amplify powerfully.",
    "boost": "This is a BOOST target. Find the most insightful angle to expand on brilliantly."
}

PROMPT = """You are a ruthlessly sharp Indian social media analyst who understands Twitter/X culture deeply.

Niche: {niche}
Category: {category}
Instructions: {category_context}

Tweet by @{author} ({likes} likes, {retweets} retweets):
\"\"\"{text}\"\"\"

Score each dimension 1-10 and respond ONLY with valid JSON, no markdown, no extra text:
{{
  "virality": <1-10>,
  "debate": <1-10>,
  "emotion": <1-10>,
  "sarcasm_opportunity": <1-10>,
  "spice_level": <1-10>,
  "tweet_environment": "<SERIOUS|HUMBLE_BRAG|CONTROVERSIAL|MOTIVATIONAL|CRINGE|FACTUAL|EMOTIONAL|SELF_PROMO|BASED|OVERCONFIDENT|HYPOCRITICAL>",
  "quote_opportunity": <1-10>,
  "hook_potential": <1-10>,
  "audience_magnet": <1-10>,
  "timing": <1-10>,
  "overall": <average of all above, 1 decimal>,
  "viral_angle": "<single best angle for max reach>",
  "tone_recommendation": "<savage|sarcastic|spicy|witty|supportive|expansive>",
  "why_viral": "<one sentence why this will blow up>",
  "sarcasm_hint": "<roast angle if applicable, else none>",
  "troll_angle": "<specific irony to exploit for roast category, else none>",
  "red_flags": "<reason this could backfire, or none>"
}}"""

def deep_analyze_tweet(tweet: dict) -> dict:
    category = tweet.get("category", "boost")
    try:
        prompt = PROMPT.format(
            niche=NICHE,
            category=category.upper(),
            category_context=CATEGORY_CONTEXT.get(category, ""),
            author=tweet["author"],
            text=tweet["text"],
            likes=tweet["likes"],
            retweets=tweet["retweets"]
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        scores = json.loads(raw)

        tweet["scores"]              = scores
        tweet["overall_score"]       = float(scores.get("overall", 0))
        tweet["viral_angle"]         = scores.get("viral_angle", "")
        tweet["tone_recommendation"] = scores.get("tone_recommendation", "bold")
        tweet["tweet_environment"]   = scores.get("tweet_environment", "SERIOUS")
        tweet["sarcasm_opportunity"] = float(scores.get("sarcasm_opportunity", 0))
        tweet["spice_level"]         = float(scores.get("spice_level", 5))
        tweet["sarcasm_hint"]        = scores.get("sarcasm_hint", "none")
        tweet["troll_angle"]         = scores.get("troll_angle", "none")
        tweet["why_viral"]           = scores.get("why_viral", "")
        tweet["red_flags"]           = scores.get("red_flags", "none")

        emoji = {"roast":"🔥","spicy":"🌶️","support":"💪","boost":"🚀"}.get(category,"")
        print(f"\n[analyzer] {emoji} @{tweet['author']} [{category.upper()}] | Score: {tweet['overall_score']}/10")
        print(f"           Tone: {tweet['tone_recommendation']} | Spice: {tweet['spice_level']}/10")
        print(f"           Why viral: {tweet['why_viral']}")
        if tweet["red_flags"] != "none":
            print(f"           ⚠️ Red flag: {tweet['red_flags']}")

    except Exception as e:
        print(f"[analyzer] Error on @{tweet['author']}: {e}")
        tweet["overall_score"] = 0

    return tweet

def filter_and_score(tweets: list) -> list:
    print(f"\n[analyzer] Analyzing {len(tweets)} tweets...")
    scored = [deep_analyze_tweet(t) for t in tweets]
    clean = [
        t for t in scored
        if t["overall_score"] >= SCORE_THRESHOLD
        and t.get("red_flags", "none").lower() == "none"
    ]
    clean.sort(key=lambda t: t["overall_score"], reverse=True)
    print(f"\n[analyzer] {len(clean)}/{len(tweets)} passed ✓")
    return clean
