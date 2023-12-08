from pydantic import BaseModel
from pydantic import EmailStr



class CreateUser(BaseModel):
    password: str
    username: str
    email: EmailStr

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class RefreshToken(BaseModel):
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str