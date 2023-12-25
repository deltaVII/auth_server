from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from .models import User
from .models import UserSession
from .models import UserRole, Role


async def get_user(
        user_email: str, 
        session: AsyncSession) -> dict:
    
    user_data = await get_user_password(user_email, session)
    user_data.pop('hashed_password')
    return user_data


async def get_user_password(
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


async def get_user_roles(
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


async def create_user(
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

async def get_session_with_user(
        token: str, 
        session: AsyncSession) -> dict:
    
    query = select(UserSession) \
        .join(User, User.id==UserSession.user_id) \
        .filter(UserSession.token == token)
    db_token = await session.execute(query)
    db_token = db_token.scalar()
    if db_token is None:
        raise ValueError(f'token:{token} is not found')

    data = {
        'session': {
            'user_id': db_token.user_id,
            'token': db_token.token,
            'created_at': db_token.created_at,
            'update_at': db_token.update_at,
        },
        'user': {
            'id': db_token.user.id,
            'username': db_token.user.username, 
            'email': db_token.user.email, 
        }
    }
    return data


async def update_user_session(
        old_token: str, 
        new_token: str, 
        session: AsyncSession) -> None:

    query_update = update(UserSession) \
        .where(UserSession.token == old_token) \
        .values(token=new_token)
    await session.execute(query_update)

    await session.commit()

async def create_user_session(
        token: str, 
        user_id: int, 
        session: AsyncSession) -> None:

    new_token = UserSession(
        token=token,
        user_id=user_id,
    )
    session.add(new_token)

    await session.commit()


async def add_user_role(
        user_data: str, 
        role: str, 
        session: AsyncSession) -> None:
    
    query = select(Role) \
        .where(Role.role == role)
    role_ = await session.execute(query)
    role_ = role_.scalar()

    if role_ is None:
        raise ValueError(f'role:{role} is not found')

    user_role = UserRole(
        user_id=user_data['id'],
        role_id=role_.id
    )
    session.add(user_role)
    await session.commit()
    print(role_, user_role)


async def add_role(
        role: str,
        session: AsyncSession) -> None:
    
    new_role = Role(role=role)
    
    session.add(new_role)
    await session.commit()
    