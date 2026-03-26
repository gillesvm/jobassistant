from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from config import APP_USERNAME, APP_PASSWORD
from services.auth import is_authenticated

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None},
    )


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == APP_USERNAME and password == APP_PASSWORD:
        request.session["authenticated"] = True
        request.session["username"] = username
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Invalid username or password."},
        status_code=401,
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
