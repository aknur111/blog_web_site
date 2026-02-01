from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

from ..db import posts_col, comments_col, reactions_col
from ..schemas import PostIn, PostOut, PostUpdate, CommentIn
from ..auth import require_user

router = APIRouter(prefix="/posts", tags=["posts"])


def to_out(doc):
    return {
        "id": str(doc["_id"]),
        "author_id": doc.get("author_id"),
        "content": doc.get("content"),
        "media_url": doc.get("media_url", ""),
        "category_id": doc.get("category_id"),
        "status": doc.get("status"),
        "tags": doc.get("tags", []),
        "views": doc.get("views", 0),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


def oid(id_str: str) -> ObjectId:
    """Safe ObjectId parse with 400 error."""
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid id format")
    return ObjectId(id_str)


@router.post("", response_model=PostOut)
async def create_post(payload: PostIn, user=Depends(require_user)):
    doc = payload.dict()
    doc["author_id"] = user.get("username") or user.get("id")

    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = None
    res = await posts_col.insert_one(doc)
    doc["_id"] = res.inserted_id
    return to_out(doc)


@router.get("", response_model=List[PostOut])
async def list_posts(
    tag: Optional[str] = None,
    author: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    query = {}
    if tag:
        query["tags"] = tag
    if author:
        query["author_id"] = author
    if q:
        query["$text"] = {"$search": q}

    cursor = posts_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(to_out(d))
    return docs

@router.get("/me", response_model=List[PostOut])
async def my_posts(
    user=Depends(require_user),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    author = user.get("username") or user.get("id")
    cursor = posts_col.find({"author_id": author}).sort("created_at", -1).skip(skip).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(to_out(d))
    return docs


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: str):
    doc = await posts_col.find_one({"_id": oid(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return to_out(doc)


@router.put("/{post_id}", response_model=PostOut)
async def update_post(post_id: str, payload: PostUpdate, user=Depends(require_user)):
    _id = oid(post_id)
    p = payload.dict(exclude_none=True)

    if "push_tag" in p:
        await posts_col.update_one({"_id": _id}, {"$addToSet": {"tags": p["push_tag"]}})
    if "pull_tag" in p:
        await posts_col.update_one({"_id": _id}, {"$pull": {"tags": p["pull_tag"]}})
    if "inc_views" in p:
        await posts_col.update_one({"_id": _id}, {"$inc": {"views": p["inc_views"]}})

    update = {}
    for field in ("content", "media_url", "category_id", "status", "tags"):
        if field in p:
            update[field] = p[field]

    if update:
        update["updated_at"] = datetime.utcnow()
        await posts_col.update_one({"_id": _id}, {"$set": update})

    doc = await posts_col.find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return to_out(doc)


@router.delete("/{post_id}")
async def delete_post(post_id: str, user=Depends(require_user)):
    res = await posts_col.delete_one({"_id": oid(post_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"deleted": post_id}


@router.post("/{post_id}/comments")
async def add_comment(post_id: str, payload: CommentIn, user=Depends(require_user)):
    _id = oid(post_id)

    if not await posts_col.find_one({"_id": _id}):
        raise HTTPException(status_code=404, detail="Post not found")

    doc = payload.dict()
    doc["user_id"] = user.get("username") or user.get("id")
    doc["post_id"] = post_id
    doc["created_at"] = datetime.utcnow()

    res = await comments_col.insert_one(doc)

    return {
        "id": str(res.inserted_id),
        "user_id": doc["user_id"],
        "content": doc["content"],
        "post_id": post_id,
        "created_at": doc["created_at"].isoformat(),
    }

@router.get("/{post_id}/comments")
async def list_comments(post_id: str, limit: int = Query(50, ge=1, le=200)):
    oid(post_id)

    cursor = comments_col.find(
        {"post_id": post_id},
        {"content": 1, "user_id": 1, "created_at": 1}
    ).sort("created_at", -1).limit(limit)

    items = []
    async for c in cursor:
        items.append({
            "id": str(c["_id"]),
            "user_id": c.get("user_id", "user"),
            "content": c.get("content", ""),
            "created_at": c.get("created_at"),
        })
    return items

@router.post("/{post_id}/reactions")
async def react_to_post(
    post_id: str,
    reaction_type: str = Query(..., pattern="^(like|dislike|love)$"),
    user=Depends(require_user)
):
    oid(post_id)
    user_id = user.get("_id") or user.get("id") or user.get("username")

    await reactions_col.update_one(
        {"post_id": post_id, "user_id": user_id},
        {"$set": {"reaction_type": reaction_type, "created_at": datetime.utcnow()}},
        upsert=True
    )
    return {"ok": True, "reaction": reaction_type}


@router.get("/{post_id}/reactions")
async def get_reactions(post_id: str):
    oid(post_id)

    pipeline = [
        {"$match": {"post_id": post_id}},
        {"$group": {"_id": "$reaction_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "reaction": "$_id", "count": 1}},
    ]
    return await reactions_col.aggregate(pipeline).to_list(length=10)


@router.delete("/{post_id}/reactions")
async def remove_reaction(post_id: str, user=Depends(require_user)):
    oid(post_id)

    user_id = user.get("_id") or user.get("id") or user.get("username")

    await reactions_col.delete_one({"post_id": post_id, "user_id": user_id})
    return {"ok": True}


@router.get("/analytics/top-tags")
async def top_tags(limit: int = Query(10, ge=1, le=50)):
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"tag": "$_id", "count": 1, "_id": 0}}
    ]
    return await posts_col.aggregate(pipeline).to_list(length=limit)
