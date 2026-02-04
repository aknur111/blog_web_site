import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "cosmic_blog")

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client[DB_NAME]

posts_col = db["posts"]
users_col = db["users"]
comments_col = db["comments"]
tags_col = db["tags"]
reactions_col = db["reactions"]


async def create_indexes():
    existing = await posts_col.index_information()
    existing_names = set(existing.keys())

    if "tags_created_idx" not in existing_names:
        await posts_col.create_index([("tags", 1), ("created_at", -1)], name="tags_created_idx")

    if "author_idx" not in existing_names:
        await posts_col.create_index("author_id", name="author_idx")

    if "content_text_idx" not in existing_names:
        await posts_col.create_index([("content", "text")], name="content_text_idx")

    existing_u = await users_col.index_information()
    if "token_idx" not in existing_u:
        await users_col.create_index("token", unique=True, sparse=True, name="token_idx")

    existing_c = await comments_col.index_information()
    if "comment_post_idx" not in existing_c:
        await comments_col.create_index("post_id", name="comment_post_idx")

    if "comment_post_created_idx" not in existing_c:
        await comments_col.create_index([("post_id", 1), ("created_at", -1)], name="comment_post_created_idx")

    reactions = db["reactions"]
    existing_r = await reactions.index_information()
    if "react_post_type_idx" not in existing_r:
        await reactions.create_index([("post_id", 1), ("reaction_type", 1)], name="react_post_type_idx")

    if "react_user_post_unique" not in existing_r:
        await reactions.create_index([("user_id", 1), ("post_id", 1)], unique=True, name="react_user_post_unique")



async def ping_db():
    await client.admin.command("ping")
    return True
