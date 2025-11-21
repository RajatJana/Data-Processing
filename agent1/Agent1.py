# agent1/Agent1.py
import google.generativeai as genai
from config import GEMINI_API_KEY
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class Agent1:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json"  # ← FORCED JSON = NO MORE MALFORMED CALLS
            },
            safety_settings=safety_settings
        )