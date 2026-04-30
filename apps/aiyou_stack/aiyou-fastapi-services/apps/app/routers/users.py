"""User management endpoints.

Provides CRUD operations for users with full accessibility support:
- Clear error messages
- Descriptive documentation
- Semantic HTTP status codes
- Request validation with helpful feedback
"""

from datetime import datetime

from fastapi import APIRouter, Path, Query, status

from app.models.schemas import ErrorResponse, UserCreate, UserResponse, UserUpdate
from app.utils.errors import ConflictError, NotFoundError

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={
        422: {
            "description": "Validation error - invalid input data",
            "model": ErrorResponse,
        },
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)

# In-memory storage for demonstration (replace with database in production)
users_db: list[dict] = []
user_id_counter = 1


@router.get(
    "",
    summary="Get all users",
    description="""
    Retrieve a list of all users in the system.

    Supports pagination to handle large datasets efficiently.

    **Query Parameters:**
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum number of records to return

    **Returns:**
    - List of user objects with all fields
    """,
    response_model=list[UserResponse],
    response_description="List of users with metadata",
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return (1-1000)",
    ),
) -> list[UserResponse]:
    """Get all users with pagination support.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum records to return (default: 100, max: 1000)

    Returns:
        List[UserResponse]: List of user objects

    Example Response:
        ```json
        [
            {
                "id": 1,
                "name": "Jane Smith",
                "email": "redacted@shadowtag-v4.local",
                "age": 28,
                "created_at": "2025-11-15T10:00:00Z",
                "updated_at": "2025-11-15T10:00:00Z"
            }
        ]
        ```

    """
    return users_db[skip : skip + limit]


@router.get(
    "/{user_id}",
    summary="Get a specific user",
    description="""
    Retrieve a user by their unique identifier.

    **Path Parameters:**
    - `user_id`: Positive integer identifying the user

    **Returns:**
    - User object with all fields including metadata

    **Errors:**
    - 404 Not Found - User with the specified ID doesn't exist
    """,
    response_model=UserResponse,
    response_description="User object with all fields",
    responses={
        404: {"description": "User not found", "model": ErrorResponse},
    },
)
async def get_user(
    user_id: int = Path(..., gt=0, description="The unique ID of the user to retrieve"),
) -> UserResponse:
    """Get a specific user by ID.

    Args:
        user_id: Positive integer user identifier

    Returns:
        UserResponse: User object with all fields

    Raises:
        NotFoundError: If user with specified ID doesn't exist

    Example Response:
        ```json
        {
            "id": 1,
            "name": "Jane Smith",
            "email": "redacted@shadowtag-v4.local",
            "age": 28,
            "created_at": "2025-11-15T10:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        }
        ```

    """
    for user in users_db:
        if user["id"] == user_id:
            return UserResponse(**user)

    raise NotFoundError(
        message=f"User with ID {user_id} was not found",
        details={
            "user_id": user_id,
            "suggestion": "Please verify the user ID and try again",
        },
    )


@router.post(
    "",
    summary="Create a new user",
    description="""
    Create a new user in the system.

    **Request Body:**
    - All fields are required
    - Email must be unique
    - Name must be 2-100 characters
    - Age must be 0-150 (if provided)

    **Returns:**
    - Created user object with assigned ID and timestamps

    **Errors:**
    - 409 Conflict - Email already exists
    - 422 Validation Error - Invalid input data
    """,
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    response_description="Created user object with assigned ID and metadata",
    responses={
        201: {"description": "User successfully created"},
        409: {"description": "Email already exists", "model": ErrorResponse},
    },
)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user.

    Args:
        user: User data (name, email, age)

    Returns:
        UserResponse: Created user with ID and timestamps

    Raises:
        ConflictError: If email already exists

    Example Request:
        ```json
        {
            "name": "John Doe",
            "email": "redacted@shadowtag-v4.local",
            "age": 30
        }
        ```

    Example Response:
        ```json
        {
            "id": 1,
            "name": "John Doe",
            "email": "redacted@shadowtag-v4.local",
            "age": 30,
            "created_at": "2025-11-15T10:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        }
        ```

    """
    global user_id_counter

    # Check for duplicate email
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise ConflictError(
                message=f"A user with email '{user.email}' already exists",
                details={
                    "email": user.email,
                    "suggestion": "Please use a different email address or update the existing user",
                },
            )

    # Create new user
    now = datetime.utcnow()
    new_user = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "created_at": now,
        "updated_at": now,
    }

    users_db.append(new_user)
    user_id_counter += 1

    return UserResponse(**new_user)


@router.put(
    "/{user_id}",
    summary="Update a user",
    description="""
    Update an existing user's information.

    **Path Parameters:**
    - `user_id`: ID of the user to update

    **Request Body:**
    - All fields are optional
    - Only provided fields will be updated
    - Email must be unique if changed

    **Returns:**
    - Updated user object with new timestamp

    **Errors:**
    - 404 Not Found - User doesn't exist
    - 409 Conflict - New email already exists
    - 422 Validation Error - Invalid input data
    """,
    response_model=UserResponse,
    response_description="Updated user object",
    responses={
        404: {"description": "User not found", "model": ErrorResponse},
        409: {"description": "Email already exists", "model": ErrorResponse},
    },
)
async def update_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to update"),
    user_update: UserUpdate = ...,
) -> UserResponse:
    """Update an existing user.

    Args:
        user_id: Positive integer user identifier
        user_update: Fields to update (all optional)

    Returns:
        UserResponse: Updated user object

    Raises:
        NotFoundError: If user doesn't exist
        ConflictError: If new email already exists

    Example Request:
        ```json
        {
            "name": "Jane Doe",
            "email": "redacted@shadowtag-v4.local"
        }
        ```

    """
    # Find user
    user_index = None
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            user_index = i
            break

    if user_index is None:
        raise NotFoundError(
            message=f"User with ID {user_id} was not found",
            details={
                "user_id": user_id,
                "suggestion": "Please verify the user ID and try again",
            },
        )

    # Check for email conflict (if email is being updated)
    if user_update.email:
        for i, existing_user in enumerate(users_db):
            if i != user_index and existing_user["email"] == user_update.email:
                raise ConflictError(
                    message=f"A user with email '{user_update.email}' already exists",
                    details={
                        "email": user_update.email,
                        "suggestion": "Please use a different email address",
                    },
                )

    # Update user
    user = users_db[user_index]
    if user_update.name is not None:
        user["name"] = user_update.name
    if user_update.email is not None:
        user["email"] = user_update.email
    if user_update.age is not None:
        user["age"] = user_update.age
    user["updated_at"] = datetime.utcnow()

    return UserResponse(**user)


@router.delete(
    "/{user_id}",
    summary="Delete a user",
    description="""
    Delete a user from the system.

    **Path Parameters:**
    - `user_id`: ID of the user to delete

    **Returns:**
    - 204 No Content on successful deletion

    **Errors:**
    - 404 Not Found - User doesn't exist
    """,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "User successfully deleted"},
        404: {"description": "User not found", "model": ErrorResponse},
    },
)
async def delete_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to delete"),
) -> None:
    """Delete a user.

    Args:
        user_id: Positive integer user identifier

    Raises:
        NotFoundError: If user doesn't exist

    Returns:
        None (HTTP 204 No Content)

    """
    # Find and delete user
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(i)
            return

    raise NotFoundError(
        message=f"User with ID {user_id} was not found",
        details={
            "user_id": user_id,
            "suggestion": "Please verify the user ID and try again",
        },
    )
