from fastapi.testclient import TestClient
import pytest

from app.main import app
from .conftest import client

authorization_token = ''

# потом допишу тесты


def test_register():
    response = client.post('/auth/register', json={
        'email': 'example@example.com',
        'username': 'example',
        'password': 'password'
    })
    assert response.status_code == 200

    response = client.post('/auth/register', json={
        'email': 'example@example.com',
        'username': 'example',
        'password': 'password'
    })
    assert response.status_code == 409

def test_login():
    response = client.post('/auth/login', json={
        'email': 'example@example.com',
        'password': 'password'
    })
    assert response.status_code == 200

    response = client.post('/auth/login', json={
        'email': 'example@example.com',
        'password': 'passsword'
    })
    assert response.status_code == 400

def test_token():
    response = client.put('/auth/token')
    assert response.status_code == 200

    global authorization_token
    authorization_token = ' '.join(['bearer', response.json()['access_token']['token']])

    response = client.delete('/auth/token')
    assert response.status_code == 200
    

def test_verify_authorization():
    response = client.get(
        '/test_auth/me', 
        headers={'Authorization': authorization_token})

    assert response.status_code == 200
    assert response.json()['username'] == 'example'
    assert response.json()['email'] == 'example@example.com'


def test_add_role():
    response = client.post(
        '/test_auth/role?role=test_role',         
        headers={'Authorization': authorization_token})
    
    assert response.status_code == 200

