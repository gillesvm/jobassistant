from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET_KEY
from routes.dashboard import router as dashboard_router
from routes.jobs import router as jobs_router
from routes.auth import router as auth_router

app = FastAPI(title="JobAssistant")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="jobassistant_session",
    same_site="lax",
    https_only=False,  # set to True later when using HTTPS
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
