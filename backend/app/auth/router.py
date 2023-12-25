from fastapi import APIRouter, Depends
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..database import get_async_session
from .jwt import create_tokens, verify_jwt_token
from .schemas import CreateUser, LoginUser
from .schemas import RefreshToken
from .db import get_session_with_user as get_data_db
from .db import get_user_password as get_user_password_db
from .db import create_user as create_user_db
from .db import update_user_session as update_user_session_db
from .db import create_user_session as create_user_session_db


'''
Необходимые эндпоинты для авторизации
'''

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/register')
async def register_user(
        new_user: CreateUser, 
        session: AsyncSession = Depends(get_async_session)):
    
    hashed_password = pwd_context.hash(new_user.password)
    user_data = new_user.dict()
    user_data['hashed_password'] = hashed_password
    try: # отрабатывает если email уже зарегистрирован
        await create_user_db(
            user_data,
            session
        )
    except ValueError:
        raise HTTPException(
            status_code=409, detail='Email already registered')
    return {'status': '201'}


@router.post('/login')
async def login_user(
        get_user: LoginUser, 
        session: AsyncSession = Depends(get_async_session)):
    
    try: # отрабатывает если были введены неверные данные
        user = await get_user_password_db(get_user.email, session)
    except ValueError as ex:
        raise HTTPException(
            status_code=400, detail='Incorrect username or password')

    is_password_correct = pwd_context.verify(
        get_user.password, 
        user['hashed_password'])
    if not is_password_correct:
        raise HTTPException(
            status_code=400, detail='Incorrect username or password')
    
    refresh_token, access_token = create_tokens(user)

    await create_user_session_db(
        token=refresh_token,
        user_id=user['id'],
        session=session
    )
    return {'refresh_token': refresh_token, 
            'access_token': access_token, 
            'token_type': 'bearer'}


@router.post('/token')
async def update_token(
        token: RefreshToken, 
        session: AsyncSession = Depends(get_async_session)):
    
    token_data = verify_jwt_token(token.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    
    try: # отрабатывает если был введен неверный токен с верным ключем
        db_data = await get_data_db(token.refresh_token, session)
    except ValueError as ex: 
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    
    db_token = db_data['session']

    refresh_token, access_token = create_tokens(db_data['user'])
    await update_user_session_db(
        old_token=db_token['token'],
        new_token=refresh_token,
        session=session
    )
    return {'refresh_token': refresh_token, 
            'access_token': access_token, 
            'token_type': 'bearer'}





