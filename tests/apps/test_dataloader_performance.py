import pytest
import time
from apps.dataloaders import UserLoader, AppLoader, UserAppsLoader
from apps.models import User, DeployedApp


@pytest.mark.django_db
def test_dataloader_performance_many_users():
    users = [
        User.objects.create(username=f"perfuser{i}", plan="HOBBY") for i in range(100)
    ]
    loader = UserLoader()
    start = time.time()
    result = loader.load_many([u.id for u in users])
    elapsed = time.time() - start
    assert len(result) == 100
    assert elapsed < 1.0  # Should be fast for 100 users


@pytest.mark.django_db
def test_dataloader_performance_many_apps():
    u = User.objects.create(username="perfuser_apps", plan="PRO")
    apps = [DeployedApp.objects.create(owner=u) for _ in range(200)]
    loader = AppLoader()
    start = time.time()
    result = loader.load_many([a.id for a in apps])
    elapsed = time.time() - start
    assert len(result) == 200
    assert elapsed < 1.0  # Should be fast for 200 apps


@pytest.mark.django_db
def test_user_apps_loader_performance():
    users = [
        User.objects.create(username=f"perfuserapps{i}", plan="PRO") for i in range(10)
    ]
    for u in users:
        for _ in range(20):
            DeployedApp.objects.create(owner=u)
    loader = UserAppsLoader()
    start = time.time()
    result = loader.load_many([u.id for u in users])
    elapsed = time.time() - start
    assert all(len(apps) == 20 for apps in result)
    assert elapsed < 1.0  # Should be fast for 200 apps
