import os
import json
from PIL import Image
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def analyze_image(image_path):

    image = Image.open(image_path)

    prompt = """
You are an expert civic infrastructure inspector.

Analyze the uploaded image carefully.

Return ONLY valid JSON.

{
  "category":"",
  "severity":"",
  "department":"",
  "confidence":"",
  "summary":"",
  "recommended_action":""
}

Rules:
- category should be one of:
Pothole,
Garbage,
Water Leakage,
Broken Streetlight,
Road Damage,
Drainage Issue,
Other

- severity should be:
Low
Medium
High

- confidence should be percentage.

Return ONLY JSON.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt, image]
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)