from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from .jwt import verify_jwt_token
from .schemas import AccessToken
from .db import get_user_db
from .db import get_user_roles_db

# а где ексепты?

'''
    try:
        db_data = await get_data_db(token.refresh_token, session)
    except AttributeError as ex:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
'''

async def verify_token(
        token: AccessToken):
    
    decoded_data = verify_jwt_token(token.access_token)
    if decoded_data is None:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    return decoded_data

async def get_user(
        token: AccessToken, 
        session: AsyncSession = Depends(get_async_session)):
    
    decoded_data = verify_jwt_token(token.access_token)
    if not decoded_data:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    
    try:
        user = await get_user_db(decoded_data["email"], session)
    except AttributeError as ex:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    if not user:
        raise HTTPException(
            status_code=400, detail="User not found")
    return user

async def get_user_role(
        token: AccessToken, 
        session: AsyncSession = Depends(get_async_session)):
    
    decoded_data = verify_jwt_token(token.access_token)
    if not decoded_data:
        raise HTTPException(
            status_code=400, detail="Invalid token")
    
    try:
        user = await get_user_roles_db(decoded_data["email"], session)
    except AttributeError as ex:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    if not user:
        raise HTTPException(
            status_code=400, detail="User not found")
    return user

def has_role(required_role: str):
    def role_validator(
            current_user: dict = Depends(get_user_role)):
        
        if required_role in current_user['roles']:
            return current_user
        raise HTTPException(
            status_code=403, detail="Insufficient permissions")
    return role_validator