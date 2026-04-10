"""Comment endpoints."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.comment import Comment, CommentLike
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.schemas.user import UserSummary

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new comment."""
    comment = Comment(
        forum_post_id=comment_data.forum_post_id,
        author_id=current_user.id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
    )
    db.add(comment)

    # Update user profile stats
    if current_user.profile:
        current_user.profile.total_comments += 1

    db.commit()
    db.refresh(comment)
    return comment


@router.get("/post/{post_id}", response_model=CommentListResponse)
async def list_comments_for_post(
    post_id: int, db: Session = Depends(get_db), page: int = 1, size: int = 20
):
    """List comments for a forum post."""
    query = db.query(Comment).filter(Comment.forum_post_id == post_id, not Comment.is_deleted)
    total = query.count()

    comments = query.order_by(Comment.created_at).offset((page - 1) * size).limit(size).all()

    # Format response with author info
    comment_responses = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.author_id).first()
        comment_dict = CommentResponse.model_validate(comment)
        if author and author.profile:
            comment_dict.author = UserSummary(
                id=author.id,
                username=author.username,
                display_name=author.profile.display_name,
                avatar_url=author.profile.avatar_url,
                reputation_points=author.profile.reputation_points,
            )
        comment_responses.append(comment_dict)

    return CommentListResponse(
        items=comment_responses,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0,
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check permissions
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment"
        )

    comment.content = comment_data.content
    comment.is_edited = True
    from datetime import datetime

    comment.edited_at = datetime.utcnow()

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check permissions
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment"
        )

    # Soft delete
    comment.is_deleted = True
    from datetime import datetime

    comment.deleted_at = datetime.utcnow()

    db.commit()
    return None


@router.post("/{comment_id}/like", status_code=status.HTTP_201_CREATED)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Like a comment."""
    # Verify comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check if already liked
    existing_like = (
        db.query(CommentLike)
        .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == current_user.id)
        .first()
    )

    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment already liked")

    # Create like
    like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(like)

    # Update comment like count
    comment.like_count += 1

    db.commit()
    return {"message": "Comment liked successfully"}


@router.delete("/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Unlike a comment."""
    like = (
        db.query(CommentLike)
        .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == current_user.id)
        .first()
    )

    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")

    # Delete like
    db.delete(like)

    # Update comment like count
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.like_count = max(0, comment.like_count - 1)

    db.commit()
    return None
