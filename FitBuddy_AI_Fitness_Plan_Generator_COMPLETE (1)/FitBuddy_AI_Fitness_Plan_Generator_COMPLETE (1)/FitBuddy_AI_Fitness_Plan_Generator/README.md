# FitBuddy – AI Fitness Plan Generator using Gemini Models

A FastAPI + Jinja2 + SQLite application that generates personalized 7-day workout plans and nutrition/recovery tips with Google Gemini. Users can submit feedback to regenerate a plan, while an admin page can view and delete stored users.

## Features
- User form: name, user ID, age, weight, goal, intensity
- AI-generated 7-day workout plan
- Nutrition/recovery tip
- Feedback-based plan update
- SQLite persistence using SQLAlchemy
- Admin view of users and original/updated plans
- FastAPI Swagger docs at `/docs`
- DEMO_MODE for testing the full project without an API key

## Project structure
```text
FitBuddy_AI_Fitness_Plan_Generator/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   └── all_users.html
│   └── static/
│       └── style.css
├── data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows setup
Open PowerShell in this project folder:

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open:
- Website: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin view: http://127.0.0.1:8000/view-all-users

## Gemini setup
1. Put your Gemini key in `.env`:
   `GOOGLE_API_KEY=...`
2. Set:
   `DEMO_MODE=false`
3. If a model is unavailable for your API key, change `GEMINI_WORKOUT_MODEL` and `GEMINI_TIP_MODEL` in `.env` to a currently available Gemini model.

The app uses the modern `google-genai` SDK and keeps the model names configurable.

## Demo mode
With `DEMO_MODE=true`, the project works without Gemini and returns deterministic sample plans/tips. This is useful for checking the complete application flow before connecting the API.

## Main routes
- `GET /`
- `POST /generate-workout`
- `POST /submit-feedback`
- `GET /view-all-users`
- `POST /delete-user/{user_id}`

## Safety note
This is an educational fitness-planning application. AI output is not a substitute for medical or professional fitness advice. Users should adjust activity to their abilities and seek professional guidance where appropriate.
