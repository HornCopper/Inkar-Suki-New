from typing import List, Dict

from src.utils.database.operation import getGroupSettings
from src.const.path import (
    ASSETS,
    build_path
)

import json

with open(build_path(ASSETS, ["source", "jx3", "server_aliases.json"])) as server_aliases:
    server_aliases_data = json.loads(server_aliases.read())

with open(build_path(ASSETS, ["source", "jx3", "server_zones_mapping.json"])) as server_zones_mapping:
    server_zones_mapping_data = json.loads(server_zones_mapping.read())

class Server:
    server_aliases: Dict[str, List[str]] = server_aliases_data
    server_zones_mapping: Dict[str, List[str]] = server_zones_mapping_data

    def __init__(self, server_name: str | None = None, group_id: int | None = None):
        self._server = server_name
        self.group_id = group_id

    @property
    def server_raw(self) -> str | None:
        data = self.server_aliases
        for server_name in data:
            if self._server == server_name or self._server in data[server_name]:
                return server_name
        return None

    @property
    def server(self) -> str | None:
        if self._server is None and self.group_id is not None:
            final_server = getGroupSettings(self.group_id)
        elif self._server is not None:
            final_server = self.server_raw
        else:
            final_server = None
        return final_server
    
    @property
    def zone_legacy(self) -> str | None:
        data = self.server_zones_mapping
        for zone_name in data:
            if self.server in data[zone_name]:
                return zone_name
        return None

    @property
    def zone(self) -> str | None:
        zone_legacy_name = self.zone_legacy
        if zone_legacy_name is None:
            return None
        return zone_legacy_name if zone_legacy_name == "无界区" else zone_legacy_name[:2] + "区"