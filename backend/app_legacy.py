from fastapi import FastAPI, HTTPException, Depends, Query
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from backend.db import (
    posts_col,
    users_col,
    comments_col,
    reactions_col,
    tags_col,
    create_indexes,
)
from backend.auth import get_jwt_token
from backend.schemas import (
    Post,
    User,
    Comment,
    Reaction,
    Tag,
    UserUpdate,
    PostUpdate,
    CommentUpdate,
    TagUpdate,
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    try:
        await create_indexes()
        print("MongoDB indexes created")
    except Exception as e:
        print("Warning: failed to create indexes:", e)

def parse_object_id(id_str: str, name: str = "id") -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail=f"Invalid {name}")
    return ObjectId(id_str)


def serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc

@app.post("/posts")
async def create_post(
    post: Post,
    token=Depends(get_jwt_token),
):
    data = post.dict()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = None

    res = await posts_col.insert_one(data)
    return {"id": str(res.inserted_id)}


@app.get("/posts")
async def get_posts():
    docs = []
    async for p in posts_col.find():
        docs.append(serialize(p))
    return docs


@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    oid = parse_object_id(post_id, "post_id")
    post = await posts_col.find_one({"_id": oid})
    if not post:
        raise HTTPException(404, "Post not found")
    return serialize(post)


@app.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    post: PostUpdate,
    token=Depends(get_jwt_token),
):
    oid = parse_object_id(post_id, "post_id")
    update_data = {k: v for k, v in post.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await posts_col.update_one({"_id": oid}, {"$set": update_data})
    updated = await posts_col.find_one({"_id": oid})

    if not updated:
        raise HTTPException(404, "Post not found")

    return serialize(updated)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    oid = parse_object_id(post_id, "post_id")
    res = await posts_col.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(404, "Post not found")
    return {"message": "Post deleted"}

@app.post("/tags")
async def create_tag(tag: Tag):
    data = tag.dict()
    data["created_at"] = datetime.utcnow()
    res = await tags_col.insert_one(data)
    return {"id": str(res.inserted_id)}


@app.get("/tags")
async def get_tags():
    docs = []
    async for t in tags_col.find():
        docs.append(serialize(t))
    return docs


@app.put("/tags/{tag_id}")
async def update_tag(tag_id: str, tag: TagUpdate):
    oid = parse_object_id(tag_id, "tag_id")
    update_data = {k: v for k, v in tag.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await tags_col.update_one({"_id": oid}, {"$set": update_data})
    return {"message": "Tag updated"}


@app.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str):
    oid = parse_object_id(tag_id, "tag_id")
    await tags_col.delete_one({"_id": oid})
    return {"message": "Tag deleted"}

@app.post("/users")
async def create_user(user: User):
    data = user.dict()
    data["created_at"] = datetime.utcnow()
    res = await users_col.insert_one(data)
    return {"id": str(res.inserted_id)}


@app.get("/users")
async def get_users():
    docs = []
    async for u in users_col.find():
        docs.append(serialize(u))
    return docs


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    oid = parse_object_id(user_id, "user_id")
    user = await users_col.find_one({"_id": oid})
    if not user:
        raise HTTPException(404, "User not found")
    return serialize(user)


@app.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user: UserUpdate,
    token=Depends(get_jwt_token),
):
    oid = parse_object_id(user_id, "user_id")
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await users_col.update_one({"_id": oid}, {"$set": update_data})
    updated = await users_col.find_one({"_id": oid})

    if not updated:
        raise HTTPException(404, "User not found")

    return serialize(updated)


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    oid = parse_object_id(user_id, "user_id")
    await users_col.delete_one({"_id": oid})
    return {"message": "User deleted"}

@app.post("/comments")
async def create_comment(
    comment: Comment,
    token=Depends(get_jwt_token),
):
    data = comment.dict()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = None
    res = await comments_col.insert_one(data)
    return {"id": str(res.inserted_id)}


@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: str):
    post_oid = parse_object_id(post_id, "post_id")
    docs = []
    async for c in comments_col.find({"post_id": post_oid}):
        docs.append(serialize(c))
    return docs


@app.put("/comments/{comment_id}")
async def update_comment(comment_id: str, comment: CommentUpdate):
    oid = parse_object_id(comment_id, "comment_id")
    update_data = {k: v for k, v in comment.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await comments_col.update_one({"_id": oid}, {"$set": update_data})
    return {"message": "Comment updated"}


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    oid = parse_object_id(comment_id, "comment_id")
    await comments_col.delete_one({"_id": oid})
    return {"message": "Comment deleted"}

@app.post("/reactions")
async def add_reaction(
    reaction: Reaction,
    token=Depends(get_jwt_token),
):
    user_oid = parse_object_id(reaction.user_id, "user_id")
    post_oid = parse_object_id(reaction.post_id, "post_id")

    await reactions_col.update_one(
        {"user_id": user_oid, "post_id": post_oid},
        {
            "$set": {
                "reaction_type": reaction.reaction_type,
                "created_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )
    return {"message": "Reaction saved"}


@app.get("/posts/{post_id}/reactions")
async def get_reactions(post_id: str):
    post_oid = parse_object_id(post_id, "post_id")
    docs = []
    async for r in reactions_col.find({"post_id": post_oid}):
        docs.append(serialize(r))
    return docs


@app.delete("/reactions")
async def delete_reaction(
    user_id: str = Query(...),
    post_id: str = Query(...),
):
    user_oid = parse_object_id(user_id, "user_id")
    post_oid = parse_object_id(post_id, "post_id")

    await reactions_col.delete_one(
        {"user_id": user_oid, "post_id": post_oid}
    )
    return {"message": "Reaction removed"}
