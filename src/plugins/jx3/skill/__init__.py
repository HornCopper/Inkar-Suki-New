from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.const.jx3.kungfu import Kungfu

from .macro import get_macro

MacroMatcher = on_command("jx3_macro_v2", aliases={"宏"}, force_whitespace=True, priority=5)


@MacroMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    kungfu = Kungfu(args.extract_plain_text()).name
    if kungfu is None:
        await MacroMatcher.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(kungfu)
    await MacroMatcher.finish(data)