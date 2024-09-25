from pathlib import Path
from nonebot.log import logger
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.utils.tuilan import gen_ts, dungeon_sign
from src.utils.time import Time
from src.templates import HTMLSourceCode

import json
import re
import time

from ._template import (
    star, 
    template_drop, 
    table_drop_head,
    image_template,
    template_zone_record,
    table_zone_record_head,
    template_item,
    table_item_head
)

async def get_map(name, mode) -> int | None:
    params = {
        "mode": 2
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/list", params=params).post(tuilan=True)).json()
    for i in data["data"]:
        for x in i["dungeon_infos"]:
            if x["name"] == name:
                for y in x["maps"]:
                    if y["mode"] == mode:
                        return y["map_id"]


async def get_boss(map, mode, boss) -> str | None:
    map_id = await get_map(map, mode)
    params = {
        "map_id": map_id
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/info", params=params).post(tuilan=True)).json()
    data = json.loads(data)
    for i in data["data"]["info"]["boss_infos"]:
        if i["name"] == boss:
            return i["index"]


async def get_drops(map, mode, boss) -> dict:
    boss_id = await get_boss(map, mode, boss)
    params = {
        "boss_id": boss_id
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/boss-drop", params=params).post(tuilan=True)).json()
    return json.loads(data)

# 暂时不打算做5人副本，5人副本与10人副本的请求地址不同。
# 10人/25人：https://m.pvp.xoyo.com/dungeon/list
# 5人：https://m.pvp.xoyo.com/dungeon/list-all
# 暂时未知数据是否相同，后续考虑是否添加。

equip_types = ["帽子", "上衣", "腰带", "护臂", "裤子", "鞋", "项链", "腰坠", "戒指", "投掷囊"]

filter_words = ["根骨", "力道", "元气", "身法", "体质"]

async def get_drop_list_image(map: str, mode: str, boss: str):
    try:
        data = await get_drops(map, mode, boss)
    except KeyError:
        return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
    data = data["data"]
    armors = data["armors"]
    others = data["others"]
    weapons = data["weapons"]
    if armors is None:
        armors = []
    if others is None:
        others = []
    if weapons is None:
        weapons = []
    if len(armors) == 0 and len(others) == 0 and len(weapons) == 0:
        return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    else:
        table_content = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            if i["Icon"]["SubKind"] in equip_types:
                if "Type" in list(i):
                    if i["Type"] == "Act_运营及版本道具":
                        type_ = "外观"
                        attrs = "不适用"
                        fivestone = "不适用"
                        max = "不适用"
                        quailty = "不适用"
                        score = "不适用"
                        type_ = "装备"
                    else:
                        type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                        attrs = "不适用"
                        fivestone = "不适用"
                        max = "不适用"
                        quailty = "不适用"
                        score = "不适用"
                else:
                    type_ = i["Icon"]["SubKind"]
                    attrs_data = i["ModifyType"]
                    attrs_list = []
                    for x in attrs_data:
                        string = x["Attrib"]["GeneratedMagic"]
                        flag = False
                        for y in filter_words:
                            if string.find(y) != -1:
                                flag = True
                        if flag:
                            continue
                        attrs_list.append(string)
                    attrs = "<br>".join(attrs_list)
                    if i["Icon"]["SubKind"] != "戒指":
                        diamon_data = i["DiamonAttribute"]
                        diamon_list = []
                        logger.info(diamon_data)
                        for x in diamon_data:
                            if x["Desc"] == "atInvalid":
                                continue
                            diamon_string = re.sub(r"\d+", "?", x["Attrib"]["GeneratedMagic"])
                            diamon_list.append(diamon_string)
                        fivestone = "<br>".join(diamon_list)
                    else:
                        fivestone = "不适用"
                    max = i["MaxStrengthLevel"]
                    stars = []
                    if max != "":
                        for x in range(int(max)):
                            stars.append(star)
                        stars = "\n".join(stars)
                    else:
                        stars = "<p>不适用</p>"
                    quailty = i["Quality"]
                    equip_type = i["Icon"]["SubKind"]
                    if equip_type == "帽子":
                        score = str(int(int(quailty)*1.62))
                    elif equip_type in ["上衣", "裤子"]:
                        score = str(int(int(quailty)*1.8))
                    elif equip_type in ["腰带", "护臂", "鞋"]:
                        score = str(int(int(quailty)*1.26))
                    elif equip_type in ["项链", "腰坠", "戒指"]:
                        score = str(int(int(quailty)*0.9))
                    elif equip_type in ["投掷囊"]:
                        score = str(int(int(quailty)*1.08))
            else:
                type_ = "未知"
                flag = False
                if "Type" in list(i):
                    if i["Type"] == "Act_运营及版本道具":
                        type_ = "外观"
                        flag = True
                if flag is False:
                    type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                attrs = "不适用"
                fivestone = "不适用"
                stars = "不适用"
                quailty = "不适用"
                score = "不适用"
            table_content.append(
                Template(template_drop).render(
                    icon = icon,
                    name = name,
                    attrs = attrs,
                    type = type_,
                    stars = stars,
                    quality = quailty,
                    score = score,
                    fivestone = fivestone
                )
            )
        for i in weapons:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            type_ = i["Icon"]["SubKind"] if i["Icon"]["SubKind"] != "投掷囊" else "暗器"
            attrs_data = i["ModifyType"]
            attrs_list = []
            for x in attrs_data:
                string = x["Attrib"]["GeneratedMagic"]
                flag = False
                for y in filter_words:
                    if string.find(y) != -1:
                        flag = True
                if flag:
                    continue
                attrs_list.append(string)
            attrs = "<br>".join(attrs_list)
            diamon_data = i["DiamonAttribute"]
            diamon_list = []
            for x in diamon_data:
                if x["Desc"] == "atInvalid":
                    continue
                string = re.sub(r"\d+", "?", x["Attrib"]["GeneratedMagic"])
                diamon_list.append(string)
            fivestone = "<br>".join(diamon_list)
            max = i["MaxStrengthLevel"]
            stars = []
            if max != "":
                for x in range(int(max)):
                    stars.append(star)
                stars = "\n".join(stars)
            else:
                stars = "<p>不适用</p>"
            quailty = i["Quality"]
            score = str(int(int(quailty)*2.16))
            Template(template_drop).render(
                icon = icon,
                name = name,
                attrs = attrs,
                type = type_,
                stars = stars,
                quality = quailty,
                score = score,
                fivestone = fivestone
            )
        for i in others:
            type_ = "不适用"
            icon = i["Icon"]["FileName"]
            name = i["Name"]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            table_content.append(
                Template(template_drop).render(
                    icon = icon,
                    name = name,
                    attrs = attrs,
                    type = type_,
                    stars = stars,
                    quality = quailty,
                    score = score,
                    fivestone = fivestone
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 掉落列表 · {mode}{map} · {boss}",
                additional_css = Path(build_path(TEMPLATES, ["jx3", "drop.css"])).as_uri(),
                table_head = table_drop_head,
                table_body = "\n".join(table_content)
            )
        )
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()

async def get_zone_record_image(server: str, role: str):
    data = await search_player(role_name=role, server_name=server)
    details_data = data.format_jx3api()
    if details_data["code"] != 200:
        guid = ""
        return ["唔……获取玩家信息失败。"]
    else:
        guid = details_data["data"]["globalRoleId"]
    ts = gen_ts()
    params = {
        "globalRoleId": guid,
        "sign": dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    data = (await Request("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", params=params).post(tuilan=True)).json()
    unable = Template(image_template).render(
        image_path = build_path(ASSETS, ["jx3", "image", "cat", "grey.png"])
    )
    available = Template(image_template).render(
        image_path = build_path(ASSETS, ["jx3", "image", "cat", "gold.png"])
    )
    if data["data"] == []:
        return ["该玩家目前尚未打过任何副本哦~\n注意：10人普通副本会在周五刷新一次。"]
    else:
        contents = []
        if data is None:
            return ["获取玩家信息失败！"]
        for i in data["data"]:
            images = []
            map_name = i["mapName"]
            map_type = i["mapType"]
            for x in i["bossProgress"]:
                if x["finished"] is True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            contents.append(
                Template(template_zone_record).render(
                    zone_name = map_name,
                    zone_mode = map_type,
                    images = image_content
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 副本记录 · {server} · {role}",
                table_head = table_zone_record_head,
                table_body = "\n".join(contents)
            )
        )
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()


async def get_item_record(name: str):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.jx3mm.com/jx3fun/jevent/jcitem.html"
    }
    filter = {
        "Zone": "",
        "Srv": "",
        "Droppedi": name
    }
    base_params = {
        "sort": "Tm",
        "order": "desc",
        "limit": 30,
        "offset": 0,
        "_": int(time.time()) * 1000,
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": "{\"Zone\":\"LIKE\",\"Srv\":\"LIKE\"}"
    }
    data = (await Request("https://www.jx3mm.com/jx3fun/jevent/jcitem", headers=headers, params=base_params).get()).json()
    if data["total"] == 0:
        return ["未找到相关物品，请检查物品名称是否正确！"]
    known_time = []
    known_id = []
    table_contents = []
    num = 0
    for i in data["rows"]:
        if i["Tm"] in known_time and i["Nike"] in known_id:
            continue
        known_time.append(i["Tm"])
        known_id.append(i["Nike"])
        role = i["Nike"]
        item_name = i["Droppedi"]
        if i["Copyname"][0:2] in ["英雄", "普通"]:
            zone = "25人" + i["Copyname"]
        else:
            zone = i["Copyname"]
        catch_time = Time(i["Tm"]).format()
        if not isinstance(catch_time, str):
            return
        relate_time = Time().relate(i["Tm"])
        server = i["Srv"]
        table_contents.append(
            Template(template_item).render(
                server = server,
                name = item_name,
                map = zone,
                role = role,
                time = catch_time,
                relate = relate_time
            )
        )
        num += 1
        if num == 30:
            break  # 不限？不限给你鲨了
    html = str(
        HTMLSourceCode(
            application_name = f" · 掉落统计 · {server} · " + Time().format("%H:%M:%S"),
            table_head = table_item_head,
            table_body = "\n".join(table_contents)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
