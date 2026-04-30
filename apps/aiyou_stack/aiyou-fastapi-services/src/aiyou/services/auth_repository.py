"""Auth service layer addendum.

Extracts the remaining db.query from the auth route.
The existing AuthService handles password/token operations;
this adds user lookup.
"""

from sqlalchemy.orm import Session

from ..models.user import User


class AuthRepository:
    """Repository for auth-related database lookups."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Look up a user by email address."""
        return db.query(User).filter(User.email == email).first()
