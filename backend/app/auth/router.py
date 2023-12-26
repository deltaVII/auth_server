import jwt

from fastapi import APIRouter, Depends
from fastapi import Cookie, Response
Response
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..database import get_session as get_db_session
from .jwt import create_tokens, verify_refresh_token
from .schemas import CreateUser, LoginUser
from .schemas import RefreshToken
from .db import get_session_with_user as get_data_db
from .db import get_user_password as get_user_password_db
from .db import create_user as create_user_db
from .db import get_user_session as get_user_session_db
from .db import update_user_session as update_user_session_db
from .db import create_user_session as create_user_session_db
from .db import delete_user_session as delete_user_session_db
from .main import verify_token


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
        session: AsyncSession = Depends(get_db_session)):
    
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
        response: Response,
        get_user: LoginUser, 
        session: AsyncSession = Depends(get_db_session)):
    
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

    response.set_cookie(key='session', value=refresh_token, 
                        httponly=True, max_age=60*60*24*30)
    return {
        'session': {
            'token': refresh_token,
            'type': 'cookie'}, 
        'access_token': {
            'token': access_token,
            'type': 'bearer'}
    }


@router.put('/token')
async def update_session(
        response: Response,
        session: str | None = Cookie(default=None),
        db_session: AsyncSession = Depends(get_db_session)):
    
    user_session = session # т.к. кука называется "session"
    if user_session is None:
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    try:
        token_data = verify_refresh_token(user_session)
    except jwt.ExpiredSignatureError:
        await delete_user_session_db(user_session, db_session)
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    
    
    try: # проверяет наличие сессии в бд
        _user_session = await get_user_session_db(user_session, db_session)
    except ValueError: 
        raise HTTPException(
            status_code=400, detail='Incorrect token')

    token_data['id'] = token_data['user_id'] 
    # так как в токене поле "user_id" а не "id"

    refresh_token, access_token = create_tokens(token_data)
    await update_user_session_db(
        old_token=user_session,
        new_token=refresh_token,
        session=db_session
    )

    response.set_cookie(key='session', value=refresh_token, 
                        httponly=True, max_age=60*60*24*30)
    return {
        'session': {
            'token': refresh_token,
            'type': 'cookie'}, 
        'access_token': {
            'token': access_token,
            'type': 'bearer'}
    }


@router.delete('/token')
async def logout(
        response: Response,
        session: str | None = Cookie(default=None),
        db_session: AsyncSession = Depends(get_db_session)):
    
    user_session = session # т.к. кука называется "session"
    if user_session is None:
        raise HTTPException(
            status_code=400, detail='Incorrect token')
    
    await delete_user_session_db(user_session, db_session)
    response.delete_cookie(key='session')

    return {'status': '200'}
    

