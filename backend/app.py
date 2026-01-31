from fastapi import FastAPI, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

from backend.database import get_db, create_indexes
from backend.auth import get_jwt_token
from backend.models import Post, User, Comment, Reaction, Tag
from backend.models import UserUpdate, PostUpdate, CommentUpdate, TagUpdate

app = FastAPI()

@app.on_event("startup")
def startup_event():
    db = get_db()
    create_indexes(db)
    print("✅ MongoDB indexes created")

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.post("/posts")
def create_post(
    post: Post,
    db: MongoClient = Depends(get_db),
    token = Depends(get_jwt_token)
):
    data = post.dict()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = None

    result = db.posts.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/posts")
def get_posts(db=Depends(get_db)):
    return [serialize(p) for p in db.posts.find()]


@app.get("/posts/{post_id}")
def get_post(post_id: str, db=Depends(get_db)):
    post = db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(404, "Post not found")
    return serialize(post)


@app.put("/posts/{post_id}")
def update_post(
    post_id: str,
    post: PostUpdate,
    db=Depends(get_db),
    token=Depends(get_jwt_token)
):
    update_data = {k: v for k, v in post.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    result = db.posts.find_one_and_update(
        {"_id": ObjectId(post_id)},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(404, "Post not found")

    return serialize(result)

@app.delete("/posts/{post_id}")
def delete_post(post_id: str, db=Depends(get_db)):
    res = db.posts.delete_one({"_id": ObjectId(post_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Post not found")
    return {"message": "Post deleted"}

@app.post("/tags")
def create_tag(tag: Tag, db=Depends(get_db)):
    data = tag.dict()
    data["created_at"] = datetime.utcnow()
    result = db.tags.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/tags")
def get_tags(db=Depends(get_db)):
    return [serialize(t) for t in db.tags.find()]

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: str, db=Depends(get_db)):
    db.tags.delete_one({"_id": ObjectId(tag_id)})
    return {"message": "Tag deleted"}

@app.put("/tags/{tag_id}")
def update_tag(tag_id: str, tag: TagUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in tag.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    db.tags.update_one(
        {"_id": ObjectId(tag_id)},
        {"$set": update_data}
    )
    return {"message": "Tag updated"}

@app.put("/posts/{post_id}/remove_tag/{tag_id}")
def remove_tag_from_post(post_id: str, tag_id: str, db=Depends(get_db)):
    db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"tags": ObjectId(tag_id)}}
    )
    return {"message": "Tag removed from post"}

@app.post("/users")
def create_user(user: User, db=Depends(get_db)):
    data = user.dict()
    data["created_at"] = datetime.utcnow()
    result = db.users.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/users")
def get_users(db=Depends(get_db)):
    return [serialize(u) for u in db.users.find()]


@app.get("/users/{user_id}")
def get_user(user_id: str, db=Depends(get_db)):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")
    return serialize(user)

@app.put("/users/{user_id}")
def update_user(
    user_id: str,
    user: UserUpdate,
    db=Depends(get_db),
    token=Depends(get_jwt_token)
):
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    result = db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(404, "User not found")

    result["_id"] = str(result["_id"])
    return result


@app.delete("/users/{user_id}")
def delete_user(user_id: str, db=Depends(get_db)):
    db.users.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted"}

@app.post("/comments")
def create_comment(
    comment: Comment,
    db=Depends(get_db),
    token=Depends(get_jwt_token)
):
    data = comment.dict()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = None
    result = db.comments.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/posts/{post_id}/comments")
def get_comments(post_id: str, db=Depends(get_db)):
    return [
        serialize(c)
        for c in db.comments.find({"post_id": ObjectId(post_id)})
    ]


@app.put("/comments/{comment_id}")
def update_comment(
    comment_id: str,
    comment: CommentUpdate,
    db=Depends(get_db)
):
    update_data = {k: v for k, v in comment.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": update_data}
    )

    return {"message": "Comment updated"}


@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, db=Depends(get_db)):
    db.comments.delete_one({"_id": ObjectId(comment_id)})
    return {"message": "Comment deleted"}

@app.post("/reactions")
def add_reaction(
    reaction: Reaction,
    db=Depends(get_db),
    token=Depends(get_jwt_token)
):
    db.reactions.update_one(
        {
            "user_id": ObjectId(reaction.user_id),
            "post_id": ObjectId(reaction.post_id)
        },
        {
            "$set": {
                "reaction_type": reaction.reaction_type,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    return {"message": "Reaction saved"}


@app.get("/posts/{post_id}/reactions")
def get_reactions(post_id: str, db=Depends(get_db)):
    return [
        serialize(r)
        for r in db.reactions.find({"post_id": ObjectId(post_id)})
    ]

@app.delete("/reactions")
def delete_reaction(user_id: str, post_id: str, db=Depends(get_db)):
    db.reactions.delete_one({
        "user_id": ObjectId(user_id),
        "post_id": ObjectId(post_id)
    })
    return {"message": "Reaction removed"}
