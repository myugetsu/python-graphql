import pytest
from graphene.test import Client
from apps.schema import schema
from apps.models import User

@pytest.mark.django_db
def test_upgrade_account_invalid_id():
    client = Client(schema)
    mutation = '''mutation { upgradeAccount(userId: "invalid") { ok user { id plan } } }'''
    response = client.execute(mutation)
    assert 'errors' in response
    assert 'Invalid global ID format' in response['errors'][0]['message']

@pytest.mark.django_db
def test_upgrade_account_user_not_found():
    client = Client(schema)
    # Valid relay id, but user does not exist
    from base64 import b64encode
    fake_id = b64encode(b'UserNode:u_fakeid').decode()
    mutation = f'''mutation {{ upgradeAccount(userId: "{fake_id}") {{ ok user {{ id plan }} }} }}'''
    response = client.execute(mutation)
    assert 'errors' in response
    assert 'User not found' in response['errors'][0]['message']

@pytest.mark.django_db
def test_downgrade_account_invalid_id():
    client = Client(schema)
    mutation = '''mutation { downgradeAccount(userId: "invalid") { ok user { id plan } } }'''
    response = client.execute(mutation)
    assert 'errors' in response
    assert 'Invalid global ID format' in response['errors'][0]['message']

@pytest.mark.django_db
def test_downgrade_account_user_not_found():
    client = Client(schema)
    from base64 import b64encode
    fake_id = b64encode(b'UserNode:u_fakeid').decode()
    mutation = f'''mutation {{ downgradeAccount(userId: "{fake_id}") {{ ok user {{ id plan }} }} }}'''
    response = client.execute(mutation)
    assert 'errors' in response
    assert 'User not found' in response['errors'][0]['message']
