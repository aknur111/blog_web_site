from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from backend.database import get_db
from backend.auth import create_access_token, verify_token, get_jwt_token  # Убираем JWTBearer
from backend.models import Post, User, Reaction, Comment
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Модель данных для Post
class Post(BaseModel):
    author_id: str
    content: str
    media_url: str
    category_id: str
    status: str
    tags: List[str]

@app.post("/posts")
async def create_post(post: Post, db: MongoClient = Depends(get_db), token: str = Depends(get_jwt_token)):
    # Логика создания поста
    post_data = {
        "author_id": post.author_id,
        "content": post.content,
        "media_url": post.media_url,
        "created_at": datetime.now(),
        "tags": post.tags,
        "category_id": post.category_id,
        "status": post.status,
    }
    result = db.posts.insert_one(post_data)
    return {"id": str(result.inserted_id), "message": "Post created successfully!"}

@app.get("/posts/{post_id}")
async def get_post(post_id: str, db: MongoClient = Depends(get_db), token: str = Depends(get_jwt_token)):
    # Получение поста по ID
    post = db.posts.find_one({"_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Дополнительные эндпоинты для CRUD операций, комментариев, лайков и т.д.
