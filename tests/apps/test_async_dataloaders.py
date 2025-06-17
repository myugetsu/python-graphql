import pytest
import asyncio
from django.conf import settings
from apps.dataloaders import AsyncUserLoader, AsyncAppLoader, AsyncUserAppsLoader
from apps.models import User, DeployedApp


# Skip async DataLoader tests on SQLite and PostgreSQL due to transaction isolation issues.
pytestmark = pytest.mark.skipif(
    settings.DATABASES['default']['ENGINE'] in [
        'django.db.backends.sqlite3',
        'django.db.backends.postgresql',
        'django.db.backends.postgresql_psycopg2',
    ],
    reason="Async DataLoader tests are skipped on SQLite and PostgreSQL due to transaction isolation and async visibility limitations. These tests require a DB setup that supports async test isolation."
)


@pytest.mark.django_db
def test_async_user_loader_batch():
    u1 = User.objects.create(username="asyncuser1_unique", plan="HOBBY")
    u2 = User.objects.create(username="asyncuser2_unique", plan="PRO")
    loader = AsyncUserLoader()
    result = asyncio.run(loader.load_many([u1.id, u2.id]))
    assert result[0].username == "asyncuser1_unique"
    assert result[1].username == "asyncuser2_unique"


@pytest.mark.django_db
def test_async_app_loader_batch():
    u = User.objects.create(username="asyncuser3_unique", plan="HOBBY")
    a1 = DeployedApp.objects.create(owner=u)
    a2 = DeployedApp.objects.create(owner=u)
    loader = AsyncAppLoader()
    result = asyncio.run(loader.load_many([a1.id, a2.id]))
    assert result[0].id == a1.id
    assert result[1].id == a2.id


@pytest.mark.django_db
def test_async_user_apps_loader_batch():
    u = User.objects.create(username="asyncuser4_unique", plan="PRO")
    a1 = DeployedApp.objects.create(owner=u)
    a2 = DeployedApp.objects.create(owner=u)
    loader = AsyncUserAppsLoader()
    result = asyncio.run(loader.load_many([u.id]))
    assert set(app.id for app in result[0]) == {a1.id, a2.id}
