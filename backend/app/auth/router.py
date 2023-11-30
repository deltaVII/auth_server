from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..database import get_async_session
from .jwt import create_tokens
from .jwt import verify_jwt_token
from .schemas import CreateUser
from .schemas import LoginUser
from .schemas import RefreshToken
from .db import add_user_role
from .db import get_data_db
from .db import get_user_db
from .db import create_user_db
from .db import save_tokens_db

from .main import get_user
from .main import has_role


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/resources/")
def get_resource_data(
        current_user: dict = Depends(has_role('test1'))):
    
    return {"message": "Welcome, resource owner!"}

@router.get("/users/me")
async def get_user_me(
        current_user: dict = Depends(get_user)):
    
    return current_user

@router.get("/users/role")
async def get_user_me(
        role: str, 
        current_user: dict = Depends(get_user), 
        session: AsyncSession = Depends(get_async_session)):
    
    await add_user_role(current_user, role, session)
    return {'status': '200'}


@router.post("/register")
async def register_user(
        new_user: CreateUser, 
        session: AsyncSession = Depends(get_async_session)):
    
    hashed_password = pwd_context.hash(new_user.password)
    user_data = new_user.dict()
    user_data['hashed_password'] = hashed_password
    try:
        await create_user_db(
            user_data,
            session
        )
    except IntegrityError as ex:
        print(ex)
        raise HTTPException(
            status_code=409, detail="Email already registered")
    return {"status": "200"}


@router.post("/login")
async def login_user(
        get_user: LoginUser, 
        session: AsyncSession = Depends(get_async_session)):
    
    try:
        user = await get_user_db(get_user.email, session)
    except AttributeError as ex:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(
        get_user.password, 
        user['hashed_password'])
    if not is_password_correct:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    
    refresh_token, access_token = create_tokens(user)

    await save_tokens_db(
        old_token=None,
        new_token=refresh_token,
        user_id=user['id'],
        session=session
    )
    return {"refresh_token": refresh_token, 
            "access_token": access_token, 
            "token_type": "bearer"}


@router.post("/token")
async def update_token(
        token: RefreshToken, 
        session: AsyncSession = Depends(get_async_session)):
    
    token_data = verify_jwt_token(token.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=400, detail="Incorrect token")
    
    try:
        db_data = await get_data_db(token.refresh_token, session)
    except AttributeError as ex:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    
    db_token = db_data['token']
    if db_token is None or not db_token['is_relevant']:
        raise HTTPException(
            status_code=400, detail="Incorrect token")

    refresh_token, access_token = create_tokens(db_data["user"])
    await save_tokens_db(
        old_token=db_token['token'],
        new_token=refresh_token,
        user_id=db_token['user_id'],
        session=session
    )
    return {"refresh_token": refresh_token, 
            "access_token": access_token, 
            "token_type": "bearer"}





