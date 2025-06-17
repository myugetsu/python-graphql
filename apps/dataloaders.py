import asyncio
from collections import defaultdict
from apps.models import User, DeployedApp
from asgiref.sync import sync_to_async


class UserLoader:
    def __init__(self):
        self._cache = {}

    def load_many(self, ids):
        users = User.objects.filter(id__in=ids)
        user_map = {user.id: user for user in users}
        return [user_map.get(i) for i in ids]


class AppLoader:
    def __init__(self):
        self._cache = {}

    def load_many(self, ids):
        apps = DeployedApp.objects.filter(id__in=ids)
        app_map = {app.id: app for app in apps}
        return [app_map.get(i) for i in ids]


class UserAppsLoader:
    def __init__(self):
        self._cache = defaultdict(list)

    def load_many(self, user_ids):
        apps = DeployedApp.objects.filter(owner_id__in=user_ids)
        for app in apps:
            self._cache[app.owner_id].append(app)
        return [self._cache[uid] for uid in user_ids]


class AsyncUserLoader:
    async def load_many(self, ids):
        users = await sync_to_async(list)(User.objects.filter(id__in=ids))
        user_map = {user.id: user for user in users}
        return [user_map.get(i) for i in ids]


class AsyncAppLoader:
    async def load_many(self, ids):
        apps = await sync_to_async(list)(DeployedApp.objects.filter(id__in=ids))
        app_map = {app.id: app for app in apps}
        return [app_map.get(i) for i in ids]


class AsyncUserAppsLoader:
    async def load_many(self, user_ids):
        apps = await sync_to_async(list)(
            DeployedApp.objects.filter(owner_id__in=user_ids)
        )
        cache = defaultdict(list)
        for app in apps:
            cache[app.owner_id].append(app)
        return [cache[uid] for uid in user_ids]
