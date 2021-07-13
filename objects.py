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

    def __init__(self, json: dict, serialise_date, cf):
        self._cf = cf
        self.id: int = json['id']
        self.display_name: str = json['displayName']
        self.file_name: str = json['fileName']
        if serialise_date:
            self.uploaded_at: datetime = iso_8601_to_datetime(json['fileDate'])
            self.released_at: datetime = iso_8601_to_datetime(json['gameVersionDateReleased'])
        else:
            self.uploaded_at: str = json['fileDate']
            self.released_at: str = json['gameVersionReleaseDate']
        self.size: int = json['fileLength']
        self.release_type: ReleaseType = ReleaseType(json['releaseType'])
        self.file_status: FileStatus = FileStatus(json['fileStatus'])
        self.download_url: str = json['downloadUrl']
        self.alternate: bool = json['isAlternate']
        self.alternate_file_id: int = json['alternateFileId']
        self.dependencies: Iterable[int] = map(lambda d: d['id'], json['dependencies'])
        self.available: bool = json['isAvailable']
        self.modules: Iterable[Module] = map(lambda j: Module(j), json['modules'])
        self.package_fingerprint: str = json['packageFingerprint']
        self.game_versions: [str] = json['gameVersion']
        self.install_metadata: Optional[str] = json.get('installMetadata')
        self.changelog: Optional[str] = json.get('changelog')
        self.has_install_script: bool = json['hasInstallScript']
        self.game_version_flavor: Optional[int] = json.get('gameVersionFlavor')


class Addon:

    def __init__(self, json: dict, serialise_date, cf):
        self._cf = cf
        self._serialise = serialise_date
        self.id: int = json['id']
        self.name: str = json['name']
        self.authors: Iterable[Author] = map(lambda j: Author(j), json['authors'])
        self.attachments: Iterable[Attachment] = map(lambda j: Attachment(j), json['attachments'])
        self.website_url: str = json['websiteUrl']
        self.game_id: int = json['gameId']
        self.summary: str = json['summary']
        self.default_file_id: int = json['defaultFileId']
        self.download_count: int = json['downloadCount']
        self.latest_files: Iterable[AddonFile] = map(lambda j: AddonFile(j, serialise_date, cf), json['latestFiles'])
        self.status: AddonStatus = AddonStatus(json['status'])
        self.primary_category_id: int = json['primaryCategoryId']
        self.categories: Iterable[Category] = map(lambda j: Category(j), json['categories'])
        self.category_section: CategorySection = CategorySection(json['categorySection'])
        self.slug: str = json['slug']
        self.game_version_latest_files: Iterable[GameVersionLatestFile] = map(
            lambda j: GameVersionLatestFile(j), json['gameVersionLatestFiles'])
        self.featured: bool = json['isFeatured']
        self.popularity: float = json['popularityScore']
        self.game_popularity_rank: int = json['gamePopularityRank']
        self.primary_language: str = json['primaryLanguage']
        self.game_slug: str = json['gameSlug']
        self.game_name: str = json['gameName']
        self.portal: str = json['portalName']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(json['dateModified'])
            self.created_at: datetime = iso_8601_to_datetime(json['dateCreated'])
            self.released_at: datetime = iso_8601_to_datetime(json['dateReleased'])
        else:
            self.modified_at: str = json['dateModified']
            self.created_at: str = json['dateCreated']
            self.released_at: str = json['dateReleased']
        self.available: bool = json['isAvailable']
        self.experimental: bool = json['isExperiemental']  # Lmao this is actually their typo

    async def get_description(self) -> str:
        return await self._cf.get_addon_description(self.id)

    async def get_files(self) -> Iterable[AddonFile]:
        return await self._cf.get_addon_files(self.id, self._serialise)

    async def get_file(self, file_id) -> AddonFile:
        return await self._cf.get_addon_file(self.id, file_id, self._serialise)


class Author:

    def __init__(self, json: dict):
        self.name: str = json['name']
        self.url: str = json['url']
        self.addon_id: int = json['projectId']
        self.id: int = json['id']
        self.addon_title_id: dict = json['projectTitleId']
        self.addon_title_title: dict = json['projectTitleTitle']  # #BestKeyNameEver
        self.user_id: int = json['userId']
        self.twitch_id: int = json['twitchId']


class Attachment:

    def __init__(self, json: dict):
        self.id: int = json['id']
        self.addon_id: int = json['projectId']
        self.description: str = json['description']
        self.default: bool = json['isDefault']
        self.thumbnail_url: str = json['thumbnailUrl']
        self.title: str = json['title']
        self.url: str = json['url']
        self.status: int = json['status']


