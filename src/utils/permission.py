from typing import Dict

from src.utils.exceptions import DatabaseInternelException
from src.utils.database.classes import Permission
from src.utils.database import db

def get_all_admin() -> Permission:
    """
    获取权限数据库对象。

    Returns:
        obj (Permission): 权限数据库对象。
    """
    data = db.where_one(Permission(), default=Permission())
    if not isinstance(data, Permission):
        raise DatabaseInternelException()
    return data

def checker(user_id: str | int, level: str | int) -> bool:
    """
    检查用户是否满足某个权限等级。

    Args:
        user_id (str, int): 用户`uin`。
        level (str, int): 至少需达到的权限等级。
    """
    data: Permission = get_all_admin()
    permissions: Dict[str, str] = data.permissions_list
    return False if str(user_id) not in permissions else int(permissions[str(user_id)]) >= int(level)

def error(level: int | str) -> str:
    """
    构造权限不足提示。

    Args:
        level (str, int): 没有达到的权限等级。
    """
    return f"唔……你权限不够哦，这条命令要至少{level}的权限哦~"