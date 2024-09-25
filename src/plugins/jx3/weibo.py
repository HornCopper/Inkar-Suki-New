from playwright.async_api import Response, Browser
from datetime import datetime, timedelta
from nonebot.log import logger

from src.utils.database.operation import send_subscribe

import asyncio

def trim_to_last_period(s: str) -> str:
    return s[:s.rfind("。") + 1] if "。" in s else s

def check_time(timestamp: str) -> bool:
    given_time = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %z %Y")
    now = datetime.now(given_time.tzinfo)
    time_difference = now - given_time
    return time_difference > timedelta(hours=2)

async def execute_on_new_post(post):
    data = trim_to_last_period(post.get("text_raw"))
    logger.info({"data": data})
    await send_subscribe("咸鱼", data)

async def poll_weibo_api(browser: Browser | None, uid: str, interval=60):
    """
    轮询微博。

    Args:
        browser (Browser): 浏览器实例，可从`ScreenshotGenerator`类中获得类变量传入。
        uid (str): 微博用户`UID`。
        interval: 请求间隔，默认为`1分钟`（60，单位`second`）。

    Returns:
        None. 可在函数内调用`execute_on_new_post`异步函数进行发送订阅。
    """
    if browser is None:
        await asyncio.sleep(5)
    page = await browser.new_page() # type: ignore
    logger.info("Start to monitor weibo.com.")
    last_seen_id = None
    while True:
        logger.info("Fetching API of weibo.com......")
        try:
            await page.goto("https://weibo.com")
            await page.wait_for_timeout(5000)
            response = await page.goto(f"https://weibo.com/ajax/statuses/mymblog?uid={uid}")
            if not isinstance(response, Response):
                continue
            data = await response.json()
            if "data" in data and "list" in data["data"]:
                posts = data["data"]["list"]
                if posts:
                    latest_post = posts[0]
                    post_id = latest_post.get("idstr")
                    if last_seen_id != post_id and not check_time(latest_post.get("created_at")):
                        await execute_on_new_post(latest_post)
                        last_seen_id = post_id
                else:
                    logger.info("Fetch completed, no new data!")
            else:
                logger.error("Fetch completed, no data returned!")
                
        except Exception as e:
            logger.error("Fetch failed, check the network!")
        
        await asyncio.sleep(interval)