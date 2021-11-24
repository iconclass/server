from os import access
from fastapi import Depends, HTTPException, status, Request
from fastapi.security.base import SecurityBase
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.param_functions import Form
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from starlette.responses import RedirectResponse
from .config import ADMIN_DATABASE, SECRET_KEY, ACCESS_TOKEN_EXPIRE_DAYS
import sqlite3
import html
from passlib.context import CryptContext
from .main import app
from .util import send_email

from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from email_validator import validate_email, EmailNotValidError
from ksuid import KsuidMs

ALGORITHM = "HS256"
templates = Jinja2Templates(directory="templates")


def init_admin_db():
    con = sqlite3.connect(ADMIN_DATABASE)
    cur = con.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS users 
    (username TEXT, 
    name TEXT,
    password TEXT,
    activation_date TEXT)"""  # We will store these as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS") in GMT
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username ON users (username)")
    cur.execute("CREATE TABLE IF NOT EXISTS email_confirm (username TEXT, nonce TEXT)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS email_confirm_username on email_confirm (username)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS email_confirm_nonce on email_confirm (nonce)"
    )
    # The nonce used in the email_confim is a ksuid https://segment.com/blog/a-brief-history-of-the-uuid/
    # so it has a timestamp baked in


init_admin_db()


class User(BaseModel):
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
    return con.execute(
        "SELECT * FROM users WHERE username = ?", (username_in,)
    ).fetchone()


def authenticate_user(username_in: str, password_in: str):
    user_record = get_user_fromdb(username_in)
    if not user_record:
        return False
    username, name, stored_password, activation_date = user_record
    if not verify_password(password_in, stored_password):
        return False
    return User(username=username, name=name)


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

    user_record = get_user_fromdb(username)
    if not user_record:
        raise credentials_exception
    username, name, stored_password, activation_date = user_record
    return User(username=username, name=name)


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/login", response_class=HTMLResponse)
async def mylogin(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout", response_class=RedirectResponse)
async def mylogout():
    r = RedirectResponse("/")
    r.delete_cookie("access_token")
    return r


@app.get("/register", response_class=HTMLResponse)
async def myregister(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


def create_mail_reminder(email: str, subject: str = None, msg: str = None) -> str:
    # Make a nonce and insert in the admin database, send user a password reminder link
    nonce = KsuidMs()
    admin_db = sqlite3.connect(ADMIN_DATABASE)
    con = admin_db.cursor()
    con.execute("INSERT INTO email_confirm VALUES (?, ?)", (email, str(nonce)))
    admin_db.commit()
    if not subject:
        subject = "Password change request at test.iconclass.org"
    if not msg:
        msg = f"""Somebody (hopefully it was you!) submitted a password reset request at https://test.iconclass.org

To enter a new password, you can use this link: https://test.iconclass.org/password/{nonce}        
(After about a day, this link does not work anymore)
"""
    send_email(
        "info@iconclass.org",
        email,
        subject,
        msg,
    )


@app.post("/password/reminder")
async def password_reminder(email: str = Form(...)):
    user = get_user_fromdb(email)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {email} not found")
    create_mail_reminder(email)
    return {"msg": "OK! 🤓"}


@app.get("/password/{nonce}", response_class=HTMLResponse)
async def password_reset_form(request: Request, nonce: str):
    con = sqlite3.connect(ADMIN_DATABASE).cursor()
    nonce_exists = con.execute(
        "SELECT * FROM email_confirm WHERE nonce = ?", (nonce,)
    ).fetchone()
    if not nonce_exists:
        raise HTTPException(
            status_code=404, detail="The page you asked for does not exist"
        )
    return templates.TemplateResponse(
        "reset_password.html", {"request": request, "nonce": nonce}
    )


@app.post("/password/{nonce}/reset")
async def password_reset(nonce: str, newpassword: str = Form(...)):
    admin_db = sqlite3.connect(ADMIN_DATABASE)
    con = admin_db.cursor()
    nonce_exists = con.execute(
        "SELECT * FROM email_confirm WHERE nonce = ?", (nonce,)
    ).fetchone()
    if not nonce_exists:
        raise HTTPException(
            status_code=404, detail="The page you asked for does not exist"
        )
    username, nonce = nonce_exists

    hashed_password = get_password_hash(newpassword)

    con.execute(
        "UPDATE users SET password = ? WHERE username = ?", (hashed_password, username)
    )
    con.execute("DELETE FROM email_confirm WHERE nonce = ?", (nonce,))
    admin_db.commit()
    return {"msg": "Password has been reset"}


@app.post("/newuser")
async def newuser(username: str = Form(...), email: str = Form(...)):
    # Do some basic sanity checking on the email submitted
    try:
        nonce = KsuidMs()
        admin_db = sqlite3.connect(ADMIN_DATABASE)
        con = admin_db.cursor()
        con.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?) ", (email, username, None, None)
        )
        admin_db.commit()
        valid = validate_email(email)
        email = valid.email
        msg_body = f"""Thanks for registering as a new user at https://test.iconclass.org with the username {username} <{email}>

Please now enter a new password using this link: https://test.iconclass.org/password/{nonce}
"""
        create_mail_reminder(email, "New user password link", msg_body)

    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400, detail="Hmmm, that email seems to have been used already"
        )

    msg = html.escape(f"Thanks for registering: {username} <{email}>")

    return {"msg": msg}


class CookieTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        access_token = request.cookies.get("access_token")
        if access_token:
            user = get_user_from_token(access_token)
            if user:
                su = SimpleUser(user.username)
                return AuthCredentials(["authenticated"]), su


app.add_middleware(AuthenticationMiddleware, backend=CookieTokenAuthBackend())
