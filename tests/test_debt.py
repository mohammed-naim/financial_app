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

def test_create_debt(session: Session):
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    assert response.status_code == 201
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Debt added successfully'

def test_get_debts(session: Session):
    response = session.get('http://localhost:5000/api/debts/')
    assert response.status_code == 200
    data = response.json()
    assert 'debts' in data
    assert isinstance(data['debts'], list)

def test_get_debt_by_id(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    response = session.get(f'http://localhost:5000/api/debts/?id={debt_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'person_name' in data
    assert data['person_name'] == 'John Doe'

def test_update_debt(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    response = session.put(f'http://localhost:5000/api/debts/{debt_id}', json={
        'person_name': 'Jane Doe',
        'type': 'debtor',
        'amount': 700.0,
        'description': 'Loan from Jane',
        'account_id': 17
    })
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Debt updated successfully'

def test_delete_debt(session: Session):
    # Create test debt
    response = session.post('http://localhost:5000/api/debts/', json={
        'person_name': 'John Doe',
        'type': 'creditor',
        'amount': 500.0,
        'description': 'Loan to John',
        'account_id': 17
    })
    debt_id = response.json()['debt']['id']
    
    response = session.delete(f'http://localhost:5000/api/debts/{debt_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Debt deleted successfully'