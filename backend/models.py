from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Post(BaseModel):
    author_id: str
    content: str
    media_url: Optional[str] = None
    category_id: str
    status: str
    tags: List[str] = Field(default_factory=list)
    views: int = 0


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


class CommentUpdate(BaseModel):
    content: Optional[str] = None

class Reaction(BaseModel):
    user_id: str
    post_id: str
    reaction_type: str

class User(BaseModel):
    username: str
    email: EmailStr
    role: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class Tag(BaseModel):
    name: str
    description: Optional[str] = None


class TagUpdate(BaseModel):
    description: Optional[str] = None