class AddonFileDetails(AddonFile):

    def __init__(self, json, serialise_date, cf):
        super().__init__(json, serialise_date, cf)
        self.game_versions: map = map(lambda j: GameVersion(j, serialise_date), json['sortableGameVersion'])
        self.compatible_with_client: bool = json['isCompatibleWithClient']
        self.category_section_package_type: int = json['categorySectionPackageType']
        self.restrict_addon_file_access: int = json['restrictProjectFileAccess']
        self.addon_status: AddonStatus = AddonStatus(json['projectStatus'])
        self.render_cache_id: int = json['renderCacheId']
        self.legacy_mapping_id: Optional[int] = json.get('fileLegacyMappingId')
        self.addon_id: int = json['projectId']
        self.parent_addon_file_id: Optional[int] = json.get('parentProjectFileId')
        self.parent_file_legacy_mapping_id: Optional[int] = json.get('parentFileLegacyMappingId')
        self.file_type_id: Optional[int] = json.get('fileTypeId')
        self.expose_as_alternative: Optional[float, int] = json.get('exposeAsAlternative')  # Float/Int?
        self.package_fingerprint_id: int = json['packageFingerprintId']
        self.game_id: int = json['gameId']
        self.server_pack: bool = json['isServerPack']
        self.server_pack_file_id: Optional[int] = json.get('serverPackFileId')
        self.game_version_mapping_id: int = json['gameVersionMappingId']
        self.game_version_id: int = json['gameVersionId']


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

    def __init__(self, json: dict):
        self.id: int = json['categoryId']
        self.name: str = json['name']
        self.url: str = json['url']
        self.avatar_url: str = json['avatarUrl']
        self.parent_id: int = json['parentId']
        self.root_id: int = json['rootId']
        self.addon_id: int = json['projectId']
        self.avatar_id: int = json['avatarId']
        self.game_id: int = json['gameId']


class CategorySection:

    def __init__(self, json: dict):
        self.id: int = json['id']
        self.game_id: int = json['gameId']
        self.name: str = json['name']
        self.package_type: int = json['packageType']
        self.path: str = json['path']
        self.initial_inclusion_pattern: str = json['initialInclusionPattern']
        self.extra_include_pattern: Optional[str] = json.get('extraIncludePattern')
        self.game_category_id: int = json['gameCategoryId']


class GameVersionLatestFile:

    def __init__(self, json: dict):
        self.version: str = json['gameVersion']
        self.file_id: int = json['projectFileId']
        self.file_name: str = json['projectFileName']
        self.file_type: int = json['fileType']
        self.version_flavor: Optional[str] = json.get('gameVersionFlavor')


class Game:

    def __init__(self, json, serialise_date):
        self.id: int = json['id']
        self.name: str = json['name']
        self.slug: str = json['slug']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(json['dateModified'])
        else:
            self.modified_at: str = json['dateModified']
        self.game_files: Iterable[GameFile] = map(lambda j: GameFile(j), json['gameFiles'])
        self.game_detection_hints: Iterable[GameDetectionHint] = map(
            lambda j: GameDetectionHint(j), json['gameDetectionHints'])
        self.file_parsing_rules: Iterable[FileParsingRule] = map(lambda j: FileParsingRule(j), json['fileParsingRules'])
        self.category_sections: Iterable[CategorySection] = map(lambda j: CategorySection(j), json['categorySections'])
        self.max_free_storage: Union[float, int] = json['maxFreeStorage']  # float / int?
        self.max_premium_storage: Union[float, int] = json['maxPremiumStorage']  # float / int?
        self.max_file_size: Union[float, int] = json['maxFileSize']  # float / int?
        self.addon_settings_folder_filter: Optional[str] = json['addonSettingsFolderFilter']
        self.addon_settings_starting_folder: Optional[str] = json['addonSettingsStartingFolder']
        self.addon_settings_file_filter: Optional[str] = json['addonSettingsFileFilter']
        self.addon_settings_file_removal_filter: Optional[str] = json['addonSettingsFileRemovalFilter']
        self.support_addons: bool = json['supportsAddons']
        self.support_partner_addons: bool = json['supportsPartnerAddons']
        self.supported_client_config: int = json['supportedClientConfiguration']
        self.support_notifications: bool = json['supportsNotifications']
        self.profiler_addon_id: int = json['profilerAddonId']
        self.twitch_game_id: int = json['twitchGameId']
        self.client_game_settings_id: int = json['clientGameSettingsId']


