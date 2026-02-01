from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Post(BaseModel):
    id: Optional[str] = None
    author_id: str
    content: str
    media_url: Optional[str] = ""
    category_id: str
    status: str
    tags: List[str] = Field(default_factory=list)
    views: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None
    category_id: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class Comment(BaseModel):
    user_id: str
    post_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None

class Reaction(BaseModel):
    user_id: str
    post_id: str
    reaction_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    username: str
    email: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class Tag(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class TagUpdate(BaseModel):
    description: Optional[str] = None
