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

def test_get_overview(session: Session):
    response = session.get('http://localhost:5000/api/dashboard/overview')
    assert response.status_code == 200
    data = response.json()
    assert 'income' in data
    assert 'expenses' in data
    assert 'enabled_accounts_balance' in data
    assert 'disabled_accounts_balance' in data
    assert 'total_creditor_debts' in data
    assert 'total_debtor_debts' in data
    assert 'total_invested' in data
    assert 'total_profit' in data

def test_get_cash_flow(session: Session):
    response = session.get('http://localhost:5000/api/dashboard/cash-flow')
    assert response.status_code == 200
    data = response.json()
    assert 'current_period' in data
    assert 'income' in data['current_period']
    assert 'expenses' in data['current_period']

def test_get_detailed_cash_flow(session: Session):
    response = session.get('http://localhost:5000/api/dashboard/cash-flow/detailed?start_date=2023-01-01&end_date=2023-12-31&interval=month')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert 'start_date' in data[0]
    assert 'end_date' in data[0]
    assert 'income' in data[0]
    assert 'expenses' in data[0]

def test_get_category_summary(session: Session):
    response = session.get('http://localhost:5000/api/dashboard/category-summary')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)