from fastapi import APIRouter
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form

from database import SessionLocal
from routers.auth import get_current_user, authenticate_user, get_user_exception

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return bcrypt_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def change_password(request: Request):
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
        request: Request,
        username: str = Form(...),
        current_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
        db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    print(user)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user2 = authenticate_user(username, current_password, db)
    if user2 is None:
        raise get_user_exception()
    if password != password2:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    user2.hashed_password = get_password_hash(password)
    db.add(user2)
    db.commit()

    msg = "Password changed successfully"
    return templates.TemplateResponse("change-password.html", {"request": request, "msg": msg})
