from typing import List, Dict
from typing_extensions import Self

from src.utils.analyze import invert_dict
from src.const.path import (
    ASSETS,
    build_path
)
from src.const.jx3.school import school_aliases_data

import json

with open(build_path(ASSETS, ["source", "jx3", "kungfu_aliases.json"])) as kungfu_aliases:
    kungfu_aliases_data = json.loads(kungfu_aliases.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_colors.json"])) as kungfu_colors:
    kungfu_colors_data = json.loads(kungfu_colors.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_internel_id.json"])) as kungfu_internel_id:
    kungfu_internel_id_data = json.loads(kungfu_internel_id.read())

class Kungfu:
    kungfu_aliases: Dict[str, List[str]] = kungfu_aliases_data
    kungfu_colors_data: Dict[str, str] = kungfu_colors_data
    kungfu_internel_id: Dict[str, str] = kungfu_internel_id_data

    school_aliases: Dict[str, List[str]] = school_aliases_data

    def __init__(self, kungfu_name: str = ""):
        self.kungfu_name = kungfu_name

    @classmethod
    def with_internel_id(cls, internel_id: int | str) -> Self:
        if str(internel_id) in invert_dict(cls.kungfu_internel_id):
            return cls(invert_dict(cls.kungfu_internel_id)[str(internel_id)])
        return cls()
    
    @property
    def name(self) -> str | None:
        for kungfu_name, aliases in self.kungfu_aliases.items():
            if self.kungfu_name == kungfu_name or self.kungfu_name in aliases:
                return kungfu_name
        return None
    
    @property
    def school(self) -> str | None:
        for school_name, aliases in self.school_aliases.items():
            if self.kungfu_name in aliases:
                return school_name
        return None