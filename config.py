import os
import json
from dotenv import load_dotenv

load_dotenv()

# Groq (free LLM)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

# X API keys (for posting)
X_API_KEY       = os.getenv("X_API_KEY")
X_API_SECRET    = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN  = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# Voice and niche
BRAND_VOICE = os.getenv("BRAND_VOICE", "bold, direct, no fluff, slightly savage")
NICHE       = os.getenv("NICHE", "AI automation and making money online")

# Agent settings
SCORE_THRESHOLD  = 3.0   # minimum score to generate a quote
MAX_POSTS_PER_RUN = 5    # max quotes posted per run
