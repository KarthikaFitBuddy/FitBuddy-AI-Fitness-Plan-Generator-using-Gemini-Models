import os
from dotenv import load_dotenv

load_dotenv()

def generate_nutrition_tip_with_flash(goal):
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        tips = {
            "muscle gain": "Include a protein-rich food in each main meal and stay hydrated.",
            "weight loss": "Prioritize vegetables, adequate protein, whole foods, and water while keeping portions appropriate.",
            "general wellness": "Build meals around vegetables or fruit, protein, whole grains, and adequate hydration.",
        }
        return tips.get(goal.lower(), "Stay hydrated and build balanced meals with protein, vegetables, and whole foods.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to .env or enable DEMO_MODE.")

    from google import genai
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash")
    prompt = f"Give one concise, practical nutrition or recovery tip for the fitness goal: {goal}. Avoid medical claims."
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
