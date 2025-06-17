import pytest
from graphene.test import Client
from apps.schema import schema
from apps.models import User, DeployedApp


@pytest.mark.django_db
def test_node_query_user():
    user = User.objects.create(username="testnodeuser", plan="HOBBY")
    client = Client(schema)
    global_id = f"VXNlck5vZGU6{user.id}"  # This is not the real encoding, but graphene will encode automatically
    # Get the real global id from graphene
    query = """{ allUsers { id username } }"""
    result = client.execute(query)
    user_id = result["data"]["allUsers"][-1]["id"]
    node_query = (
        f"""{{ node(id: "{user_id}") {{ ... on UserNode {{ id username plan }} }} }}"""
    )
    node_result = client.execute(node_query)
    assert node_result["data"]["node"]["username"] == "testnodeuser"
    assert node_result["data"]["node"]["plan"] == "HOBBY"


@pytest.mark.django_db
def test_node_query_app():
    user = User.objects.create(username="testnodeappuser", plan="PRO")
    app = DeployedApp.objects.create(owner=user)
    client = Client(schema)
    query = """{ allApps { id active owner { id username } } }"""
    result = client.execute(query)
    app_id = result["data"]["allApps"][-1]["id"]
    node_query = f"""{{ node(id: "{app_id}") {{ ... on DeployedAppNode {{ id active owner {{ username }} }} }} }}"""
    node_result = client.execute(node_query)
    assert node_result["data"]["node"]["owner"]["username"] == "testnodeappuser"
