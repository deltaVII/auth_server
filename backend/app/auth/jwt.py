import jwt
from datetime import datetime
from datetime import timedelta

from config import SECRET_KEY

ALGORITHM = 'HS256'
EXPIRATION_TIME = {'access_token': timedelta(minutes=30), 'refresh_token': timedelta(days=30)}

def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME[data['type']]
    data.update({'exp': expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError as ex:
        return None
    
def create_tokens(user: dict) -> list[dict]:
    new_refresh_token = create_jwt_token({
        'iser_id': user['id'],
        'username': user['username'],                   
        'email': user['email'],
        'type': 'refresh_token',
    })
    new_access_token = create_jwt_token({
        'iser_id': user['id'],
        'username': user['username'],                   
        'email': user['email'],
        'type': 'access_token',
    })
    return new_refresh_token, new_access_token
