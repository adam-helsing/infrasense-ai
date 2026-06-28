import os
import io
import json
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
 
load_dotenv()
 
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
 
MODEL = "gemini-2.5-flash"
 
 
def analyze_image(image_path):
 
    pil_image = Image.open(image_path).convert("RGB")
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG")
    image = types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")
 
    prompt = """
You are InfraSense AI, an advanced AI system for smart city infrastructure inspection.
 
Your task is to inspect the uploaded image exactly like a professional municipal engineer.
 
Analyze ONLY what is visible in the image.
 
Return ONLY valid JSON.
 
Do NOT use markdown.
Do NOT explain anything.
Do NOT wrap the JSON.
 
JSON FORMAT
 
{
  "category":"",
  "severity":"",
  "department":"",
  "confidence":0,
  "summary":"",
  "recommended_action":""
}
 
VALID CATEGORIES
 
- Pothole
- Road Damage
- Garbage
- Water Leakage
- Drainage Issue
- Broken Streetlight
- Electrical Hazard
- Building Damage
- Traffic Sign Damage
- Public Safety Hazard
- Fallen Tree
- Road Obstruction
- Other
 
SEVERITY
 
High
Medium
Low
 
DEPARTMENT
 
Road Authority
Municipal Corporation
Water Department
Electricity Board
Public Works Department
Traffic Police
Disaster Management
 
CATEGORY MAPPING
 
Pothole -> Road Authority
Road Damage -> Road Authority
Garbage -> Municipal Corporation
Drainage Issue -> Municipal Corporation
Water Leakage -> Water Department
Broken Streetlight -> Electricity Board
Electrical Hazard -> Electricity Board
Building Damage -> Public Works Department
Traffic Sign Damage -> Traffic Police
Public Safety Hazard -> Municipal Corporation
Fallen Tree -> Disaster Management
Road Obstruction -> Municipal Corporation
Other -> Public Works Department
 
IMPORTANT RULES
 
1. Detect ONLY ONE primary issue.
2. Never invent objects that are not visible.
3. Confidence must be an integer between 80 and 99.
4. Summary must be less than 35 words.
5. Recommended action must be less than 20 words.
6. Prefer the MOST SPECIFIC category instead of Other.
7. If exposed wires, damaged electrical poles, hanging cables or broken electrical fixtures exist, classify as Electrical Hazard.
8. If cracks, broken walls, damaged public buildings or collapsing structures exist, classify as Building Damage.
9. If road is blocked by objects, classify as Road Obstruction.
10. If fallen branches or trees block roads, classify as Fallen Tree.
11. If no infrastructure issue is clearly visible, return category as Other.
 
Return ONLY JSON.
"""
 
    response = client.models.generate_content(
    model=MODEL,
    contents=[prompt,pil_image]
    )
 
    text = response.text or ""
 
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()
 
    try:
        return json.loads(text)
 
    except Exception:
        return {
            "category": "Other",
            "severity": "Low",
            "department": "Public Works Department",
            "confidence": 80,
            "summary": "Unable to analyze image.",
            "recommended_action": "Please upload a clearer image."
        }