from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Home"])
def read_root():
    return {"message": "Welcome to the ChocoMax Shop API"}
