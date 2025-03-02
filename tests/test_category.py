import pytest
from requests import Session

def login(session:Session):
    response = session.post('http://localhost:5000/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    
@pytest.fixture
def session():
    with Session() as session:
      login(session)
      yield session

def test_create_category(session:Session):    
    response = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Category',
        'category_type': 'expense'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'category' in data
    assert data['category']['name'] == 'Test Category'
    assert data['category']['type'] == 'expense'

def test_get_categories(session:Session):
    response = session.get('http://localhost:5000/api/category/')
    assert response.status_code == 200
    data = response.json()
    assert 'categories' in data
    assert isinstance(data['categories'], list)

def test_get_category_by_id(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Category',
        'category_type': 'expense'
    })
    category_id = response.json()['category']['id']
    
    response = session.get(f'http://localhost:5000/api/category/{category_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'category' in data
    assert data['category']['name'] == 'Test Category'

def test_update_category(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Category',
        'category_type': 'expense'
    })
    category_id = response.json()['category']['id']
    
    response = session.put(f'http://localhost:5000/api/category/{category_id}', json={
        'name': 'Updated Category',
        'category_type': 'income'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'category' in data
    assert data['category']['name'] == 'Updated Category'

def test_delete_category(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Category',
        'category_type': 'expense'
    })
    category_id = response.json()['category']['id']
    
    response = session.delete(f'http://localhost:5000/api/category/{category_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Category Deleted Successfully'

def test_enable_disable_category(session:Session):
    
    # Create test category
    response = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Category',
        'category_type': 'expense'
    })
    category_id = response.json()['category']['id']
    
    # Test disable
    response = session.put(f'http://localhost:5000/api/category/disable/{category_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Category Disable successfully'
    
    # Test enable
    response = session.put(f'http://localhost:5000/api/category/enable/{category_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'] == 'Category Enabled Successfully'

def test_get_categories_by_type(session:Session):
    
    # Create test categories
    response1 = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Expense',
        'category_type': 'expense'
    })
    response2 = session.post('http://localhost:5000/api/category/', json={
        'name': 'Test Income',
        'category_type': 'income'
    })
    
    response = session.get('http://localhost:5000/api/category/type/expense')
    assert response.status_code == 200
    data = response.json()
    assert len(data['categories']) >= 1
    assert all(cat['type'] == 'expense' for cat in data['categories'])