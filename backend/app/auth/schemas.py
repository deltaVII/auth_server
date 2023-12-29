from pydantic import BaseModel
from pydantic import EmailStr



class CreateUser(BaseModel):
    password: str
    username: str
    email: EmailStr

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class AccessToken(BaseModel):
    access_token: str