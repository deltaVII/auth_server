from datetime import datetime

from sqlalchemy import Table, Column
from sqlalchemy import MetaData
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy import Boolean


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
    Column('user_id', Integer, ForeignKey(user.c.id)),
    Column('token', String, nullable=False, primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('is_relevant', Boolean, default=True)
)