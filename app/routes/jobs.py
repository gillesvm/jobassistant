from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from services.auth import require_auth

from services.dynamodb_service import add_job, get_all_jobs, get_job, update_job

router = APIRouter(dependencies=[Depends(require_auth)])
templates = Jinja2Templates(directory="templates")


@router.get("/jobs")
def jobs_list(request: Request, status: str = None):
    from datetime import datetime

    jobs = get_all_jobs()

    # Format dates
    for job in jobs:
        if job.get("next_followup_at"):
            try:
                dt = datetime.fromisoformat(job["next_followup_at"].replace('Z', '+00:00'))
                job["next_followup_at_formatted"] = dt.strftime("%d-%m-%Y")
            except:
                job["next_followup_at_formatted"] = job["next_followup_at"]

    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job.get('status') == status]

    # Get unique statuses for filter dropdown
    all_statuses = sorted(set(job.get('status', '') for job in get_all_jobs() if job.get('status')))

    return templates.TemplateResponse(
        request,
        "jobs_list.html",
        {
            "jobs": jobs,
            "all_statuses": all_statuses,
            "selected_status": status
        },
    )


@router.get("/jobs/new")
def new_job_form(request: Request):
    return templates.TemplateResponse(
        request,
        "job_form.html",
        {},
    )


@router.post("/jobs/new")
def create_job(
    request: Request,
    company: str = Form(...),
    title: str = Form(...),
    job_url: str = Form(...),
    status: str = Form(...),
    job_description: str = Form(""),
    resume_used: str = Form(""),
    cover_letter: str = Form("")
):
    job_id = add_job(
        company=company,
        title=title,
        job_url=job_url,
        status=status,
        job_description=job_description,
        resume_used=resume_used,
        cover_letter=cover_letter
    )
    return RedirectResponse(url="/jobs", status_code=303)


@router.get("/jobs/{job_id}/edit")
def edit_job_form(request: Request, job_id: str):
    from datetime import datetime

    items = get_job(job_id)
    if not items:
        raise HTTPException(status_code=404, detail="Job not found")

    # Combine all items for this job into a single dict
    job_data = {}

    # First, get the JOB item
    for item in items:
        if item['item_type'] == 'JOB':
            job_data = dict(item)  # Start with JOB data
            break

    # Then add the text fields
    for item in items:
        if item['item_type'] == 'DESCRIPTION':
            job_data['job_description'] = item.get('content', '')
        elif item['item_type'] == 'RESUME':
            job_data['resume_used'] = item.get('content', '')
        elif item['item_type'] == 'COVER_LETTER':
            job_data['cover_letter'] = item.get('content', '')
        elif item['item_type'] == 'FEEDBACK':
            job_data['feedback'] = item.get('content', '')

    # Format dates for display
    job_data['created_at_date'] = ''
    job_data['next_followup_at_date'] = ''
    job_data['updated_at_formatted'] = ''

    if job_data.get('created_at'):
        try:
            # Try ISO format first (with or without timezone)
            dt = datetime.fromisoformat(job_data['created_at'].replace('Z', '+00:00'))
            job_data['created_at_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            # Fallback: try YYYY-MM-DD format
            try:
                dt = datetime.strptime(job_data['created_at'], '%Y-%m-%d')
                job_data['created_at_date'] = dt.strftime('%Y-%m-%d')
            except Exception:
                # Fallback: try DD-MM-YYYY format
                try:
                    dt = datetime.strptime(job_data['created_at'], '%d-%m-%Y')
                    job_data['created_at_date'] = dt.strftime('%Y-%m-%d')
                except Exception:
                    # If all else fails, just use the raw value
                    job_data['created_at_date'] = job_data['created_at']

    if job_data.get('next_followup_at'):
        try:
            # Try ISO format first (with or without timezone)
            dt = datetime.fromisoformat(job_data['next_followup_at'].replace('Z', '+00:00'))
            job_data['next_followup_at_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            # Fallback: try YYYY-MM-DD format
            try:
                dt = datetime.strptime(job_data['next_followup_at'], '%Y-%m-%d')
                job_data['next_followup_at_date'] = dt.strftime('%Y-%m-%d')
            except Exception:
                # Fallback: try DD-MM-YYYY format
                try:
                    dt = datetime.strptime(job_data['next_followup_at'], '%d-%m-%Y')
                    job_data['next_followup_at_date'] = dt.strftime('%Y-%m-%d')
                except Exception:
                    # If all else fails, just use the raw value
                    job_data['next_followup_at_date'] = job_data['next_followup_at']

    if job_data.get('updated_at'):
        try:
            # Try ISO format first (with or without timezone)
            dt = datetime.fromisoformat(job_data['updated_at'].replace('Z', '+00:00'))
            job_data['updated_at_formatted'] = dt.strftime('%d-%m-%Y')
        except Exception:
            # Fallback: try YYYY-MM-DD format
            try:
                dt = datetime.strptime(job_data['updated_at'], '%Y-%m-%d')
                job_data['updated_at_formatted'] = dt.strftime('%d-%m-%Y')
            except Exception:
                # Fallback: try DD-MM-YYYY format
                try:
                    dt = datetime.strptime(job_data['updated_at'], '%d-%m-%Y')
                    job_data['updated_at_formatted'] = dt.strftime('%d-%m-%Y')
                except Exception:
                    # If all else fails, just use the raw value
                    job_data['updated_at_formatted'] = job_data['updated_at']

    return templates.TemplateResponse(
        request,
        "job_edit.html",
        {"job": job_data},
    )


@router.post("/jobs/{job_id}/edit")
def update_job_endpoint(
    request: Request,
    job_id: str,
    company: str = Form(...),
    title: str = Form(...),
    job_url: str = Form(...),
    status: str = Form(...),
    created_at: str = Form(...),
    next_followup_at: str = Form(""),
    job_description: str = Form(""),
    resume_used: str = Form(""),
    cover_letter: str = Form(""),
    feedback: str = Form("")
):
    update_job(
        job_id=job_id,
        company=company,
        title=title,
        job_url=job_url,
        status=status,
        created_at=created_at,
        next_followup_at=next_followup_at,
        job_description=job_description,
        resume_used=resume_used,
        cover_letter=cover_letter,
        feedback=feedback
    )
    return RedirectResponse(url="/jobs", status_code=303)
