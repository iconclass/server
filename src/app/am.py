from os import access
from fastapi import Depends, HTTPException, status, Request
from fastapi.security.base import SecurityBase
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from .config import ADMIN_DATABASE, SECRET_KEY, ACCESS_TOKEN_EXPIRE_DAYS
import sqlite3
from passlib.context import CryptContext
from .main import app

from starlette.authentication import AuthenticationBackend, AuthCredentials
from starlette.middleware.authentication import AuthenticationMiddleware


ALGORITHM = "HS256"
templates = Jinja2Templates(directory="templates")


class User(BaseModel):
    pk: str
    username: str
    name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_fromdb(username_in: str):
    con = sqlite3.connect(ADMIN_DATABASE).cursor()
    user = con.execute(
        "SELECT * FROM users WHERE username = ?", (username_in,)
    ).fetchone()
    return user


def authenticate_user(username_in: str, password_in: str):
    user = get_user_fromdb(username_in)
    if not user:
        return False
    user_pk, username, name, stored_password = user
    if not verify_password(password_in, stored_password):
        return False
    return User(pk=user_pk, username=username, name=name)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return get_user_from_token(token)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_fromdb(username)
    if not user:
        raise credentials_exception
    user_pk, username, name, stored_password = user
    return User(pk=user_pk, username=username, name=name)


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/login", response_class=HTMLResponse)
async def mylogin(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def myregister(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


class CookieTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        access_token = request.cookies.get("access_token")
        if access_token:
            user = get_user_from_token(access_token)
            if user:
                return AuthCredentials(["authenticated"]), user


app.add_middleware(AuthenticationMiddleware, backend=CookieTokenAuthBackend())
