from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

from services.mock_data import get_all_jobs, get_job_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/jobs")
def jobs_list(request: Request):
    jobs = get_all_jobs()
    return templates.TemplateResponse(
        request,
        "jobs_list.html",
        {"jobs": jobs},
    )


@router.get("/jobs/new")
def new_job_form(request: Request):
    return templates.TemplateResponse(
        request,
        "job_form.html",
        {},
    )


@router.get("/jobs/{job_id}")
def job_detail(request: Request, job_id: str):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return templates.TemplateResponse(
        request,
        "job_detail.html",
        {"job": job},
    )
