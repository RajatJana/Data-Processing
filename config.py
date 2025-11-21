import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Fallback for demonstration if .env isn't set, though .env is preferred
    print("Warning: GEMINI_API_KEY not found in environment variables.")