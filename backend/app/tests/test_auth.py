from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.main import has_user_role, get_user, verify_token
from ..auth.db import add_user_role, get_user_db
from ..database import get_async_session

router = APIRouter(
    prefix="/test_auth",
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

@router.post("/add_role")
async def get_user_me(
        role: str,
        current_user: dict = Depends(get_user),
        session: AsyncSession = Depends(get_async_session)):
    
    add_user_role(current_user, role, session)

    return {"status": "200"}

@router.get("/test")
async def get_user_me(
        email: str = 'ssuser@example.com', 
        session: AsyncSession = Depends(get_async_session)):

    q=await get_user_db(email, session)
    return q