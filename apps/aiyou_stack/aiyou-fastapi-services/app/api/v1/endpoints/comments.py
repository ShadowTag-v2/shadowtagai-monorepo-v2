# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Comment endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Create a new comment."""
    return CommentService.create_comment(
        db,
        forum_post_id=comment_data.forum_post_id,
        author=current_user,
        content=comment_data.content,
        parent_id=comment_data.parent_id,
    )


@router.get("/post/{post_id}", response_model=CommentListResponse)
async def list_comments_for_post(
    post_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    page: int = 1,
    size: int = 20,
):
    """List comments for a forum post."""
    result = CommentService.list_comments_for_post(db, post_id, page, size)

    comment_responses = []
    for item in result["items"]:
        comment_dict = CommentResponse.model_validate(item["comment"])
        if item["author"]:
            comment_dict.author = item["author"]
        comment_responses.append(comment_dict)

    return CommentListResponse(
        items=comment_responses,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"],
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):  # noqa: B008
    """Get a comment."""
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Update a comment."""
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    return CommentService.update_comment(db, comment, comment_data.content)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Delete a comment."""
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    CommentService.soft_delete_comment(db, comment)


@router.post("/{comment_id}/like", status_code=status.HTTP_201_CREATED)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Like a comment."""
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    try:
        CommentService.like_comment(db, comment_id, current_user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment already liked"
        ) from None

    return {"message": "Comment liked successfully"}


@router.delete("/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Unlike a comment."""
    try:
        CommentService.unlike_comment(db, comment_id, current_user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Like not found"
        ) from None
