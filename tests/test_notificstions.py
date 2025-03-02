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

def test_get_notifications(session: Session):
    response = session.get('http://localhost:5000/api/notification/')
    assert response.status_code == 200
    data = response.json()
    assert 'notifications' in data
    assert isinstance(data['notifications'], list)

def test_update_notification(session: Session):
    # Create test notification
    response = session.get('http://localhost:5000/api/notification/')
    notifications = response.json()['notifications']
    notification_id = notifications[0]['id']
    
    response = session.put(f'http://localhost:5000/api/notification/{notification_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Notification updated successfully'