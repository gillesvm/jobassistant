from fastapi import Request, HTTPException


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("authenticated"))


def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return None
