from typing import Tuple, List
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

from src.const.path import ASSETS, CACHE, build_path
from src.const.jx3.kungfu import Kungfu
from src.utils.network import Request
from src.utils.generate import get_uuid
from src.utils.typing import override

from src.plugins.jx3.attributes.v2 import (
    local_save,
    special_weapon,
    JX3AttributeV2,
    SingleAttr
)

import json

async def get_recommended_equips_list(forceId: str, condition: list) -> Tuple[list, list, list, list, list]:
    params = {
        "Kungfu": forceId,
        "EquipTags": condition,
        "Size": 10,
        "cursor": 0,
        "matchSeasonId": "6629cd12ba3129001275fc58"
    }
    source_data = (await Request(url="https://m.pvp.xoyo.com/socialgw/dynamic/equip/query", params=params).post(tuilan=True)).json()
    data = []
    name = []
    tag = []
    like = []
    author = []
    for i in source_data["data"]["data"]:
        data.append(json.loads(i["matchEquip"]["equips"]))
        name.append(i["matchEquip"]["name"])
        tag.append(i["matchEquip"]["tags"][0])
        author.append(i["nickname"])
        like.append(str(i["likeCount"]))
    return data, name, tag, author, like

class JX3AttributeV2_M(JX3AttributeV2):
    @override
    def _panel_type(self, panel_attr_name: str) -> SingleAttr:
        """
        将面板展示的属性转换为实际需要的属性，并传出已有数据的对应属性字典。
        """
        panel_attr_map = {
            "面板攻击": "攻击力",
            "基础攻击": "基础攻击力",
            "最大气血值": "气血",
            "面板治疗量": "治疗量",
            "基础治疗量": "治疗量",
            "外防": "外功防御",
            "内防": "内功防御"
        }
        if panel_attr_name in panel_attr_map:
            panel_attr_name = panel_attr_map[panel_attr_name]
        speed_percent = False
        if panel_attr_name == "加速率":
            speed_percent = True
        for attr in self.data["data"]["PersonalPanel"]:
            if attr["name"] == panel_attr_name:
                return SingleAttr(attr, speed_percent)
        raise ValueError(f"Unexpected attribute `{panel_attr_name}`!")

def att_mapping(att):
    if att == "根骨":
        return "atSpiritBase"
    elif att == "力道":
        return "atStrengthBase"
    elif att == "元气":
        return "atSpunkBase"
    elif att == "身法":
        return "atAgilityBase"
    
async def get_single_recequips(data: dict, author: str, name: str, tag: str, kungfu: str):
    score = str(data["matchDetail"]["score"])
    basic = [score, name, author, tag]
    kungfu_obj = Kungfu(kungfu)
    background = await JX3AttributeV2_M.background(str(kungfu_obj.name))
    data_obj = JX3AttributeV2_M(data)
    max_strength, current_strength = data_obj.strength or ([], [])
    equip_names, equip_icons = data_obj.equips_and_icons or ([], [])
    color_stones = data_obj.color_stone or [("", "")]
    if kungfu_obj.school == "藏剑":
        c1n, c1i = color_stones[0]
        c2n, c2i = color_stones[1]
    else:
        c1n, c1i = color_stones[0]
        c2n, c2i = ""
    image = await get_recommend_equip_image(
        kungfu_obj,
        background,
        max_strength,
        current_strength,
        equip_names,
        equip_icons,
        data_obj.qualities or [],
        basic,
        data_obj.common_enchant or [],
        data_obj.permanent_enchant or [],
        data_obj.five_stones,
        c1i,
        c1n,
        data_obj.attr_values,
        c2n,
        c2i
    )
    return image
    

