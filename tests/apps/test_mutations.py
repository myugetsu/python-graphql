import pytest
from graphene.test import Client
from apps.schema import schema
from apps.models import User


@pytest.mark.django_db
def test_upgrade_account_mutation():
    user = User.objects.create(username="mutuser1", plan="HOBBY")
    client = Client(schema)
    # Get relay global id
    query = "{ allUsers { id username plan } }"
    result = client.execute(query)
    user_id = result["data"]["allUsers"][-1]["id"]
    mutation = f"""mutation {{ upgradeAccount(userId: "{user_id}") {{ ok user {{ id plan }} }} }}"""
    response = client.execute(mutation)
    assert response["data"]["upgradeAccount"]["ok"] is True
    assert response["data"]["upgradeAccount"]["user"]["plan"] == "PRO"


@pytest.mark.django_db
def test_downgrade_account_mutation():
    user = User.objects.create(username="mutuser2", plan="PRO")
    client = Client(schema)
    query = "{ allUsers { id username plan } }"
    result = client.execute(query)
    user_id = result["data"]["allUsers"][-1]["id"]
    mutation = f"""mutation {{ downgradeAccount(userId: "{user_id}") {{ ok user {{ id plan }} }} }}"""
    response = client.execute(mutation)
    assert response["data"]["downgradeAccount"]["ok"] is True
    assert response["data"]["downgradeAccount"]["user"]["plan"] == "HOBBY"
