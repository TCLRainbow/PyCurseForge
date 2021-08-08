from typing import Iterable

import aiohttp

import objects

__base_url__ = 'https://addons-ecs.forgesvc.net/api/v2/'


class CurseForgeException(Exception):

    def __init__(self, r):
        self.response: aiohttp.ClientResponse = r


def _default_error(c):
    raise c


class CurseForge:

    def __init__(self, session: aiohttp.ClientSession = aiohttp.ClientSession()):
        self.__session = session
        self.__error = _default_error

    def error(self, func):
        self.__error = func

    async def __get(self, path: str, t, serialise_date: bool = True):
        async with self.__session.get(__base_url__ + path) as r:
            if r.ok:
                return t(await r.json(), serialise_date, self)
            else:
                self.__error(CurseForgeException(r))

    async def __get_text(self, path: str, params=None):
        async with self.__session.get(__base_url__ + path, params=params) as r:
            if r.ok:
                return await r.text()
            else:
                self.__error(CurseForgeException(r))

    async def __multi_get(self, path: str, t, params=None, serialise_date: bool = True):
        async with self.__session.get(__base_url__ + path, params=params) as r:
            if r.ok:
                return map(lambda e: t(e, serialise_date, self), await r.json())
            else:
                self.__error(CurseForgeException(r))

    async def __post_json(self, path: str, json=None):
        async with self.__session.post(__base_url__ + path, json=json) as r:
            if r.ok:
                return await r.json()
            else:
                self.__error(CurseForgeException(r))

    async def __post(self, path: str, t, json=None, serialise_date: bool = True):
        json = await self.__post_json(path, json)
        if json:
            return t(json, serialise_date, self)

    async def __multi_post(self, path: str, t, json=None, serialise_date: bool = True):
        async with self.__session.post(__base_url__ + path, json=json) as r:
            if r.ok:
                return map(lambda e: t(e, serialise_date, self), await r.json())
            else:
                self.__error(CurseForgeException(r))

    async def get_addon(self, addon_id, serialise_date: bool = True) -> objects.Addon:
        return await self.__get(f'addon/{addon_id}', objects.Addon, serialise_date)

    async def get_addons(self, addon_ids: Iterable, serialise_date: bool = True) -> Iterable[objects.Addon]:
        return await self.__multi_post('addon', objects.Addon, addon_ids, serialise_date)

    async def search_addons(self, game_id, game_ver: str = None, category_id=0, index: int = 0,
                            name: str = None, section_id=None, sort: bool = 0,
                            serialise_date: bool = True) -> Iterable[objects.Addon]:
        param = {'gameId': game_id}
        if game_ver:
            param['gameVersion'] = game_ver
        if category_id:
            param['categoryId'] = category_id
        if index:
            param['index'] = index
        if name:
            param['searchFilter'] = name
        if section_id:
            param['sectionId'] = section_id
        if sort:
            param['sort'] = int(sort)
        return await self.__multi_get('addon/search', objects.Addon, param, serialise_date)

    async def get_featured_addons(self, game_id: int, addon_ids: Iterable[int] = (), featured_count: int = 1,
                                  popular_count: int = 1, updated_count: int = 1,
                                  serialise_date: bool = True) -> Iterable[objects.Addon]:
        j = await self.__post_json('addon/featured',
                                   {'gameId': game_id, 'addonsIds': addon_ids, 'featuredCount': featured_count,
                                    'popularCount': popular_count, 'updatedCount': updated_count})
        if j and j['Featured']:
            return map(lambda a: objects.Addon(a, serialise_date, self), j['Featured'])

    async def get_addon_description(self, addon_id) -> str:
        return await self.__get_text(f'addon/{addon_id}/description')

    async def get_addon_files(self, addon_id, serialise_date: bool = True) -> Iterable[objects.AddonFile]:
        return await self.__multi_get(f'addon/{addon_id}/files', objects.AddonFile, serialise_date=serialise_date)

    async def get_addon_file(self, addon_id, file_id, serialise_date: bool = True) -> objects.AddonFile:
        return await self.__get(f'addon/{addon_id}/file/{file_id}', objects.AddonFile, serialise_date)

    async def get_addon_file_changelog(self, addon_id, file_id) -> str:
        return await self.__get_text(f'addon/{addon_id}/file/{file_id}/changelog')

    async def get_addon_file_download(self, addon_id, file_id) -> str:
        return await self.__get_text(f'addon/{addon_id}/file/{file_id}/download-url')

    async def get_fingerprint_addons(self, fingerprints: Iterable[int],
                                     serialise_date: bool = True) -> objects.FingerprintResponse:
        return await self.__post('fingerprint', objects.FingerprintResponse, fingerprints, serialise_date)

    async def get_minecraft_versions(self, serialise_date: bool = True) -> Iterable[objects.Minecraft]:
        return await self.__multi_get('minecraft/version', objects.Minecraft, serialise_date=serialise_date)

    async def get_minecraft_version(self, version_name: str, serialise_date: bool = True) -> objects.Minecraft:
        return await self.__get('minecraft/version/' + version_name, objects.Minecraft, serialise_date)

    async def get_mod_loader_details(self, mod_loader: str, serialise_date: bool = True) -> objects.ModLoaderDetails:
        return await self.__get('minecraft/modloader/' + mod_loader,
                                objects.ModLoaderDetails, serialise_date=serialise_date)

    async def get_mod_loaders(self, serialise_date: bool = True) -> Iterable[objects.ModLoader]:
        return await self.__multi_get('minecraft/modloader', objects.ModLoader, serialise_date=serialise_date)
