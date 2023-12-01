from fastapi import APIRouter, Depends

from ..auth.main import has_user_role, get_user

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.get("/has_role/")
def get_resource_data(
        current_user: dict = Depends(has_user_role('test1'))):

    return {"message": "Welcome, resource owner!"}

@router.get("/me")
async def get_user_me(
        current_user: dict = Depends(get_user)):

    return current_user

