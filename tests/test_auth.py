import pytest
import requests

@pytest.fixture
def session():
    with requests.Session() as session:
        yield session

def test_signup(session):
    response = session.post('http://localhost:5000/auth/signup', json={
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'fullName': 'New User'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'User registered successfully'

def test_login(session):
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Login successful'

def test_logout(session):
    # First, login
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    
    # Then, logout
    response = session.post('http://localhost:5000/auth/logout')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Logout successful'
