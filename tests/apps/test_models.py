import pytest
from django.core.exceptions import ValidationError
from apps.models import User, DeployedApp, generate_user_id, generate_app_id


@pytest.mark.django_db
def test_generate_user_id_format():
    user_id = generate_user_id()
    assert user_id.startswith("u_")
    assert len(user_id) > 3
    assert user_id[2:].isalnum()


@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create(username="alice_unique", plan="HOBBY")
    assert user.id.startswith("u_")
    assert user.username == "alice_unique"
    assert user.plan == "HOBBY"


@pytest.mark.django_db
def test_create_user_edge_case_empty_username():
    user = User(username="", plan="HOBBY")
    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_create_user_failure_invalid_plan():
    user = User(username="bob", plan="INVALID")
    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_generate_app_id_format():
    app_id = generate_app_id()
    assert app_id.startswith("app_")
    assert len(app_id) > 4
    assert app_id[4:].isalnum()


@pytest.mark.django_db
def test_create_deployed_app_success():
    user = User.objects.create(username="carol_unique", plan="PRO")
    app = DeployedApp.objects.create(owner=user)
    assert app.id.startswith("app_")
    assert app.active is True
    assert app.owner == user


@pytest.mark.django_db
def test_create_deployed_app_edge_case_no_owner():
    app = DeployedApp()
    with pytest.raises(ValidationError):
        app.full_clean()


@pytest.mark.django_db
def test_create_deployed_app_failure():
    # Failure: owner is required
    app = DeployedApp(active=False)
    with pytest.raises(ValidationError):
        app.full_clean()