class GameFile:

    def __init__(self, json):
        self.id: int = json['id']
        self.game_id: int = json['gameId']
        self.required: bool = json['isRequired']
        self.file_name: str = json['fileName']
        self.file_type: int = json['fileType']
        self.platform_type: int = json['platformType']


class GameDetectionHint:

    def __init__(self, json):
        self.id: int = json['id']
        self.hint_type: int = json['hintType']
        self.hint_path: str = json['hintPath']
        self.hint_key = json['hintKey']
        self.hint_options: int = json['hintOptions']
        self.game_id: int = json['gameId']


class FileParsingRule:

    def __init__(self, json):
        self.id: int = json['id']
        self.comment_strip_pattern: str = json['commentStripPattern']
        self.extension: str = json['fileExtension']
        self.inclusion_pattern: str = json['inclusionPattern']
        self.game_id: int = json['gameId']


class Module:

    def __init__(self, json):
        self.folder: str = json['folderName']
        self.fingerprint: str = str(json['fingerprint'])
        self.type: int = json['type']


class GameVersion:

    def __init__(self, json, serialise_date):
        self.version = json['gameVersion']
        if serialise_date:
            self.released_at: datetime = iso_8601_to_datetime(json['gameVersionReleaseDate'])
        else:
            self.released_at: str = json['gameVersionReleaseDate']
        self.version_padded: str = json['gameVersionPadded']
        self.name: str = json['gameVersionName']


class FingerprintMatch:

    def __init__(self, json: dict, serialise_date, cf):
        self.id: int = json['id']
        self.file: AddonFileDetails = AddonFileDetails(json['file'], serialise_date, cf)
        self.latest_files: Iterable[AddonFileDetails] = map(
            lambda j: AddonFileDetails(j, serialise_date, cf), json['latestFiles'])


class FingerprintResponse:

    def __init__(self, json: dict, serialise_date, cf):
        self.cache_built: bool = json['isCacheBuilt']
        self.exact_matches: Iterable[FingerprintMatch] = map(
            lambda j: FingerprintMatch(j, serialise_date, cf), json['exactMatches'])
        self.exact_fingerprints: [int] = json['exactFingerprints']
        self.partial_matches: Iterable[FingerprintMatch] = map(
            lambda j: FingerprintMatch(j, serialise_date, cf), json['partialMatches'])
        self.partial_match_fingerprints: Union[List, {}] = json['partialMatchFingerprints']  # Doc: List, Received Dict
        self.installed_fingerprints: [int] = json['installedFingerprints']
        self.unmatched_fingerprints: [int] = json['unmatchedFingerprints']


class Minecraft:

    def __init__(self, json: dict, serialise_date, cf):
        self.id: int = json['id']
        self.version: str = json['versionString']
        self.version_id: int = json['gameVersionId']
        self.jar_download_url: str = json['jarDownloadUrl']
        self.json_download_url: str = json['jsonDownloadUrl']
        self.approved: bool = json['approved']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(json['dateModified'])
        else:
            self.modified_at: str = json['dateModified']
        self.version_type_id: int = json['gameVersionTypeId']
        self.version_status: int = json['gameVersionStatus']
        self.version_type_status: int = json['gameVersionTypeStatus']


class ModLoader:

    def __init__(self, j: dict, serialise_date, cf):
        self.id: int = j['id']
        self.game_version_id: int = j['gameVersionId']
        self.minecraft_version_id: int = j['minecraftGameVersionId']
        self.forge_version: str = j['forgeVersion']
        self.name: str = j['name']
        self.type: int = j['type']
        self.download_url: str = j['downloadUrl']
        self.file_name: str = j['filename']
        self.install_method: int = j['installMethod']
        self.latest: bool = j['latest']
        self.recommended: bool = j['recommended']
        self.approved: bool = j['approved']
        if serialise_date:
            self.modified_at: datetime = iso_8601_to_datetime(j['dateModified'])
        else:
            self.modified_at: str = j['dateModified']
        self.maven_version: str = j['mavenVersionString']
        self.version_json: dict = json.loads(j['versionJson'])
        self.libs_install_path: str = j['librariesInstallLocation']
        self.minecraft_version: str = j['minecraftVersion']
        if j.get('additionalFilesJson'):
            self.additional_files_json: dict = json.loads(j['additionalFilesJson'])
        else:
            self.additional_files_json = None

