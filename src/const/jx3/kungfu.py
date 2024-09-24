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

with open(build_path(ASSETS, ["source", "jx3", "kungfu_baseattr.json"])) as kungfu_baseattr:
    kungfu_baseattr_data = json.loads(kungfu_baseattr.read())

class Kungfu:
    kungfu_aliases: Dict[str, List[str]] = kungfu_aliases_data
    kungfu_colors_data: Dict[str, str] = kungfu_colors_data
    kungfu_internel_id: Dict[str, str] = kungfu_internel_id_data
    kungfu_baseattr: Dict[str, List[str]]

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
        """
        心法实际名称。
        """
        for kungfu_name, aliases in self.kungfu_aliases.items():
            if self.kungfu_name == kungfu_name or self.kungfu_name in aliases:
                return kungfu_name
        return None
    
    @property
    def school(self) -> str | None:
        """
        所属门派。
        """
        for school_name, aliases in self.school_aliases.items():
            if self.name in aliases:
                return school_name
        return None
    
    @property
    def color(self) -> str:
        """
        心法颜色。
        """
        if self.name is None:
            return "#FFFFFF"
        return self.kungfu_colors_data.get(self.name, "#FFFFFF")
    
    @property
    def icon(self) -> str | None:
        """
        心法图标。
        """
        if self.name is None:
            return
        return build_path(
            ASSETS,
            [
                "image",
                "jx3",
                "kungfu"
            ],
            end_with_slash=True
        ) + self.name + ".png"
    
    @property
    def base(self) -> str | None:
        """
        心法基础属性。

        防御与治疗不参与。
        """
        if self.name is None:
            return
        for base_attr, kungfus in self.kungfu_baseattr.items():
            if self.name in kungfus:
                return base_attr
        return None