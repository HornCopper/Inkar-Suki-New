from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext
)
from typing import Optional
from pathlib import Path

from nonebot.log import logger

from src.utils.exceptions import BrowserNotInitializedException
from src.const.path import CACHE

import uuid
import asyncio
import time

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")

class ScreenshotGenerator:
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None

    def __init__(
            self, 
            path: str,
            web: bool = False, 
            locate: str = "", 
            first: bool = False, 
            delay: int = 0, 
            additional_css: str = "", 
            additional_js: str = "",
            viewport: dict = {}, 
            full_screen: bool = False, 
            hide_classes: list = [],
            device_scale_factor: float = 1.0,
            output_path: str = "",
        ):

        self.path = Path(path).as_uri() if not web else path
        self.web = web
        self.locate = locate
        self.first = first
        self.delay = delay
        self.additional_css = additional_css or ""
        self.additional_js = additional_js or ""
        self.viewport = viewport
        self.full_screen = full_screen
        self.hide_classes = hide_classes
        self.device_scale_factor = device_scale_factor
        self.output_path = output_path
        self.uuid = get_uuid()

    @classmethod
    async def _launch_browser(cls, playwright):
        if cls._browser is None:
            cls._browser = await playwright.chromium.launch(headless=True, slow_mo=0)

    @classmethod
    async def _setup_context(cls):
        if cls._browser is None:
            raise BrowserNotInitializedException()
        if cls._context is None:
            cls._context = await cls._browser.new_context(device_scale_factor=1.0)

    @classmethod
    async def _close_browser(cls):
        if cls._context:
            await cls._context.close()
            cls._context = None
        if cls._browser:
            await cls._browser.close()
            cls._browser = None

    async def _setup_page(self):
        if not isinstance(self._context, BrowserContext):
            raise BrowserNotInitializedException()
        page = await self._context.new_page()
        await page.goto(self.path)
        return page

    async def _apply_customizations(self, page):
        if self.delay > 0:
            await asyncio.sleep(self.delay / 1000)
        if self.web:
            if self.additional_css:
                await page.add_style_tag(content=self.additional_css)
        if self.additional_js:
            await page.evaluate(self.additional_js)
        if self.hide_classes:
            await self._hide_elements_by_class(page)

    async def _hide_elements_by_class(self, page):
        if self.hide_classes:
            combined_selector = ', '.join(f'.{cls}' for cls in self.hide_classes)
            await page.evaluate(f"document.querySelectorAll('{combined_selector}').forEach(el => el.style.display = 'none')")

    async def _capture_element_screenshot(self, locator, store_path):
        if self.first:
            locator = locator.first
        await locator.screenshot(path=store_path)

    async def _capture_full_screenshot(self, page, store_path):
        await page.screenshot(path=store_path, full_page=self.full_screen)

    async def _save_screenshot(self, page, store_path):
        store_path = f"{CACHE}/{self.uuid}.png" if not store_path else store_path
        if self.locate:
            locator = page.locator(self.locate)
            await self._capture_element_screenshot(locator, store_path)
        else:
            await self._capture_full_screenshot(page, store_path)
        return store_path

    async def generate(self):
        try:
            time_start = time.time()
            logger.opt(colors=True).info(f"<green>Generating source: {self.path}</green>")

            async with async_playwright() as p:
                await self._launch_browser(p)
                await self._setup_context()
                page = await self._setup_page()
                await self._apply_customizations(page)
                store_path = await self._save_screenshot(page, self.output_path)

            time_end = time.time()
            logger.opt(colors=True).info(f"<green>Generated successfully: {store_path}, spent {round(time_end - time_start, 2)}s</green>")
            return store_path

        except Exception as ex:
            logger.error(f"图片生成失败，请尝试执行 `playwright install`！: {ex}")
            return False

    @classmethod
    async def close(cls):
        await cls._close_browser()

async def generate(
    path: str,
    web: bool = False,
    locate: str = "",
    first: bool = False,
    delay: int = 0,
    additional_css: str = "",
    additional_js: str = "",
    viewport: dict = {},
    full_screen: bool = False,
    hide_classes: list = [],
    device_scale_factor: float = 1.0,
    output: str = ""
):
    generator = ScreenshotGenerator(path, web, locate, first, delay, additional_css, additional_js, viewport, full_screen, hide_classes, device_scale_factor, output)
    return await generator.generate()
