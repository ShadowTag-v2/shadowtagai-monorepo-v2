from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def managers():
    return {"status": "active"}
