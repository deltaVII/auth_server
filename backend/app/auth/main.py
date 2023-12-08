from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from .jwt import verify_jwt_token
from .schemas import AccessToken
from .db import get_user_db, get_user_roles_db

'''
Функции для использования в зависимостях
'''

async def verify_token(
        token: AccessToken) -> dict:
    
    decoded_data = verify_jwt_token(token.access_token)
    if decoded_data is None:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    return decoded_data


async def get_user(
        token: AccessToken, 
        session: AsyncSession = Depends(get_async_session)) -> dict:
    
    decoded_data = verify_jwt_token(token.access_token)
    if decoded_data is None:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    
    try:
        user = await get_user_db(decoded_data["email"], session)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    return user


async def get_user_role(
        token: AccessToken, 
        session: AsyncSession = Depends(get_async_session)) -> dict:
    
    decoded_data = verify_jwt_token(token.access_token)
    if decoded_data is None:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    
    try:
        user = await get_user_roles_db(decoded_data["email"], session)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    return user


def has_user_role(required_role: str) -> dict:
    def role_validator(
            current_user: dict = Depends(get_user_role)):
        
        if required_role in current_user['roles']:
            return current_user
        raise HTTPException(
            status_code=403, detail="Insufficient permissions")
    return role_validator