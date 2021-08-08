import json
from collections import Iterable
from datetime import datetime
from enum import IntEnum
from typing import Optional, Union, List


def iso_8601_to_datetime(date: str) -> datetime:
    try:
        return datetime.strptime(date, f'%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return datetime.strptime(date, f'%Y-%m-%dT%H:%M:%SZ')


class AddonFile:

    def __init__(self, j: dict, serialise_date, cf):
        self._cf = cf
        self.id: int = j['id']
        self.display_name: str = j['displayName']
        self.file_name: str = j['fileName']
        if serialise_date:
            self.uploaded_at: datetime = iso_8601_to_datetime(j['fileDate'])
            self.released_at: datetime = iso_8601_to_datetime(j['gameVersionDateReleased'])
        else:
            self.uploaded_at: str = j['fileDate']
            self.released_at: str = j['gameVersionReleaseDate']
        self.size: int = j['fileLength']
        self.release_type: ReleaseType = ReleaseType(j['releaseType'])
        self.file_status: FileStatus = FileStatus(j['fileStatus'])
        self.download_url: str = j['downloadUrl']
        self.alternate: bool = j['isAlternate']
        self.alternate_file_id: int = j['alternateFileId']
        self.dependencies: Iterable[int] = map(lambda d: d['id'], j['dependencies'])
        self.available: bool = j['isAvailable']
        self.modules: Iterable[Module] = map(lambda m: Module(m), j['modules'])
        self.package_fingerprint: str = j['packageFingerprint']
        self.game_versions: [str] = j['gameVersion']
        self.install_metadata: Optional[str] = j.get('installMetadata')
        self.changelog: Optional[str] = j.get('changelog')
        self.has_install_script: bool = j['hasInstallScript']
        self.game_version_flavor: Optional[int] = j.get('gameVersionFlavor')


class Addon:

    def __init__(self, j: dict, serialise_date, cf):
        self._cf = cf
        self._serialise = serialise_date
        self.id: int = j['id']
        self.name: str = j['name']
        self.authors: Iterable[Author] = map(lambda a: Author(a), j['authors'])
        self.attachments: Iterable[Attachment] = map(lambda a: Attachment(a), j['attachments'])
        self.website_url: str = j['websiteUrl']
        self.game_id: int = j['gameId']
        self.summary: str = j['summary']
        self.default_file_id: int = j['defaultFileId']
        self.download_count: int = j['downloadCount']
        self.latest_files: Iterable[AddonFile] = map(lambda f: AddonFile(f, serialise_date, cf), j['latestFiles'])
        self.status: AddonStatus = AddonStatus(j['status'])
        self.primary_category_id: int = j['primaryCategoryId']
        self.categories: Iterable[Category] = map(lambda c: Category(c), j['categories'])
        self.category_section: CategorySection = CategorySection(j['categorySection'])
        self.slug: str = j['slug']
        self.game_version_latest_files: Iterable[GameVersionLatestFile] = map(
            lambda f: GameVersionLatestFile(f), j['gameVersionLatestFiles'])
        self.featured: bool = j['isFeatured']
        self.popularity: float = j['popularityScore']
        self.game_popularity_rank: int = j['gamePopularityRank']
        self.primary_language: str = j['primaryLanguage']
        self.game_slug: str = j['gameSlug']
        self.game_name: str = j['gameName']
        self.portal: str = j['portalName']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(j['dateModified'])
            self.created_at: datetime = iso_8601_to_datetime(j['dateCreated'])
            self.released_at: datetime = iso_8601_to_datetime(j['dateReleased'])
        else:
            self.modified_at: str = j['dateModified']
            self.created_at: str = j['dateCreated']
            self.released_at: str = j['dateReleased']
        self.available: bool = j['isAvailable']
        self.experimental: bool = j['isExperiemental']  # Lmao this is actually their typo

    async def get_description(self) -> str:
        return await self._cf.get_addon_description(self.id)

    async def get_files(self) -> Iterable[AddonFile]:
        return await self._cf.get_addon_files(self.id, self._serialise)

    async def get_file(self, file_id) -> AddonFile:
        return await self._cf.get_addon_file(self.id, file_id, self._serialise)


class Author:

    def __init__(self, j: dict):
        self.name: str = j['name']
        self.url: str = j['url']
        self.addon_id: int = j['projectId']
        self.id: int = j['id']
        self.addon_title_id: dict = j['projectTitleId']
        self.addon_title_title: dict = j['projectTitleTitle']  # #BestKeyNameEver
        self.user_id: int = j['userId']
        self.twitch_id: int = j['twitchId']


class Attachment:

    def __init__(self, j: dict):
        self.id: int = j['id']
        self.addon_id: int = j['projectId']
        self.description: str = j['description']
        self.default: bool = j['isDefault']
        self.thumbnail_url: str = j['thumbnailUrl']
        self.title: str = j['title']
        self.url: str = j['url']
        self.status: int = j['status']


class AddonFileDetails(AddonFile):

    def __init__(self, j, serialise_date, cf):
        super().__init__(j, serialise_date, cf)
        self.game_versions: map = map(lambda v: GameVersion(v, serialise_date), j['sortableGameVersion'])
        self.compatible_with_client: bool = j['isCompatibleWithClient']
        self.category_section_package_type: int = j['categorySectionPackageType']
        self.restrict_addon_file_access: int = j['restrictProjectFileAccess']
        self.addon_status: AddonStatus = AddonStatus(j['projectStatus'])
        self.render_cache_id: int = j['renderCacheId']
        self.legacy_mapping_id: Optional[int] = j.get('fileLegacyMappingId')
        self.addon_id: int = j['projectId']
        self.parent_addon_file_id: Optional[int] = j.get('parentProjectFileId')
        self.parent_file_legacy_mapping_id: Optional[int] = j.get('parentFileLegacyMappingId')
        self.file_type_id: Optional[int] = j.get('fileTypeId')
        self.expose_as_alternative: Optional[float, int] = j.get('exposeAsAlternative')  # Float/Int?
        self.package_fingerprint_id: int = j['packageFingerprintId']
        self.game_id: int = j['gameId']
        self.server_pack: bool = j['isServerPack']
        self.server_pack_file_id: Optional[int] = j.get('serverPackFileId')
        self.game_version_mapping_id: int = j['gameVersionMappingId']
        self.game_version_id: int = j['gameVersionId']


class ReleaseType(IntEnum):
    RELEASE = 1
    BETA = 2
    ALPHA = 3


class FileStatus(IntEnum):
    PROCESSING = 1
    CHANGES_REQUIRED = 2
    UNDER_REVIEW = 3
    APPROVED = 4
    REJECTED = 5
    MALWARE_DETECTED = 6
    DELETED = 7
    ARCHIVED = 8
    TESTING = 9
    RELEASED = 10
    READY_FOR_REVIEW = 11
    DEPRECATED = 12
    BAKING = 13
    AWAITING_PUBLISHING = 14
    FAILED_PUBLISHING = 15


class AddonStatus(IntEnum):
    NEW = 1
    CHANGES_REQUIRED = 2
    UNDER_SOFT_REVIEW = 3
    APPROVED = 4
    REJECTED = 5
    CHANGES_MADE = 6
    INACTIVE = 7
    ABANDONED = 8
    DELETED = 9
    UNDER_REVIEW = 10


class Category:

    def __init__(self, j: dict):
        self.id: int = j['categoryId']
        self.name: str = j['name']
        self.url: str = j['url']
        self.avatar_url: str = j['avatarUrl']
        self.parent_id: int = j['parentId']
        self.root_id: int = j['rootId']
        self.addon_id: int = j['projectId']
        self.avatar_id: int = j['avatarId']
        self.game_id: int = j['gameId']


class CategorySection:

    def __init__(self, j: dict):
        self.id: int = j['id']
        self.game_id: int = j['gameId']
        self.name: str = j['name']
        self.package_type: int = j['packageType']
        self.path: str = j['path']
        self.initial_inclusion_pattern: str = j['initialInclusionPattern']
        self.extra_include_pattern: Optional[str] = j.get('extraIncludePattern')
        self.game_category_id: int = j['gameCategoryId']


class GameVersionLatestFile:

    def __init__(self, j: dict):
        self.version: str = j['gameVersion']
        self.file_id: int = j['projectFileId']
        self.file_name: str = j['projectFileName']
        self.file_type: int = j['fileType']
        self.version_flavor: Optional[str] = j.get('gameVersionFlavor')


class Game:

    def __init__(self, j, serialise_date):
        self.id: int = j['id']
        self.name: str = j['name']
        self.slug: str = j['slug']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(j['dateModified'])
        else:
            self.modified_at: str = j['dateModified']
        self.game_files: Iterable[GameFile] = map(lambda f: GameFile(f), j['gameFiles'])
        self.game_detection_hints: Iterable[GameDetectionHint] = map(
            lambda h: GameDetectionHint(h), j['gameDetectionHints'])
        self.file_parsing_rules: Iterable[FileParsingRule] = map(lambda r: FileParsingRule(r), j['fileParsingRules'])
        self.category_sections: Iterable[CategorySection] = map(lambda s: CategorySection(s), j['categorySections'])
        self.max_free_storage: Union[float, int] = j['maxFreeStorage']  # float / int?
        self.max_premium_storage: Union[float, int] = j['maxPremiumStorage']  # float / int?
        self.max_file_size: Union[float, int] = j['maxFileSize']  # float / int?
        self.addon_settings_folder_filter: Optional[str] = j['addonSettingsFolderFilter']
        self.addon_settings_starting_folder: Optional[str] = j['addonSettingsStartingFolder']
        self.addon_settings_file_filter: Optional[str] = j['addonSettingsFileFilter']
        self.addon_settings_file_removal_filter: Optional[str] = j['addonSettingsFileRemovalFilter']
        self.support_addons: bool = j['supportsAddons']
        self.support_partner_addons: bool = j['supportsPartnerAddons']
        self.supported_client_config: int = j['supportedClientConfiguration']
        self.support_notifications: bool = j['supportsNotifications']
        self.profiler_addon_id: int = j['profilerAddonId']
        self.twitch_game_id: int = j['twitchGameId']
        self.client_game_settings_id: int = j['clientGameSettingsId']


class GameFile:

    def __init__(self, j):
        self.id: int = j['id']
        self.game_id: int = j['gameId']
        self.required: bool = j['isRequired']
        self.file_name: str = j['fileName']
        self.file_type: int = j['fileType']
        self.platform_type: int = j['platformType']


class GameDetectionHint:

    def __init__(self, j):
        self.id: int = j['id']
        self.hint_type: int = j['hintType']
        self.hint_path: str = j['hintPath']
        self.hint_key = j['hintKey']
        self.hint_options: int = j['hintOptions']
        self.game_id: int = j['gameId']


class FileParsingRule:

    def __init__(self, j):
        self.id: int = j['id']
        self.comment_strip_pattern: str = j['commentStripPattern']
        self.extension: str = j['fileExtension']
        self.inclusion_pattern: str = j['inclusionPattern']
        self.game_id: int = j['gameId']


class Module:

    def __init__(self, j):
        self.folder: str = j['folderName']
        self.fingerprint: str = str(j['fingerprint'])
        self.type: int = j['type']


class GameVersion:

    def __init__(self, j, serialise_date):
        self.version = j['gameVersion']
        if serialise_date:
            self.released_at: datetime = iso_8601_to_datetime(j['gameVersionReleaseDate'])
        else:
            self.released_at: str = j['gameVersionReleaseDate']
        self.version_padded: str = j['gameVersionPadded']
        self.name: str = j['gameVersionName']


class FingerprintMatch:

    def __init__(self, j: dict, serialise_date, cf):
        self.id: int = j['id']
        self.file: AddonFileDetails = AddonFileDetails(j['file'], serialise_date, cf)
        self.latest_files: Iterable[AddonFileDetails] = map(
            lambda d: AddonFileDetails(d, serialise_date, cf), j['latestFiles'])


class FingerprintResponse:

    def __init__(self, j: dict, serialise_date, cf):
        self.cache_built: bool = j['isCacheBuilt']
        self.exact_matches: Iterable[FingerprintMatch] = map(
            lambda m: FingerprintMatch(m, serialise_date, cf), j['exactMatches'])
        self.exact_fingerprints: [int] = j['exactFingerprints']
        self.partial_matches: Iterable[FingerprintMatch] = map(
            lambda m: FingerprintMatch(m, serialise_date, cf), j['partialMatches'])
        self.partial_match_fingerprints: Union[List, {}] = j['partialMatchFingerprints']  # Doc: List, Received Dict
        self.installed_fingerprints: [int] = j['installedFingerprints']
        self.unmatched_fingerprints: [int] = j['unmatchedFingerprints']


class Minecraft:

    def __init__(self, j: dict, serialise_date, cf):
        self.id: int = j['id']
        self.version: str = j['versionString']
        self.version_id: int = j['gameVersionId']
        self.jar_download_url: str = j['jarDownloadUrl']
        self.json_download_url: str = j['jsonDownloadUrl']
        self.approved: bool = j['approved']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(j['dateModified'])
        else:
            self.modified_at: str = j['dateModified']
        self.version_type_id: int = j['gameVersionTypeId']
        self.version_status: int = j['gameVersionStatus']
        self.version_type_status: int = j['gameVersionTypeStatus']


class ModLoader:

    def __init__(self, j: dict, serialise_date, cf):
        self.name: str = j['name']
        self.game_version: str = j['gameVersion']
        self.latest: bool = j['latest']
        self.recommended: bool = j['recommended']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(j['dateModified'])
        else:
            self.modified_at: str = j['dateModified']


class ModLoaderDetails(ModLoader):

    def __init__(self, j: dict, serialise_date, cf):
        j['gameVersion'] = j.pop('minecraftVersion')
        super().__init__(j, serialise_date, cf)
        self.id: int = j['id']
        self.game_version_id: int = j['gameVersionId']
        self.minecraft_version_id: int = j['minecraftGameVersionId']
        self.forge_version: str = j['forgeVersion']
        self.type: int = j['type']
        self.download_url: str = j['downloadUrl']
        self.file_name: str = j['filename']
        self.install_method: int = j['installMethod']
        self.approved: bool = j['approved']
        self.maven_version: str = j['mavenVersionString']
        self.version: dict = json.loads(j['versionJson'])
        self.libs_install_path: str = j['librariesInstallLocation']
        if j.get('additionalFilesJson'):
            self.additional_files: dict = json.loads(j['additionalFilesJson'])
            self.install_profile: dict = json.loads(j['installProfileJson'])
        else:
            self.additional_files = self.install_profile = None
        self.mod_loader_game_version_id: int = j['modLoaderGameVersionId']
        self.mod_loader_game_version_type_id: int = j['modLoaderGameVersionTypeId']
        self.mod_loader_game_version_status: int = j['modLoaderGameVersionStatus']
        self.mod_loader_game_version_type_status: int = j['modLoaderGameVersionTypeStatus']
        self.mc_game_version_id: int = j['mcGameVersionId']
        self.mc_game_version_type_id: int = j['mcGameVersionTypeId']
        self.mc_game_version_status: int = j['mcGameVersionStatus']
        self.mc_game_version_type_status: int = j['mcGameVersionTypeStatus']
