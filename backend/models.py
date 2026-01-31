from pydantic import BaseModel
from typing import List

class Post(BaseModel):
    author_id: str
    content: str
    media_url: str
    category_id: str
    status: str
    tags: List[str]

class Comment(BaseModel):
    user_id: str
    post_id: str
    content: str

class Reaction(BaseModel):
    user_id: str
    post_id: str
    reaction_type: str  # like, love, etc.

class User(BaseModel):
    username: str
    email: str
    role: str  # author, reader
