from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import posts
from backend.auth import create_user_token
from backend.db import create_indexes, ping_db

app = FastAPI(title="Cosmic Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts, prefix="/api")


@app.get("/api/health")
async def health():
    await ping_db()
    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    try:
        await create_indexes()
        print("Indexes created")
    except Exception as e:
        import traceback
        print("Warning: failed to create indexes")
        traceback.print_exc()


@app.post("/api/register")
async def register(username: str, email: str):
    return await create_user_token(username, email)
