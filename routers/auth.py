import sys
sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Users


SECRET_KEY = "3e01bc20f26c36172ec6164b8fdf7cca93ec3c7fd044edc965dc1bb5c3fead19"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users)\
        .filter(models.Users.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
        username: str,
        user_id: int,
        expires_delta: Optional[timedelta] = None
):
    encode = {
        "sub": username,
        "id": user_id
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {
            "username": username,
            "id": user_id
        }
    except JWTError:
        raise get_user_exception()


@router.post("/token")
async def login_for_access_token(
        response: Response,
        form_data: LoginForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise get_user_exception()
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get('/logout')
async def logout(request: Request):
    msg = 'Logout Successful'
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie("access_token")
    return response


@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post('/register', response_class=HTMLResponse)
async def register_user(
        request: Request,
        email: str = Form(...),
        username: str = Form(...),
        firstname: str = Form(...),
        lastname: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
        db: Session = Depends(get_db)
):
    validation1 = db.query(Users).filter(Users.username == username).first()
    validation2 = db.query(Users).filter(Users.email == email).first()
    if password != password2:
        msg = "Passwords do not match"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    if validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    user_model = Users(
        username=username,
        email=email,
        first_name=firstname,
        last_name=lastname,
        hashed_password=get_password_hash(password),
        is_active=True
    )
    db.add(user_model)
    db.commit()

    msg = "Registration Successful"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response