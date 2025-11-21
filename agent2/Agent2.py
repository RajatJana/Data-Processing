# agent2/Agent2.py
import google.generativeai as genai
from config import GEMINI_API_KEY
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class Agent2:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)

        safety = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json"
            },
            safety_settings=safety
        )