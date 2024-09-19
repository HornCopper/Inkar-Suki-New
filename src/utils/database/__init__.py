from src.utils.database.lib import Database
from src.utils.database.classes import (
    AffectionsList,
    ApplicationsList,
    BannedList,
    BannedWordList,
    GroupSettings,
    Permission,
    Population,
    RoleData
)

from src.const.path import DATA

db = Database(DATA + "/database/Snowykami.db")

db.auto_migrate(
    AffectionsList(),
    ApplicationsList(),
    BannedList(),
    BannedWordList(),
    GroupSettings(),
    Permission(),
    Population(),
    RoleData()
)