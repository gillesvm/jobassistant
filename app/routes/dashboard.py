from datetime import date
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from services.mock_data import get_all_jobs

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def dashboard(request: Request):
    jobs = get_all_jobs()
    today = str(date.today())

    overdue = [
        job for job in jobs
        if job.get("next_followup_at") and job["next_followup_at"] < today
    ]

    due_soon = [
        job for job in jobs
        if job.get("next_followup_at") and job["next_followup_at"] >= today
    ]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "jobs": jobs,
            "overdue": overdue,
            "due_soon": due_soon,
        },
    )
