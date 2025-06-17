import pytest
from apps.dataloaders import UserLoader, AppLoader, UserAppsLoader
from apps.models import User, DeployedApp


@pytest.mark.django_db
def test_user_loader_batch():
    u1 = User.objects.create(username="dluser1", plan="HOBBY")
    u2 = User.objects.create(username="dluser2", plan="PRO")
    loader = UserLoader()
    result = loader.load_many([u1.id, u2.id])
    assert result[0].username == "dluser1"
    assert result[1].username == "dluser2"


@pytest.mark.django_db
def test_app_loader_batch():
    u = User.objects.create(username="dluser3", plan="HOBBY")
    a1 = DeployedApp.objects.create(owner=u)
    a2 = DeployedApp.objects.create(owner=u)
    loader = AppLoader()
    result = loader.load_many([a1.id, a2.id])
    assert result[0].id == a1.id
    assert result[1].id == a2.id


@pytest.mark.django_db
def test_user_apps_loader_batch():
    u = User.objects.create(username="dluser4", plan="PRO")
    a1 = DeployedApp.objects.create(owner=u)
    a2 = DeployedApp.objects.create(owner=u)
    loader = UserAppsLoader()
    result = loader.load_many([u.id])
    assert set(app.id for app in result[0]) == {a1.id, a2.id}
