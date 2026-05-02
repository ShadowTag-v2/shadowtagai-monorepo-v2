from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from src.database import get_db
    from src.models import User
except ImportError:
    from database import get_db
    from models import User

# ==============================================================================
# 1. Pydantic Schemas (For Request/Response Validation)
# ==============================================================================
# We define these here so we never accidentally return a user's hashed password!


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    # This tells Pydantic to read the data from a SQLAlchemy model object
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# 2. FastAPI Application Initialization
# ==============================================================================
app = FastAPI(
    title="ShadowTag-v2 Services API",
    description="The core backend service for the Uphillsnowball Monorepo",
    version="0.1.0",
)


# ==============================================================================
# 3. API Endpoints
# ==============================================================================


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:  # noqa: B008
    """Create a new user in the database."""
    # Check if the user already exists using SQLAlchemy 2.0 syntax
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalars(stmt).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Note: In a real app, you MUST hash the password here (e.g., with passlib/bcrypt)
    fake_hashed_password = f"hashed_{user.password}"

    # Create the SQLAlchemy model instance
    db_user = User(email=user.email, hashed_password=fake_hashed_password)

    # Save it to the database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/users", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):  # noqa: B008
    """Fetch a list of all users."""
    # Fetch users using SQLAlchemy 2.0 syntax
    stmt = select(User).offset(skip).limit(limit)
    users = db.scalars(stmt).all()

    return list(users)


@app.get("/health")
def health_check():
    """Simple health check endpoint for Docker/Kubernetes."""
    return {"status": "healthy", "service": "shadowtag_v4-fastapi-services"}
