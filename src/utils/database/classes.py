from typing import List, Dict

from src.utils.database.lib import LiteModel

class Affections(LiteModel):
    TABLE_NAME: str = "affections"
    server: str = ""
    uin_1: int = 0
    uin_2: int = 0
    name_1: str = ""
    name_2: str = ""
    time: int = 0
    school_1: str = ""
    school_2: str = ""

class ApplicationsList(LiteModel):
    TABLE_NAME: str = "applications"
    applications_list: list = []

# class BannedWordList(LiteModel):
#     TABLE_NAME: str = "banword"
#     banned_word_list: List[str] = []

class BannedUser(LiteModel):
    TABLE_NAME: str = "ban"
    user_id: int = 0
    reason: str = ""    

# class BannedList(LiteModel):
#     TABLE_NAME: str = "ban"
#     banned_list: list = []

class GroupSettings(LiteModel):
    TABLE_NAME: str = "settings"
    server: str = ""
    group_id: str = ""
    subscribe: List[str] = []
    addtions: List[str] = []
    welcome: str = "欢迎入群！"
    blacklist: List[Dict[str, str]] = [] 
    wiki: dict = {"startwiki": "", "interwiki": []}
    webhook: List[str] = []
    opening: list = []

class Permission(LiteModel):
    TABLE_NAME: str = "permission"
    permissions_list: dict = {}

class Population(LiteModel):
    TABLE_NAME: str = "population"
    populations: dict = {}

class RoleData(LiteModel):
    TABLE_NAME: str = "role_data"
    bodyName: str = ""
    campName: str = ""
    forceName: str = ""
    globalRoleId: str = ""
    roleName: str = ""
    roleId: str = ""
    serverName: str = ""