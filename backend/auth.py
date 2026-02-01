import secrets
from datetime import datetime
from fastapi import HTTPException, Header
from backend.db import users_col

async def create_user_token(username: str, email: str):
    existing = await users_col.find_one({"email": email})
    if existing:
        return {
            "id": str(existing["_id"]),
            "username": existing["username"],
            "email": existing["email"],
            "token": existing["token"],
        }

    token = secrets.token_urlsafe(24)

    user = {
        "username": username,
        "email": email,
        "token": token,
        "created_at": datetime.utcnow(),
    }

    res = await users_col.insert_one(user)

    return {
        "id": str(res.inserted_id),
        "username": username,
        "email": email,
        "token": token,
    }


async def require_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split(" ")
        if scheme != "Bearer":
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    user = await users_col.find_one({"token": token})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user["_id"] = str(user["_id"])
    return user
