import pytest
from requests import Session
base_url = ''
def login(session:Session):
    response = session.post(f'http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    
@pytest.fixture
def session():
    with Session() as session:
      login(session)
      yield session

def test_add_transaction(session:Session):
  response = session.post(f'http://localhost:5000/api/transaction/',json={
    'amount': 50,
    'account_id' : 17,
    'category_id' : 31,
    'transaction_date' : '2025-2-24',
    'description': "some description"
  })
  assert "error" not in response.text
  assert response.status_code == 201
  data = response.json()
  assert 'message' in data
  assert data['message'] == 'Transaction created successfully'
  assert 'transaction' in data
  assert data['transaction']['account_id'] 
  assert data['transaction']['category_id'] 
  assert data['transaction']['description'] 
  assert data['transaction']['date'] 
  assert data['transaction']['status'] 
  assert data['transaction']['category_name'] 
  assert data['transaction']['type'] 
  assert data['transaction']['account_name'] 
  
def test_get_transactions(session:Session):
    response = session.get('http://localhost:5000/api/transaction/')
    assert response.status_code == 200
    data = response.json()
    assert 'error' not in data
    assert 'transactions' in data
    assert isinstance(data['transactions'], list)
    assert 'totalPages' in data
    assert 'currentPage' in data
    assert 'totalItems' in data

def test_update_transaction(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/transaction/', json={
        'amount': 50,
        'account_id' : 17,
        'category_id' : 31,
        'transaction_date' : '2025-2-24',
        'description': "some description"
    })
    transaction_id = response.json()['transaction']['id']
    
    response = session.put(f'http://localhost:5000/api/transaction/{transaction_id}', json={
        'amount': 30,
        'account_id' : 17,
        'category_id' : 31,
    })
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'transaction' in data
    assert float(data['transaction']['amount']) == 30.0
    

def test_delete_transaction(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/transaction/', json={
        'amount': 51,
        'account_id' : 17,
        'category_id' : 31,
        'transaction_date' : '2025-2-24',
        'description': "some description"
    })
    transaction_id = response.json()['transaction']['id']
    
    response = session.delete(f'http://localhost:5000/api/transaction/{transaction_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Transaction deleted successfully'
