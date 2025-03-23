from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

# Security settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake User Database
fake_users_db = {
    "johndoe@example.com": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    }
}

# In-memory token store
issued_tokens = {}


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    username: str | None = None
    exp: datetime | None = None


class User(BaseModel):
    username: str
    email: str
    full_name: str | None = None


class UserInDB(User):
    hashed_password: str


# Security settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, email: str, password: str):
    user = get_user(fake_db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        exp = datetime.fromtimestamp(payload["exp"], timezone.utc)
        if username is None:
            raise credentials_exception
        return TokenData(username=username, exp=exp)
    except InvalidTokenError:
        raise credentials_exception


@app.post("/token")
async def login_or_register_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = get_user(fake_users_db, form_data.username)

    if not user:
        # If user does not exist, register them
        hashed_password = get_password_hash(form_data.password)
        fake_users_db[form_data.username] = {
            "username": form_data.username.split("@")[
                0
            ],  # Extract a username from email
            "full_name": None,
            "email": form_data.username,
            "hashed_password": hashed_password,
        }
        user = get_user(fake_users_db, form_data.username)

    # Validate credentials (even for newly created users)
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Store Token
    if user.username not in issued_tokens:
        issued_tokens[user.username] = []
    issued_tokens[user.username].append(
        {"token": access_token, "expires_at": expires_at}
    )

    return Token(access_token=access_token, token_type="bearer", expires_at=expires_at)


# Endpoint to get issued tokens
@app.get("/tokens", response_model=list[Token])
async def get_issued_tokens(
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    user_tokens = issued_tokens.get(current_user.username, [])
    return [
        Token(
            access_token=token["token"],
            token_type="bearer",
            expires_at=token["expires_at"],
        )
        for token in user_tokens
    ]
