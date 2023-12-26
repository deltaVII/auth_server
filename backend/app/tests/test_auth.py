from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.main import has_user_role, get_user, verify_token
from ..auth.db import add_user_role as add_user_role_db
from ..auth.db import add_role as add_role_db
from ..database import get_session as get_db_session

router = APIRouter(
    prefix='/test_auth',
    tags=['Test']
)

@router.get('/has_role/')
async def get_resource_data(
        current_user: dict = Depends(has_user_role('test_role'))):

    return {'message': 'Welcome, test_role!'}

@router.get('/me')
async def get_user_me(
        current_user: dict = Depends(get_user)):

    return current_user

@router.get('/verify')
async def get_user_me(
        current_user: dict = Depends(verify_token)):

    return current_user

@router.post('/add_user_role')
async def get_user_me(
        role: str,
        current_user: dict = Depends(get_user),
        session: AsyncSession = Depends(get_db_session)):
    
    try:
        await add_user_role_db(current_user, role, session)
    except ValueError:
        raise HTTPException(
            status_code=400, detail='Incorrect role')
    return {'status': '200'}

@router.post('/add_role')
async def get_user_me(
        role: str,
        session: AsyncSession = Depends(get_db_session)):
    
    await add_role_db(role, session)

    return {'status': '200'}