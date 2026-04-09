from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Request, Depends
from services.auth import require_auth
from fastapi.templating import Jinja2Templates

from services.dynamodb_service import get_all_jobs

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BRUSSELS_TZ = ZoneInfo("Europe/Brussels")


def format_date(date_str):
    """Convert ISO datetime string to date-only format"""
    if not date_str:
        return ""
    try:
        # Parse the datetime string
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Return only the date part
        return dt.strftime("%d-%m-%Y")
    except:
        return date_str


@router.get("/", dependencies=[Depends(require_auth)])
async def dashboard(request: Request):
    jobs = get_all_jobs()
    now = datetime.now(BRUSSELS_TZ)

    # Format dates and categorize
    for job in jobs:
        if job.get("next_followup_at"):
            followup_dt = None
            try:
                # Try ISO format first (with or without timezone)
                followup_dt = datetime.fromisoformat(job["next_followup_at"].replace('Z', '+00:00'))
            except Exception:
                # Fallback: try YYYY-MM-DD format
                try:
                    # Parse as date-only and add Brussels timezone at midnight
                    followup_dt = datetime.strptime(job["next_followup_at"], '%Y-%m-%d')
                    followup_dt = followup_dt.replace(tzinfo=BRUSSELS_TZ)
                except Exception:
                    # Fallback: try DD-MM-YYYY format
                    try:
                        followup_dt = datetime.strptime(job["next_followup_at"], '%d-%m-%Y')
                        followup_dt = followup_dt.replace(tzinfo=BRUSSELS_TZ)
                    except Exception:
                        # Could not parse, skip this job
                        job["next_followup_at_formatted"] = job["next_followup_at"]
                        job["is_overdue"] = False
                        continue

            # Format the date and check if overdue
            job["next_followup_at_formatted"] = followup_dt.strftime("%d-%m-%Y")
            job["is_overdue"] = followup_dt < now

    overdue = [job for job in jobs if
               job.get("is_overdue") and job.get("status") in ["new", "applied", "interviewing"]]
    due_soon = [job for job in jobs if
                job.get("next_followup_at") and not job.get("is_overdue") and job.get("status") in
                ["new", "applied", "interviewing"]]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "jobs": jobs,
            "overdue": overdue,
            "due_soon": due_soon,
        },
    )
