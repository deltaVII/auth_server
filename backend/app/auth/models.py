from datetime import datetime

from sqlalchemy import Table, Column
from sqlalchemy import MetaData
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy import Boolean

from sqlalchemy.orm import relationship

from ..database import Base


metadata = MetaData()

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String, nullable=False, unique=True),
    Column('username', String, nullable=False, unique=True),
    Column('hashed_password', String, nullable=False),
)

role = Table(
    'role',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('role', String, nullable=False),
)

user_role = Table(
    'user_role',
    metadata,
    Column('user_id', Integer(), ForeignKey("user.id"), primary_key=True),
    Column('role_id', Integer(), ForeignKey("role.id"), primary_key=True)
)

user_session = Table(
    'user_session',
    metadata,
    Column('user_id', Integer, ForeignKey(user.c.id)),
    Column('token', String, nullable=False, primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('update_at', TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow),
)


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String(length=1024), nullable=False)

    roles = relationship(
        'Role',
        secondary="user_role",
        back_populates="users",
    )

class Role(Base):
    __tablename__ = 'role'
    
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)

    users = relationship(
        'User',
        secondary="user_role",
        back_populates="roles",
    )

class UserRole(Base):
    __tablename__ = 'user_role'

    user_id = Column(Integer(), ForeignKey("user.id"), primary_key=True)
    role_id = Column(Integer(), ForeignKey("role.id"), primary_key=True)

class UserSession(Base):
    __tablename__ = 'user_session'

    token = Column(String, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    update_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship(
        'User', 
        backref='Refresh_tokens', 
        lazy='selectin',
    )

