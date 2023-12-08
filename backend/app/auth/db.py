from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from .models import User
from .models import Refresh_token
from .models import UserRole, Role


async def get_user_db(
        user_email: str, 
        session: AsyncSession) -> dict:
    
    user_data = await get_user_password_db(user_email, session)
    user_data.pop('hashed_password')
    return user_data


async def get_user_password_db(
        user_email: str, 
        session: AsyncSession) -> dict:
    
    query = select(User).where(User.email == user_email)
    user = await session.execute(query)
    user = user.scalar()
    
    if user is None:
        raise ValueError(f'user with the email:{user_email} was not found')

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'hashed_password': user.hashed_password
    }
    return data


async def get_user_roles_db(
        user_email: str, 
        session: AsyncSession) -> dict:
    
    query = select(User) \
        .where(User.email == user_email) \
        .options(joinedload(User.roles))
    user = await session.execute(query)
    user = user.scalar()

    if user is None:
        raise ValueError(f'user with the email:{user_email} is not found')
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'hashed_password': user.hashed_password,
        'roles': [role.role for role in user.roles]
    }
    return data


async def create_user_db(
        user_data: dict, 
        session: AsyncSession) -> None:
    

    user = User(        
        username=user_data['username'], 
        email=user_data['email'], 
        hashed_password=user_data['hashed_password']
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise ValueError(f'Email:{user_data["email"]} already registered')

async def get_data_db(
        token: str, 
        session: AsyncSession) -> dict:
    
    query = select(Refresh_token) \
        .join(User, User.id==Refresh_token.user_id) \
        .filter(Refresh_token.token == token)
    db_token = await session.execute(query)
    db_token = db_token.scalar()
    if db_token is None:
        raise ValueError(f'token:{token} is not found')

    data = {
        'token': {
            'user_id': db_token.user_id,
            'token': db_token.token,
            'created_at': db_token.created_at,
            'is_relevant': db_token.is_relevant,
        },
        'user': {
            'id': db_token.user.id,
            'username': db_token.user.username, 
            'email': db_token.user.email, 
        }
    }
    return data


async def save_tokens_db(
        old_token: str, 
        new_token: str, 
        user_id: int, 
        session: AsyncSession) -> None:

    new_token_ = Refresh_token(
        user_id=user_id,
        token=new_token
    )
    session.add(new_token_)
    if old_token is not None:
        query_update = update(Refresh_token) \
            .where(Refresh_token.token == old_token) \
            .values(is_relevant=False)
        await session.execute(query_update)

    await session.commit()


async def add_user_role(
        user_data: str, 
        role: str, 
        session: AsyncSession) -> None:
    
    query = select(Role) \
        .where(Role.role == role)
    role_ = await session.execute(query)
    role_ = role_.scalar()

    user_role = UserRole(
        user_id=user_data['id'],
        role_id=role_.id
    )
    session.add(user_role)
    await session.commit()


async def add_role(
        role: str,
        session: AsyncSession) -> None:
    
    new_role = Role(role=role)
    
    session.add(new_role)
    await session.commit()
    