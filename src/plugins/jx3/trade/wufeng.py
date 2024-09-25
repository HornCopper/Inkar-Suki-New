from pathlib import Path
from typing import Optional

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.path import ASSETS, build_path
from src.const.jx3.constant import server_aliases_data as servers
from src.utils.analyze import check_number
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML

from .api import coin_to_image, calculator_price, template_msgbox, template_table

import json
import re

basic_name = "无封"

def extract_numbers(string):
    pattern = r"\d+"
    numbers = re.findall(pattern, string)
    return [int(num) for num in numbers]

def convertAttrs(raw: str):
    # 手搓关键词提取
    def fd(raw: str, to: str):
        if raw.find(to) != -1:
            return True
        return False

    raw = raw.replace("攻击", "")
    raw = raw.replace("攻", "")
    raw = raw.replace("品", "")

    more = []

    # 基础类型 内外功
    if fd(raw, "外"):
        basic = "外功"
    elif fd(raw, "内"):
        basic = "内功"
    else:
        return False

    more.append(basic + "攻击")

    # 基础类型 会心 破防 无双 破招（不存在纯破招无封）
    if fd(raw, "纯会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")
    if fd(raw, "纯无"):
        more.append("无双")
    if fd(raw, "纯破"):
        more.append(basic + "破防")

    # 双会类
    if fd(raw, "双会") or fd(raw, "会心会效") or fd(raw, "会会"):
        if basic == "外功":
            more.append(basic + "会心")
            more.append(basic + "会心效果")
        else:
            more.append("全会心")
            more.append("全会心效果")

    # 双会可能出现的组合
    if fd(raw, "破") and not fd(raw, "纯破") and not fd(raw, "破招"):
        more.append(basic + "破防")
    
    if fd(raw, "招") or fd(raw, "破破"):
        more.append("破招")
    
    if fd(raw, "无") and not fd(raw, "纯无"):
        more.append("无双")
    
    # 会心
    if fd(raw, "会") and not fd(raw, "双会") and not fd(raw, "纯会") and not fd(raw, "会效") and not fd(raw, "会心会效") and not fd(raw, "会会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")

    num_list = extract_numbers(raw)
    if len(num_list) != 1:
        return False
    
    # 部位
    place = ""

    quality = num_list[0]
    
    if fd(raw, "头") or fd(raw, "帽") or fd(raw, "脑壳"):
        place = "头饰"
    elif fd(raw, "手") or fd(raw, "臂"):
        place = "护臂"
    elif fd(raw, "裤") or fd(raw, "下装"):
        place = "裤"
    elif fd(raw, "鞋") or fd(raw, "jio") or fd(raw, "脚"):
        place = "鞋"
    elif fd(raw, "链") or fd(raw, "项"):
        place = "项链"
    elif fd(raw, "坠") or fd(raw, "腰"):
        if not fd(raw, "腰带"):
            place = "腰坠"
    elif fd(raw, "暗器") or fd(raw, "囊") or fd(raw, "弓弦"):
        place = "囊"
    else:
        return False

    return [more, place, quality]

def getAttrs(data: list):
    attrs = []
    for i in data:
        if i["color"] == "green":
            label = i["label"].split("提高")
            if len(label) == 1:
                label = i["label"].split("增加")
            label = label[0].replace("等级", "").replace("值", "")
            attrs.append(label)
    return attrs

async def getData(name, quality):
    url = f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&MinLevel={quality}&MaxLevel={quality}&BindType=2"
    data = []
    getdata = (await Request(url).get()).json()
    for x in getdata["data"]["data"]:
        if str(x["Level"]) == str(quality):
            data.append(x)
    return data

async def getArmor(raw: str):
    attrs = convertAttrs(raw)
    if not attrs:
        return [f"您输入的装备词条有误，请确保包含以下四个要素：\n品级、属性、部位、内外功\n示例：13550内功双会头"]
    parsed = attrs[0]
    place = attrs[1]
    quality = attrs[2]
    final_name = basic_name + place
    data = await getData(final_name, quality)
    if len(data) == 0:
        return [f"未查找到该{basic_name}装备！"]
    else:
        for i in data:
            if set(getAttrs(i["attributes"])) == set(parsed):
                return i
        raise ValueError
            
