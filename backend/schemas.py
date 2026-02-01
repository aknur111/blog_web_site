from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PostIn(BaseModel):
    author_id: str
    content: str
    media_url: Optional[str] = None
    category_id: str = "general"
    status: str = "published"
    tags: List[str] = Field(default_factory=list)

class PostOut(PostIn):
    id: str
    views: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

class PostUpdate(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None
    category_id: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    inc_views: Optional[int] = None
    push_tag: Optional[str] = None
    pull_tag: Optional[str] = None

class UserIn(BaseModel):
    username: str
    email: str

class UserOut(UserIn):
    id: str
    token: str

class CommentIn(BaseModel):
    content: str
