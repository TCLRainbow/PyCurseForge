from datetime import datetime
from enum import IntEnum
from typing import Optional, Union


def iso_8601_to_datetime(date: str, ms: bool = True) -> datetime:
    return datetime.strptime(date, f'%Y-%m-%dT%H:%M:%S{".%f" if ms else ""}Z')


class Addon:

    def __init__(self, json: dict, serialise_date, cf):
        self._cf = cf
        self._serialise = serialise_date
        self.id: int = json['id']
        self.name: str = json['name']
        self.authors: map = map(lambda j: Author(j), json['authors'])
        self.attachments: map = map(lambda j: Attachment(j), json['attachments'])
        self.website_url: str = json['websiteUrl']
        self.game_id: int = json['gameId']
        self.summary: str = json['summary']
        self.default_file_id: int = json['defaultFileId']
        self.download_count: int = json['downloadCount']
        self.latest_files: map = map(lambda j: AddonFile(j, serialise_date, cf), json['latestFiles'])
        self.status: AddonStatus = AddonStatus(json['status'])
        self.primary_category_id: int = json['primaryCategoryId']
        self.categories: map = map(lambda j: Category(j), json['categories'])
        self.category_section: CategorySection = CategorySection(json['categorySection'])
        self.slug: str = json['slug']
        self.game_version_latest_files: map = map(lambda j: GameVersionLatestFile(j), json['gameVersionLatestFiles'])
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

    async def get_description(self):
        return await self._cf.get_addon_description(self.id)

    async def get_files(self):
        return await self._cf.get_addon_files(self.id, self._serialise)

    async def get_file(self, file_id):
        return await self._cf.get_addon_file(self.id, file_id, self._serialise)


class Author:

    def __init__(self, json: dict):
        self.name: str = json['name']
        self.url: str = json['url']
        self.id: int = json['id']
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


class AddonFile:

    def __init__(self, json: dict, serialise_date, cf):
        self.id: int = json['id']
        self.display_name: str = json['displayName']
        self.file_name: str = json['fileName']
        if serialise_date:
            self.uploaded_at: datetime = iso_8601_to_datetime(json['fileDate'])
            self.released_at: datetime = iso_8601_to_datetime(json['gameVersionDateReleased'], False)
        else:
            self.uploaded_at: str = json['fileDate']
            self.released_at: str = json['gameVersionReleaseDate']
        self.size: int = json['fileLength']
        self.release_type: ReleaseType = ReleaseType(json['releaseType'])
        self.file_status: FileStatus = FileStatus(json['fileStatus'])
        self.download_url: str = json['downloadUrl']
        self.alternate: bool = json['isAlternate']
        self.alternate_file_id: int = json['alternateFileId']
        self.dependencies: map = map(lambda d: d['id'], json['dependencies'])
        self.available: bool = json['isAvailable']
        self.modules: map = map(lambda j: Module(j), json['modules'])
        self.package_fingerprint: str = json['packageFingerprint']
        self.game_versions: [str] = json['gameVersion']
        self.install_metadata: Optional[str] = json.get('installMetadata')
        self.changelog: Optional[str] = json.get('changelog')
        self.has_install_script: bool = json['hasInstallScript']
        self.game_version_flavor: Optional[int] = json.get('gameVersionFlavor')


# class AddonFileDetails(AddonFile):
# """Bruh wtf"""
#
#     def __init__(self, json, serialise_date, cf):
#         super().__init__(json, serialise_date, cf)
#         self.game_versions: map = map(lambda j: GameVersion(j, serialise_date), json['sortableGameVersion'])
#         self.compatible_with_client: bool = json['isCompatibleWithClient']
#         self.category_section_package_type: int = json['categorySectionPackageType']
#         self.restrict_addon_file_access: int = json['restrictProjectFileAccess']
#         self.addon_status: AddonStatus = AddonStatus(json['projectStatus'])
#         self.render_cache_id: int = json['renderCacheId']
#         self.legacy_mapping_id: Optional[int] = json.get('fileLegacyMappingId')
#         self.addon_id: int = json['projectId']
#         self.parent_addon_file_id: Optional[int] = json.get('parentProjectFileId')
#         self.parent_file_legacy_mapping_id: Optional[int] = json.get('parentFileLegacyMappingId')
#         self.file_type_id: Optional[int] = json.get('fileTypeId')
#         self.expose_as_alternative: Optional[float, int] = json.get('exposeAsAlternative')  # Float/Int?
#         self.package_fingerprint_id: int = json['packageFingerprintId']
#         self.game_id: int = json['gameId']
#         self.server_pack: bool = json['isServerPack']
#         self.server_pack_file_id: Optional[int] = json.get('serverPackFileId')
#         self.game_version_mapping_id: int = json['gameVersionMappingId']
#         self.game_version_id: int = json['gameVersionId']


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
        self.game_files: map = map(lambda j: GameFile(j), json['gameFiles'])
        self.game_detection_hints: map = map(lambda j: GameDetectionHint(j), json['gameDetectionHints'])
        self.file_parsing_rules: map = map(lambda j: FileParsingRule(j), json['fileParsingRules'])
        self.category_sections: map = map(lambda j: CategorySection(j), json['categorySections'])
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
