import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("MONGO_DB", "cosmic_blog")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
)

db = client[DB_NAME]

posts_col = db["posts"]
users_col = db["users"]
comments_col = db["comments"]
tags_col = db["tags"]

async def create_indexes():
    await posts_col.create_index([("tags", 1), ("created_at", -1)], name="tags_created_idx")
    await posts_col.create_index("author_id", name="author_idx")
    await posts_col.create_index([("content", "text")], name="content_text_idx")
    await users_col.create_index("token", unique=True, sparse=True, name="token_idx")
    await comments_col.create_index("post_id", name="comment_post_idx")
    await comments_col.create_index([("post_id", 1), ("created_at", -1)], name="comment_post_created_idx")
    await db["reactions"].create_index([("post_id", 1), ("reaction_type", 1)], name="react_post_type_idx")
    await db["reactions"].create_index([("user_id", 1), ("post_id", 1)], unique=True, name="react_user_post_unique")


async def ping_db():
    await client.admin.command("ping")
    return True
