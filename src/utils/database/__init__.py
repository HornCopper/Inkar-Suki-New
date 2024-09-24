from src.utils.database.lib import Database
from src.utils.database.classes import (
    Account,
    ApplicationsList,
    BannedUser,
    GroupSettings,
    Population,
    RoleData
)

from src.const.path import DATA, build_path

db = Database(build_path(DATA, ["global", "Snowykami.db"]))

db.auto_migrate(
    Account(),
    ApplicationsList(),
    BannedUser(),
    GroupSettings(),
    Population(),
    RoleData()
)