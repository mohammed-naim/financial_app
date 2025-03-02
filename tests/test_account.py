import pytest
import requests

def login(session):
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    
@pytest.fixture
def session():
    with requests.Session() as session:
      login(session)
      yield session



def test_create_account(session):
    
    
    response = session.post('http://localhost:5000/api/account/', json={
        'name': 'Test Account',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'account' in data
    assert data['account']['name'] == 'Test Account'
    assert float(data['account']['balance']) == 1000.0
    assert data['account']['currency'] == 'ILS'

def test_get_accounts(session):
    
    response = session.get('http://localhost:5000/api/account/')
    assert response.status_code == 200
    data = response.json()
    assert 'accounts' in data
    assert isinstance(data['accounts'], list)

def test_get_account_by_id(session):
    
    
    # Create test account
    response = session.post('http://localhost:5000/api/account/', json={
        'name': 'Test Account',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    account_id = response.json()['account']['id']
    
    response = session.get(f'http://localhost:5000/api/account/{account_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'account' in data
    assert data['account']['name'] == 'Test Account'
    assert float(data['account']['balance']) == 1000.0
    assert data['account']['currency'] == 'ILS'

def test_update_account(session):
    
    
    # Create test account
    response = session.post('http://localhost:5000/api/account/', json={
        'name': 'Test Account',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    account_id = response.json()['account']['id']
    
    response = session.put(f'http://localhost:5000/api/account/{account_id}', json={
        'name': 'Updated Account',
        'balance': 2000.0,
        'currency': 'ILS'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'account' in data
    assert data['account']['name'] == 'Updated Account'
    assert float(data['account']['balance']) == 2000.0
    assert data['account']['currency'] == 'ILS'

def test_delete_account(session):
    
    
    # Create test account
    response = session.post('http://localhost:5000/api/account/', json={
        'name': 'Test Account',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    account_id = response.json()['account']['id']
    
    response = session.delete(f'http://localhost:5000/api/account/{account_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Account Deleted Successfully'

def test_enable_disable_account(session):
    
    
    # Create test account
    response = session.post('http://localhost:5000/api/account/', json={
        'name': 'Test Account',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    account_id = response.json()['account']['id']
    
    # Test disable
    response = session.put(f'http://localhost:5000/api/account/disable/{account_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Account Disabled Successfully'
    
    # Test enable
    response = session.put(f'http://localhost:5000/api/account/enable/{account_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Account Enabled Successfully'

def test_transfer_between_accounts(session):
    
    
    # Create two test accounts
    response1 = session.post('http://localhost:5000/api/account/', json={
        'name': 'Account 1',
        'balance': 1000.0,
        'currency': 'ILS'
    })
    account1_id = response1.json()['account']['id']
    
    response2 = session.post('http://localhost:5000/api/account/', json={
        'name': 'Account 2',
        'balance': 0.0,
        'currency': 'ILS'
    })
    account2_id = response2.json()['account']['id']
    
    response = session.post('http://localhost:5000/api/account/transfer', json={
        'from_account_id': account1_id,
        'to_account_id': account2_id,
        'amount': 500.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Transfer completed successfully'
    
    # Verify balances
    response1 = session.get(f'http://localhost:5000/api/account/{account1_id}')
    data1 = response1.json()
    assert float(data1['account']['balance']) == 500.0
    
    response2 = session.get(f'http://localhost:5000/api/account/{account2_id}')
    data2 = response2.json()
    assert float(data2['account']['balance']) == 500.0