from jinja2 import Template

from src.const.path import (
    ASSETS, 
    CACHE, 
    TEMPLATES, 
    build_path
)
from src.utils.file import read
from src.config import Config

import re

universal_template = read(
    build_path(
        TEMPLATES,
        [
            "universe.html"
        ]
    )
)

class HTMLSourceCode:
    standard = universal_template

    def __init__(
            self,
            application_name: str,
            font_path: str = build_path(ASSETS, ["font", "cutsom.ttf"]),
            footer: str = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！",
            additional_css: str = "",
            **kwargs
    ):
        """
        初始化`HTML`生成器实例。

        Args:
            application_name (str): 需要生成的`HTML`的模块名。
            font_path (str): 非必需。`HTML`整体字体，不传入则使用`src/assets/font/custom.ttf`。
            footer (str): 非必需。页面最底部的字符串，推荐剑网3模块使用骚话，其他模块使用说明。
            additional_css (str): 额外定义的`CSS`，如果需要使用请提前定义！
            **kwargs (dict)：其他替换参数，按键值对直接进行替换，请确保存在。
        """
        self.name = application_name
        self.font = font_path    
        self.footer = footer
        self.css = additional_css
        self.kwargs = kwargs

    def __str__(self) -> str:
        if self.kwargs.get("table_head", None) is not None:
            self.kwargs["table_width_length"] = str(len(re.findall(r"<th.*?>.*?</th>", self.kwargs.get("table_head", []), re.DOTALL)))
        css_path = f"<link rel=\"stylesheet\" href=\"" + self.css + "\">" if self.css.startswith("file") else ""
        css_content = self.css if not self.css.startswith("file") else ""
        return Template(
            self.standard
        ).render(
            css_link = css_path,
            css = css_content,
            font = self.font,
            bot_name = Config.bot_basic.bot_name_argument,
            app_info = self.name,
            footer_msg = self.footer,
            **self.kwargs
        )