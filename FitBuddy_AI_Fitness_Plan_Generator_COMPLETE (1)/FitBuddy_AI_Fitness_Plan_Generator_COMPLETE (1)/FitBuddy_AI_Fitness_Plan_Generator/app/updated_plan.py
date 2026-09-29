import os
from dotenv import load_dotenv

load_dotenv()

def _demo_update(original_plan, feedback):
    return original_plan + f"\n\n--- UPDATED FROM FEEDBACK ---\nRequested feedback: {feedback}\nAdjustment: Keep the same weekly structure while applying the requested preference safely; reduce or add volume gradually as appropriate."

def update_workout_plan(original_plan, feedback):
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        return _demo_update(original_plan, feedback)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to .env or enable DEMO_MODE.")

    from google import genai
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
    prompt = f"""
Update the following 7-day fitness plan based on the user's feedback.
Preserve a clear 7-day structure, include recovery, and make only reasonable
changes. Do not make medical claims.

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}
"""
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
