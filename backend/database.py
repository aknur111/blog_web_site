from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    return client.personal_blog


def create_indexes(db):
    db.posts.create_index([
    ("author_id", ASCENDING),
    ("category_id", ASCENDING)
    ])
    db.posts.create_index([("tags", ASCENDING)])
    db.posts.create_index([("created_at", -1)])

    db.comments.create_index([("post_id", ASCENDING)])
    db.reactions.create_index([("post_id", ASCENDING), ("user_id", ASCENDING)])
    db.users.create_index("email", unique=True)