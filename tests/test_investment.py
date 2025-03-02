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

def test_create_investment(session: Session):
    response = session.post('http://localhost:5000/api/investment/', json={
        'account_id': 17,
        'currency': 'USD',
        'amount_invested': 1000.0,
        'purchase_price': 1000.0,
        'reference_currency': 'ILS',
        'description': 'Test Investment'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Investment added successfully'

def test_get_investments(session: Session):
    response = session.get('http://localhost:5000/api/investment/')
    assert response.status_code == 200
    data = response.json()
    assert 'investments' in data
    assert isinstance(data['investments'], list)

def test_get_investment_by_id(session: Session):
    # Create test investment
    response = session.post('http://localhost:5000/api/investment/', json={
        'account_id': 17,
        'currency': 'USD',
        'amount_invested': 1000.0,
        'purchase_price': 1000.0,
        'reference_currency': 'ILS',
        'description': 'Test Investment'
    })
    investment_id = response.json()['investment']['id']
    
    response = session.get(f'http://localhost:5000/api/investment/?id={investment_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'account_id' in data
    assert data['account_id'] == 17

def test_update_investment(session: Session):
    # Create test investment
    response = session.post('http://localhost:5000/api/investment/', json={
        'account_id': 17,
        'currency': 'USD',
        'amount_invested': 1000.0,
        'purchase_price': 1000.0,
        'reference_currency': 'ILS',
        'description': 'Test Investment'
    })
    investment_id = response.json()['investment']['id']
    
    response = session.put(f'http://localhost:5000/api/investment/{investment_id}', json={
        'currency': 'USD',
        'account_id': 17,
        'amount_invested': 1500.0,
        'purchase_price': 1500.0,
        'reference_currency': 'ILS',
        'description': 'Updated Investment'
    })
    assert 'error' not in response.text
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'message' in data
    assert data['message'] == 'Investment updated successfully'

def test_delete_investment(session: Session):
    # Create test investment
    response = session.post('http://localhost:5000/api/investment/', json={
        'account_id': 17,
        'currency': 'USD',
        'amount_invested': 1000.0,
        'purchase_price': 1000.0,
        'reference_currency': 'ILS',
        'description': 'Test Investment'
    })
    investment_id = response.json()['investment']['id']
    
    response = session.delete(f'http://localhost:5000/api/investment/{investment_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Investment deleted successfully'

def test_sell_investment(session: Session):
    # Create test investment
    response = session.post('http://localhost:5000/api/investment/', json={
        'account_id': 17,
        'currency': 'USD',
        'amount_invested': 1000.0,
        'purchase_price': 1000.0,
        'reference_currency': 'ILS',
        'description': 'Test Investment'
    })
    investment_id = response.json()['investment']['id']
    
    response = session.put(f'http://localhost:5000/api/investment/sell/{investment_id}', json={
        'sell_price': 1200.0
    })
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Investment updated successfully'

def test_get_exchange_rates(session: Session):
    response = session.get('http://localhost:5000/api/investment/exchange_rates')
    assert response.status_code == 200
    data = response.json()
    assert 'exchange_rates' in data