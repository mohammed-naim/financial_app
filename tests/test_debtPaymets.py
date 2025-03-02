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

def test_create_debt_payment(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    response = session.post('http://localhost:5000/api/debt-payments/', json={
        'amount': 100.0,
        'account_id': 17,
        'debt_id': debt_id,
        'description': 'First payment'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'amount' in data
    assert data['amount'] == '100.0'

def test_get_debt_payments(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    response = session.get(f'http://localhost:5000/api/debt-payments/{debt_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'payments' in data
    assert isinstance(data['payments'], list)

def test_get_debt_payment_by_id(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    # Create test payment
    response = session.post('http://localhost:5000/api/debt-payments/', json={
        'amount': 100.0,
        'account_id': 17,
        'debt_id': debt_id,
        'description': 'First payment'
    })
    payment_id = response.json()['id']
    
    response = session.get(f'http://localhost:5000/api/debt-payments/{debt_id}?id={payment_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'amount' in data
    assert data['amount'] == '100.0'

def test_update_debt_payment(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    # Create test payment
    response = session.post('http://localhost:5000/api/debt-payments/', json={
        'amount': 100.0,
        'account_id': 17,
        'debt_id': debt_id,
        'description': 'First payment'
    })
    payment_id = response.json()['id']
    
    response = session.put(f'http://localhost:5000/api/debt-payments/{payment_id}', json={
        'amount': 150.0,
        'account_id':17,
        'description': 'Updated payment'
    })
    data = response.json()
    assert 'error' not in data
    assert response.status_code == 200
    assert 'amount' in data
    assert data['amount'] == '150.0'

def test_delete_debt_payment(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    # Create test payment
    response = session.post('http://localhost:5000/api/debt-payments/', json={
        'amount': 100.0,
        'account_id': 17,
        'debt_id': debt_id,
        'description': 'First payment'
    })
    payment_id = response.json()['id']
    
    response = session.delete(f'http://localhost:5000/api/debt-payments/{payment_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Payment deleted successfully'