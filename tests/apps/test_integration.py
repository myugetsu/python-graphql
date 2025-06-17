"""
Integration tests for user workflows: registration, plan upgrade/downgrade, querying, and error cases.
Covers end-to-end flows using the GraphQL API.
"""
import pytest
from django.test import Client
from django.urls import reverse
import json
from django.core.management import call_command

@pytest.fixture(autouse=True)
def load_fixtures(db):
    from pathlib import Path
    fixture_dir = Path(__file__).parent.parent.parent / "fixtures"
    call_command('loaddata', str(fixture_dir / 'users.json'), verbosity=0)
    call_command('loaddata', str(fixture_dir / 'apps.json'), verbosity=0)

@pytest.mark.django_db
def test_user_registration_and_query():
    client = Client()
    query = '''
    query {
      allUsers {
        id
        username
        plan
        apps {
          edges {
            node {
              id
              active
            }
          }
        }
      }
    }
    '''
    response = client.post(
        "/graphql/",
        data=json.dumps({'query': query}),
        content_type='application/json',
    )
    if response.status_code != 200:
        print("GraphQL error response:", response.content)
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    users = data['data']['allUsers']
    assert isinstance(users, list)
    assert 'id' in users[0]
    assert 'username' in users[0]
    assert users[0]['plan'] in ('HOBBY', 'PRO')
    # Check apps connection structure
    assert 'apps' in users[0]
    assert 'edges' in users[0]['apps']
    assert 'node' in users[0]['apps']['edges'][0]
    assert 'id' in users[0]['apps']['edges'][0]['node']

@pytest.mark.django_db
def test_upgrade_and_downgrade_account():
    client = Client()
    user_query = '''
    query { allUsers { id username plan } }
    '''
    resp = client.post("/graphql/", data=json.dumps({'query': user_query}), content_type='application/json')
    user_id = resp.json()['data']['allUsers'][0]['id']

    # Upgrade
    upgrade_mut = '''
    mutation Upgrade($id: ID!) {
      upgradeAccount(userId: $id) { user { id plan } ok }
    }
    '''
    resp = client.post("/graphql/", data=json.dumps({'query': upgrade_mut, 'variables': {'id': user_id}}), content_type='application/json')
    if resp.status_code != 200:
        print("Upgrade mutation error response:", resp.content)
    assert resp.status_code == 200
    data = resp.json()
    assert data['data']['upgradeAccount']['user']['plan'] == 'PRO'
    assert data['data']['upgradeAccount']['ok'] is True

    # Downgrade
    downgrade_mut = '''
    mutation Downgrade($id: ID!) {
      downgradeAccount(userId: $id) { user { id plan } ok }
    }
    '''
    resp = client.post("/graphql/", data=json.dumps({'query': downgrade_mut, 'variables': {'id': user_id}}), content_type='application/json')
    if resp.status_code != 200:
        print("Downgrade mutation error response:", resp.content)
    assert resp.status_code == 200
    data = resp.json()
    assert data['data']['downgradeAccount']['user']['plan'] == 'HOBBY'
    assert data['data']['downgradeAccount']['ok'] is True

@pytest.mark.django_db
def test_invalid_id_errors():
    client = Client()
    upgrade_mut = '''
    mutation Upgrade($id: ID!) {
      upgradeAccount(userId: $id) { user { id plan } ok }
    }
    '''
    resp = client.post("/graphql/", data=json.dumps({'query': upgrade_mut, 'variables': {'id': 'invalid-id'}}), content_type='application/json')
    if resp.status_code != 200:
        print("Invalid ID mutation error response:", resp.content)
    assert resp.status_code == 200
    data = resp.json()
    # If upgradeAccount is None, an error was raised and returned in errors
    assert data['data']['upgradeAccount'] is None or (data['data']['upgradeAccount']['user'] is None or data['data']['upgradeAccount']['ok'] is False)
