from typing import Annotated

from fastapi import Depends, Header
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from .jwt import verify_jwt_token
from .db import get_user as get_user_db
from .db import get_user_roles as get_user_roles_db

'''
Функции для использования в зависимостях
'''

async def verify_token(
        Authorization: str|None = Header()) -> dict:

    decoded_data = verify_jwt_token(Authorization.split()[1])
    if decoded_data is None:
        raise HTTPException(
            status_code=400, detail='Invalid token')
    return decoded_data


async def get_user(
        token_data: dict = Depends(verify_token), 
        session: AsyncSession = Depends(get_async_session)) -> dict:
    
    try:
        user = await get_user_db(token_data['email'], session)
    except ValueError:
        raise HTTPException(
            status_code=400, detail='Incorrect username or password')
    return user


async def get_user_role(
        token_data: dict = Depends(verify_token), 
        session: AsyncSession = Depends(get_async_session)) -> dict:
    
    try:
        user = await get_user_roles_db(token_data['email'], session)
    except ValueError:
        raise HTTPException(
            status_code=400, detail='Incorrect username or password')
    return user


def has_user_role(required_role: str) -> dict:
    def role_validator(
            current_user: dict = Depends(get_user_role)):
        
        print(current_user)

        if required_role in current_user['roles']:
            return current_user
        raise HTTPException(
            status_code=403, detail='Insufficient permissions')
    return role_validator