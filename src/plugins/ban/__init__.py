from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.permission import checker, error
from src.utils.message import preprocess

from .process import Ban

# from src.tools.config import Config
# from src.tools.utils.num import check_number
# from src.tools.permission import checker, error
# from src.tools.database import group_db, BannedList, GroupSettings
# from src.tools.basic.process import preprocess


BanMatcher = on_command("ban", force_whitespace=True, priority=5)


@BanMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await BanMatcher.finish(error(10))
    user_id = args.extract_plain_text()
    if not check_number(user_id):
        await BanMatcher.finish(PROMPT.ArgumentInvalid)    
    status = Ban(event.user_id).ban()
    if not status:
        await BanMatcher.finish(PROMPT.BanRepeatInvalid)
    await BanMatcher.finish(f"好的，音卡已经封禁({user_id})！")

UnbanMatcher = on_command("unban", force_whitespace=True, priority=5)

@UnbanMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await UnbanMatcher.finish(error(10))
    user_id = args.extract_plain_text()
    if not check_number(user_id):
        await UnbanMatcher.finish(PROMPT.ArgumentInvalid)    
    status = Ban(event.user_id).unban()
    if not status:
        await UnbanMatcher.finish(PROMPT.BanRepeatInvalid)
    await UnbanMatcher.finish(f"好的，已经全域解封({user_id})。")


@preprocess.handle()
async def _(matcher: Matcher, event: MessageEvent):
    if Ban(event.user_id).status:
        matcher.stop_propagation()