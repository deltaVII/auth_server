from datetime import datetime

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import MetaData
from sqlalchemy import UniqueConstraint
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

refresh_token = Table(
    'refresh_token',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey(user.c.id)),
    Column('token', String, nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('is_relevant', Boolean, default=True)
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

class Refresh_token(Base):
    __tablename__ = 'refresh_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_relevant = Column(Boolean, default=True)

    user = relationship(
        'User', 
        backref='Refresh_tokens', 
        lazy='selectin',
    )

