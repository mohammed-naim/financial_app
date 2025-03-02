import pytest
from requests import Session

def login(session: Session):
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    assert response.status_code == 200

@pytest.fixture
def session():
    with Session() as session:
        login(session)
        yield session

def test_change_language(session: Session):
    response = session.put('http://localhost:5000/api/settings/ar')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'تم تغيير اللغة بنجاح'
    
    response = session.put('http://localhost:5000/api/settings/en')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Language changed successfully'


