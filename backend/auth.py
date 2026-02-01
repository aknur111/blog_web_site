import os
import jwt
from fastapi import HTTPException, Depends, Header
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import secrets
from dotenv import load_dotenv

from .db import users_col

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

def get_jwt_token(token: str = Depends(oauth2_scheme)) -> str:
    verify_token(token)
    return token

async def create_user_token(username: str, email: str):
    token = secrets.token_urlsafe(24)
    doc = {"username": username, "email": email, "token": token, "created_at": datetime.utcnow()}
    res = await users_col.insert_one(doc)
    return {"id": str(res.inserted_id), "username": username, "email": email, "token": token}

async def require_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    user = await users_col.find_one({"token": token})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": str(user["_id"]), "username": user.get("username"), "email": user.get("email")}
