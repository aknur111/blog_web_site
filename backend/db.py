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
    await posts_col.create_index([("tags", 1), ("created_at", -1)])
    await posts_col.create_index("author_id")
    await posts_col.create_index([("content", "text")])

    await users_col.create_index("token", unique=True, sparse=True)

    await comments_col.create_index("post_id")
    await comments_col.create_index([("post_id", 1), ("created_at", -1)])

    await reactions_col.create_index(
        [("user_id", 1), ("post_id", 1)],
        unique=True
    )


async def ping_db():
    await client.admin.command("ping")
    return True
