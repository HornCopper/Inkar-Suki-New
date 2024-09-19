from typing import Dict

from src.utils.exceptions import DatabaseInternelException
from src.utils.database.classes import Permission
from src.utils.database import db

def get_all_admin() -> Permission:
    data = db.where_one(Permission(), default=Permission())
    if not isinstance(data, Permission):
        raise DatabaseInternelException()
    return data

def checker(user_id: str, level: int) -> bool:
    data: Permission = get_all_admin()
    permissions: Dict[str, str] = data.permissions_list
    return False if user_id not in permissions else int(permissions[user_id]) >= level

def error(level: int | str) -> str:
    return f"唔……你权限不够哦，这条命令要至少{level}的权限哦~"