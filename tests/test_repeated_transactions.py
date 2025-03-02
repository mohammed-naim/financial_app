import pytest
from requests import Session

def login(session: Session):
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    assert response.status_code == 200

@pytest.fixture
def session(scope='session'):
    with Session() as session:
        login(session)
        yield session

def test_create_repeated_transaction(session: Session):
    response = session.post('http://localhost:5000/api/repeated_transactions/', json={
        'amount': 100.0,
        'account_id': 17,
        'category_id': 31,
        'period': 1,
        'start_date': '2025-03-01',
        'end_date': '2033-12-01',
        'description': 'Monthly subscription'
    })
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 201
    assert 'message' in data
    assert data['message'] == 'Repeated transaction created successfully'

def test_get_repeated_transactions(session: Session):
    response = session.get('http://localhost:5000/api/repeated_transactions/')
    assert response.status_code == 200
    data = response.json()
    assert 'repeated_transactions' in data
    assert isinstance(data['repeated_transactions'], list)

def test_get_repeated_transaction_by_id(session: Session):
    # Create test repeated transaction
    response = session.post('http://localhost:5000/api/repeated_transactions/', json={
        'amount': 100.0,
        'account_id': 17,
        'category_id': 31,
        'period': 30,
        'start_date': '2025-03-01',
        'end_date': '2026-12-01',
        'description': 'Monthly subscription'
    })
    assert 'error' not in response.json()
    repeated_transaction_id = response.json()['repeated_transaction']['id']
    
    response = session.get(f'http://localhost:5000/api/repeated_transactions/{repeated_transaction_id}')
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'repeated_transaction' in data
    assert data['repeated_transaction']['description'] == 'Monthly subscription'

def test_update_repeated_transaction(session: Session):
    # Create test repeated transaction
    response = session.post('http://localhost:5000/api/repeated_transactions/', json={
        'amount': 100.0,
        'account_id': 17,
        'category_id': 31,
        'period': 30,
        'start_date': '2025-03-01',
        'end_date': '2026-03-01',
        'description': 'Monthly subscription'
    })
    assert 'error' not in response.json()
    repeated_transaction_id = response.json()['repeated_transaction']['id']
    
    response = session.put(f'http://localhost:5000/api/repeated_transactions/{repeated_transaction_id}', json={
        'amount': 160.0,
        'account_id': 17,
        'category_id': 31,
        'period': 30,
        'start_date': '2025-03-01',
        'end_date': '2026-03-01',
        'description': 'Updated Monthly subscription'
    })
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'message' in data
    assert data['message'] == 'Repeated transaction updated successfully'

def test_delete_repeated_transaction(session: Session):
    # Create test repeated transaction
    response = session.post('http://localhost:5000/api/repeated_transactions/', json={
        'amount': 100.0,
        'account_id': 17,
        'category_id': 31,
        'period': 30,
        'start_date': '2025-03-01',
        'end_date': '2026-03-01',
        'description': 'Monthly subscription'
    })
    assert 'error' not in response.json()
    repeated_transaction_id = response.json()['repeated_transaction']['id']
    
    response = session.delete(f'http://localhost:5000/api/repeated_transactions/{repeated_transaction_id}')
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'message' in data
    assert data['message'] == 'Repeated transaction deleted successfully'