async def getWufengImg(raw: str, server: str):
    if server == "全服":
        result = await getAllServerWufengImg(raw)
        return result
    data = await getArmor(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"] # type: ignore
    except:
        emg = (await Request("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg").get()).content
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
    logs = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}").get()).json()
    current = logs["data"]["today"]
    yesterdayFlag = False
    if current != None:
        currentStatus = 1
    else:
        if logs["data"]["yesterday"] != None:
            yesterdayFlag = True
            currentStatus = 1
            current = logs["data"]["yesterday"]
    if currentStatus:
        toReplace = [["$low", coin_to_image(str(calculator_price(current["LowestPrice"])))], ["$equal", coin_to_image(str(calculator_price(current["AvgPrice"])))], ["$high", coin_to_image(str(calculator_price(current["HighestPrice"])))]]
        msgbox = template_msgbox
        for toReplace_word in toReplace:
            msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
    else:
        msgbox = ""
    color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]]
    detailData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
    if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
        if not yesterdayFlag:
            return ["唔……该物品目前交易行没有数据。"]
        else:
            low = calculator_price(current["LowestPrice"])
            avg = calculator_price(current["AvgPrice"])
            high = calculator_price(current["HighestPrice"])
            return [f"唔……该物品目前交易行没有数据，但是音卡找到了昨日的数据：\n昨日低价：{low}\n昨日均价：{avg}\n昨日高价：{high}"]
    table = []
    icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png" # type: ignore
    name = data["Name"] # type: ignore
    for each_price in detailData["data"]["prices"]:
        table_content = template_table
        toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + "<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", coin_to_image(calculator_price(each_price["unit_price"]))]] # type: ignore
        for word in toReplace_word:
            table_content = table_content.replace(word[0], word[1])
        table.append(table_content)
        if len(table) == 12:
            break
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/trade/trade.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server} · {name}").replace("$msgbox", msgbox)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()

async def getAllServerWufengImg(raw: str):
    servers = list(json.loads(read(TOOLS + "/basic/server.json")))
    highs = []
    lows = []
    avgs = []
    table = []
    data = await getArmor(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"] # type: ignore
    except:
        emg = await get_content("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg")
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
    for server in servers:
        logs = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}")
        current = logs["data"]["today"]
        yesterdayFlag = False
        if current != None:
            currentStatus = 1
        else:
            if logs["data"]["yesterday"] != None:
                yesterdayFlag = True
                currentStatus = 1
                current = logs["data"]["yesterday"]
            else:
                yesterdayFlag = 0
                currentStatus = 0
        if currentStatus:
            highs.append(current["HighestPrice"])
            avgs.append(current["AvgPrice"])
            lows.append(current["LowestPrice"])
        else:
            highs.append(0)
            avgs.append(0)
            lows.append(0)
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]] # type: ignore
        detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
        icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png" # type: ignore
        name = data["Name"] # type: ignore
        if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
            if not yesterdayFlag:
                toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", "<span style=\"color:red\">没有数据</span>"]] # type: ignore
                table_content = template_table
                for word in toReplace_word:
                    table_content = table_content.replace(word[0], word[1])
                table.append(table_content)
                continue
            else:
                avg = calculator_price(current["AvgPrice"])
                toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", coin_to_image(avg)]] # type: ignore
                table_content = template_table
                for word in toReplace_word:
                    table_content = table_content.replace(word[0], word[1])
                table.append(table_content)
                continue
        each_price = detailData["data"]["prices"][0]
        table_content = template_table
        toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", coin_to_image(calculator_price(each_price["unit_price"]))]] # type: ignore
        for word in toReplace_word:
            table_content = table_content.replace(word[0], word[1])
        table.append(table_content)

    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    exist_info_flag = False
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
        exist_info_flag = True
    except:
        pass
    if exist_info_flag:
        toReplace = [["$low", coin_to_image(calculator_price(final_lowest))], ["$equal", coin_to_image(calculator_price(final_avg))], ["$high", coin_to_image(calculator_price(final_highest))]] # type: ignore
    else:
        toReplace = [["$low", "未知"], ["$equal", "未知"], ["$high", "未知"]]
    msgbox = template_msgbox.replace("当日", "全服")
    for toReplace_word in toReplace:
        msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/trade/trade.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · 全服 · {name}").replace("$msgbox", msgbox)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()