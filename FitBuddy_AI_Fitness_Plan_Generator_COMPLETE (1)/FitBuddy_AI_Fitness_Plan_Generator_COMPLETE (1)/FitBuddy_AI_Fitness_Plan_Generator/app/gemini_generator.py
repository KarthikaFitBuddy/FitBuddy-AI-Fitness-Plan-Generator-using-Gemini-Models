import os
from dotenv import load_dotenv

load_dotenv()

def _demo_plan(name, goal, intensity):
    return f"""7-DAY FITBUDDY WORKOUT PLAN
Name: {name}
Goal: {goal}
Intensity: {intensity.title()}

DAY 1 - FULL BODY
Warm-up: 5-10 minutes brisk walking and mobility
Main workout: Squats 3x10, Push-ups 3x8-12, Glute bridges 3x12
Cooldown: 5 minutes gentle stretching

DAY 2 - CARDIO + CORE
Warm-up: 5-10 minutes easy movement
Main workout: 20-30 minutes moderate cardio, Plank 3x20-40 sec, Dead bug 3x10
Cooldown: Easy walking and stretching

DAY 3 - UPPER BODY
Warm-up: Shoulder circles and light movement
Main workout: Incline push-ups 3x10, Rows 3x10, Shoulder raises 3x12
Cooldown: Upper-body stretches

DAY 4 - RECOVERY
Easy walk 20-30 minutes plus gentle mobility

DAY 5 - LOWER BODY
Warm-up: 5-10 minutes
Main workout: Squats 3x10, Reverse lunges 3x8 each side, Calf raises 3x15
Cooldown: Lower-body stretching

DAY 6 - CARDIO + CORE
Warm-up: 5-10 minutes
Main workout: 20-30 minutes cardio, Side plank 3x20 sec each side, Bird dog 3x10
Cooldown: Gentle stretching

DAY 7 - REST / ACTIVE RECOVERY
Easy walk and mobility as comfortable.

GENERAL: Adjust volume to your experience and stop if an exercise causes pain."""

def generate_workout_gemini(name, age, weight, goal, intensity):
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        return _demo_plan(name, goal, intensity)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to .env or enable DEMO_MODE.")

    from google import genai
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")

    prompt = f"""
Create a safe, structured 7-day beginner-to-intermediate fitness plan.
User: {name}; age: {age}; weight: {weight} kg; goal: {goal}; intensity: {intensity}.
For every day include warm-up, main workout with exercises/sets/reps or duration,
and cooldown/recovery. Include at least one recovery/rest day. Keep the response
clear and day-by-day. Do not claim to diagnose or treat medical conditions.
"""
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
