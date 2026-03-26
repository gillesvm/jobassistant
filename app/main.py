from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.dashboard import router as dashboard_router
from routes.jobs import router as jobs_router

app = FastAPI(title="JobAssistant")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard_router)
app.include_router(jobs_router)