async def get_recommend_equip_image(
    kungfu: Kungfu, 
    school_background: str,
    max_strength: list,
    strength: list, 
    equip_list: list,
    equip_icon: list, 
    equip_quailty: list, 
    basic_info: list,
    common_enchant: list, 
    permanent_enchant: list, 
    five_stone: list, 
    color_stone_icon: str,
    color_stone_name: str, 
    attribute_values: list, 
    color_stone_name_2: str, 
    color_stone_icon_2: str
):
    attr = kungfu.base
    syst_bold = build_path(ASSETS, ["font", "syst-bold.ttf"])
    syst_mid = build_path(ASSETS, ["font", "syst-mid.ttf"])
    msyh = build_path(ASSETS, ["font", "msyh.ttf"])
    calibri = build_path(ASSETS, ["font", "calibri.ttf"])
    if attr in ["根骨", "元气", "力道", "身法"]:
        objects = ["面板攻击", "基础攻击", "会心", "会心效果", "加速", attr, "破防", "无双", "破招", "最大气血值", "御劲", "化劲"]
    elif attr == "治疗":
        objects = ["面板治疗量", "基础治疗量", "会心", "会心效果", "加速",
                   "根骨", "外防", "内防", "破招", "最大气血值", "御劲", "化劲"]
    elif attr == "防御":
        objects = ["外防", "内防", "最大气血值", "破招", "御劲", "闪避", "招架", "拆招", "体质", "加速率", "无双", "加速"]
    else:
        objects = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    background = Image.open(school_background)
    draw = ImageDraw.Draw(background)
    flickering = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "flicker.png"])).resize((38, 38))
    precious = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "peerless.png"]))
    max_strength_approching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "max_strength.png"]))
    max_strength_unapproching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "not_max_strength.png"]))
    common_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"])).resize((20, 20))
    permanent_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"])).resize((20, 20))

    # 心法图标
    background.alpha_composite(Image.open(str(kungfu.icon)).resize((50, 50)), (61, 62))

    # 武器图标
    if kungfu not in ["问水诀", "山居剑意"]:
        if equip_icon[11] != "":
            background.alpha_composite(Image.open(await local_save(equip_icon[11])).resize((38, 38)), (708, 587))
            if max_strength[11] in ["3", "4", "8"] or special_weapon(equip_list[11]):
                background.alpha_composite(precious, (688, 586))
                if max_strength[11] == "8":
                    background.alpha_composite(flickering, (707, 586))
                else:
                    if max_strength[11] == strength[11]:
                        background.alpha_composite(max_strength_approching, (708, 587))
            else:
                if max_strength[11] == strength[11]:
                    background.alpha_composite(max_strength_approching, (708, 587))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 587))
    else:
        if equip_icon[11] != "":
            background.alpha_composite(Image.open(await local_save(equip_icon[11])).resize((38, 38)), (708, 587))
            if max_strength[11] in ["3", "4", "8"] or special_weapon(equip_list[11]):
                background.alpha_composite(precious, (688, 586))
                if max_strength[11] == "8":
                    background.alpha_composite(flickering, (708, 587))
                else:
                    if max_strength[11] == strength[11]:
                        background.alpha_composite(max_strength_approching, (708, 587))
            else:
                if max_strength[11] == strength[11]:
                    background.alpha_composite(max_strength_approching, (708, 587))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 587))
        if equip_icon[12] != "":
            if special_weapon(equip_list[12]):
                background.alpha_composite(precious, (688, 635))
            background.alpha_composite(Image.open(await local_save(equip_icon[12])).resize((38, 38)), (708, 636))
            if max_strength[12] in ["3", "4", "8"]:
                background.alpha_composite(precious, (688, 635))
                if max_strength[12] == "8":
                    background.alpha_composite(flickering, (708, 636))
                else:
                    if max_strength[12] == strength[12]:
                        background.alpha_composite(max_strength_approching, (708, 636))
            else:
                if max_strength[12] == strength[12]:
                    background.alpha_composite(max_strength_approching, (708, 636))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 636))

    # 装备图标
    init = 48
    limit = 0
    for i in equip_icon:
        if i != "":
            background.alpha_composite(Image.open(await local_save(i)).resize((38, 38)), (708, init))
        init = init + 49
        limit = limit + 1
        if limit == 11:
            break

    # 装备精炼
    init = 47
    range_time = 11
    if kungfu in ["问水诀", "山居剑意"]:
        range_time = range_time + 1
    for i in range(range_time):
        if special_weapon(equip_list[i]):
            background.alpha_composite(precious, (687, init - 1))
        if max_strength[i] in ["3", "4", "8"]:
            background.alpha_composite(precious, (687, init - 1))
        if strength[i] == max_strength[i]:
            background.alpha_composite(max_strength_approching, (707, init))
        else:
            if equip_list[i] != "":
                background.alpha_composite(max_strength_unapproching, (707, init))
        if max_strength[i] == "8":
            background.alpha_composite(flickering, (709, init + 2))
        init = init + 49

    # 装备名称
    init = 50
    for i in equip_list:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 装备品级 + 属性
    init = 71
    for i in equip_quailty:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 个人基本信息
    draw.text((85, 127), str(basic_info[0]), fill=(0, 0, 0),
              font=ImageFont.truetype(calibri, size=18), anchor="mt")
    draw.text((370, 70), basic_info[1], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=32), anchor="mm")
    draw.text((370, 120), basic_info[2], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=20), anchor="mm")
    draw.text((450, 120), basic_info[3], fill=(127, 127, 127),
              font=ImageFont.truetype(calibri, size=18), anchor="mm")

    # 面板内容
    positions = [(127, 226), (258, 226), (385, 226), (514, 226), (127, 303), (258, 303),
                 (385, 303), (514, 303), (127, 380), (258, 380), (385, 380), (514, 380)]
    range_time = 12
    for i in range(range_time):
        draw.text(positions[i], objects[i], fill=(255, 255, 255),
                  font=ImageFont.truetype(syst_bold, size=20), anchor="mm")

    # 面板数值
    draw.text((129, 201), attribute_values[0], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 201), attribute_values[1], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 201), attribute_values[2], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 201), attribute_values[3], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 278), attribute_values[4], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 278), attribute_values[5], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 278), attribute_values[6], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 278), attribute_values[7], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 355), attribute_values[8], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 355), attribute_values[9], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 355), attribute_values[10], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 355), attribute_values[11], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")

    # 装备位置
    init = 50
    equips = ["帽子", "上衣", "腰带", "护手", "下装", "鞋子", "项链", "腰坠", "戒指", "戒指", "远程武器", "近身武器"]
    for i in equips:
        draw.text((940, init), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
        init = init + 49

    # 五行石
    positions = [(940, 65), (960, 65), (940, 114), (960, 114), (940, 163), (960, 163), (940, 212), (960, 212), (940, 261),
                 (960, 261), (940, 310), (960, 310), (940, 359), (940, 408), (940, 555), (940, 604), (960, 604), (980, 604)]
    range_time = 18
    if kungfu in ["问水诀", "山居剑意"]:
        range_time = range_time + 3
        positions.append((940, 653))
        positions.append((960, 653))
        positions.append((980, 653))
    for i in range(range_time):
        background.alpha_composite(Image.open(five_stone[i]).resize((20, 20)), positions[i])

    # 小附魔
    init = 45
    for i in permanent_enchant:
        if i == "":
            init = init + 49
            continue
        else:
            background.alpha_composite(permanent_enchant_icon, (1044, init))
            draw.text((1068, init + 4), i, file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")
            init = init + 49

    # 大附魔
    y = [65, 114, 163, 212, 310]
    for i in range(5):
        if common_enchant[i] == "":
            continue
        else:
            background.alpha_composite(common_enchant_icon, (1044, y[i]))
            draw.text((1068, y[i] + 4), common_enchant[i], file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")

    # 五彩石
    if color_stone_icon != "":
        background.alpha_composite(Image.open(await local_save(color_stone_icon)).resize((20, 20)), (1044, 604))
    if color_stone_name != "":
        draw.text((1068, 608), color_stone_name, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
    if color_stone_icon_2 != "":
        background.alpha_composite(Image.open(await local_save(color_stone_icon_2)).resize((20, 20)), (1044, 654))
    if color_stone_name_2 != "":
        draw.text((1068, 657), color_stone_name_2, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")

    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return Path(final_path).as_uri()