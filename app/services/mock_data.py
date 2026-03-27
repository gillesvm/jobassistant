from datetime import date, timedelta

MOCK_JOBS = [
    {
        "job_id": "1",
        "company": "Siemens",
        "title": "DevOps Security Engineer",
        "status": "applied",
        "stage": "application_sent",
        "next_followup_at": str(date.today() + timedelta(days=2)),
        "updated_at": str(date.today()),
        "notes_summary": "Applied via careers site."
    },
    {
        "job_id": "2",
        "company": "CloudPhilos",
        "title": "Principal Engineer",
        "status": "draft",
        "stage": "considering",
        "next_followup_at": str(date.today() - timedelta(days=1)),
        "updated_at": str(date.today()),
        "notes_summary": "Need to message CTO."
    },
    {
        "job_id": "3",
        "company": "Example Corp",
        "title": "Platform Engineer",
        "status": "rejected",
        "stage": "closed",
        "next_followup_at": "",
        "updated_at": str(date.today()),
        "notes_summary": "Rejected after first interview."
    },
]


def get_all_jobs():
    return MOCK_JOBS


def get_job_by_id(job_id: str):
    for job in MOCK_JOBS:
        if job["job_id"] == job_id:
            return job
    return None
