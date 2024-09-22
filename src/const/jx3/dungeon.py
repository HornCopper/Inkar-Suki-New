from typing import List, Dict

from src.const.path import (
    ASSETS,
    build_path
)

import json

with open(build_path(ASSETS, ["source", "jx3", "dungeon_name.json"])) as dungeon_name:
    dungeon_name_data = json.loads(dungeon_name.read())

with open(build_path(ASSETS, ["source", "jx3", "dungeon_mode.json"])) as dungeon_mode:
    dungeon_mode_data = json.loads(dungeon_mode.read())

class Dungeon:
    dungeon_name: Dict[str, List[str]] = dungeon_name_data
    dungeon_mode: Dict[str, List[str]] = dungeon_mode_data

    def __init__(self, name: str, mode: str):
        self._name = name
        self._mode = mode

    @property
    def name(self) -> str | None:
        """
        副本实际名称
        """
        data = self.dungeon_name
        for zone_name in data:
            if self._name in data[zone_name]:
                return zone_name
        return None
        
    @property
    def mode(self) -> str | None:
        """
        实际难度
        """
        data = self.dungeon_mode
        for mode in data:
            if self._mode in data[mode]:
                return mode
        return None