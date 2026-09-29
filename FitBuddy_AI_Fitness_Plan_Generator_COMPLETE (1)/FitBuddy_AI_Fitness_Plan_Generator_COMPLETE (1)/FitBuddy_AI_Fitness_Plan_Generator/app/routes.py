from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Plan
from .schemas import UserInput, FeedbackRequest
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# =========================================================
# HOME
# =========================================================

@router.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# GENERATE WORKOUT
# =========================================================

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):

    try:

        # Create user input object
        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        # Generate workout
        workout = generate_workout_gemini(
            data.name,
            data.age,
            data.weight,
            data.goal,
            data.intensity
        )

        # Generate nutrition tip
        tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        # Find existing user
        user = (
            db.query(User)
            .filter(User.user_id == data.user_id)
            .first()
        )

        # Create new user
        if not user:

            user = User(
                **data.model_dump()
            )

            db.add(user)
            db.flush()

        # Update existing user
        else:

            for key, value in data.model_dump().items():
                setattr(user, key, value)

        # Create workout plan
        plan = Plan(
            user_id=data.user_id,
            original_plan=workout,
            nutrition_tip=tip
        )

        db.add(plan)

        db.commit()

        db.refresh(plan)

        # Show result page
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": data.model_dump(),
                "workout_plan": workout,
                "nutrition_tip": tip,
                "message": None,
                "plan_id": plan.id,
                "updated_plan": None
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=500
        )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):

    try:

        # Validate feedback
        request_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )

        # Find latest workout plan
        plan = (
            db.query(Plan)
            .filter(
                Plan.user_id == request_data.user_id
            )
            .order_by(
                Plan.id.desc()
            )
            .first()
        )

        # Find user
        user = (
            db.query(User)
            .filter(
                User.user_id == request_data.user_id
            )
            .first()
        )

        # User or plan not found
        if not plan or not user:

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "User or workout plan not found."
                },
                status_code=404
            )

        # Generate updated plan
        updated = update_workout_plan(
            plan.original_plan,
            request_data.feedback
        )

        # Save feedback
        plan.updated_plan = updated
        plan.feedback = request_data.feedback
        plan.updated_at = datetime.utcnow()

        db.commit()

        # Show updated result
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,

                "user": {
                    "user_id": user.user_id,
                    "name": user.name,
                    "age": user.age,
                    "weight": user.weight,
                    "goal": user.goal,
                    "intensity": user.intensity
                },

                "workout_plan": plan.original_plan,

                "updated_plan": updated,

                "nutrition_tip": plan.nutrition_tip,

                "message": (
                    "Plan updated successfully "
                    "using your feedback."
                ),

                "plan_id": plan.id
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=500
        )


# =========================================================
# VIEW ALL USERS
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.id.desc())
        .all()
    )

    plans = {}

    for user in users:

        plans[user.user_id] = (
            db.query(Plan)
            .filter(
                Plan.user_id == user.user_id
            )
            .order_by(
                Plan.id.desc()
            )
            .all()
        )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "plans": plans
        }
    )


# =========================================================
# DELETE USER
# =========================================================

@router.post("/delete-user/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    # Delete user's plans
    db.query(Plan).filter(
        Plan.user_id == user_id
    ).delete()

    # Delete user
    db.query(User).filter(
        User.user_id == user_id
    ).delete()

    db.commit()

    # Go back to users page
    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )