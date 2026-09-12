"""Comment action — post a comment on a Reddit post."""

from __future__ import annotations

import contextlib
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .base import BaseAction, ActionResult
from bot.utils.timeouts import Timeouts


class CommentAction(BaseAction):
    name = "comment"

    def execute(self, link: str = "", text: str = "", **kwargs: Any) -> ActionResult:
        if not text:
            print(f">>> [REDDIT BOT] Error: No comment text provided for link: {link}", flush=True)
            return ActionResult(success=False, action="comment", link=link, message="No comment text provided")

        print(f"\n==================================================", flush=True)
        print(f">>> [REDDIT BOT] STARTING COMMENT ACTION", flush=True)
        print(f">>> Link: {link}", flush=True)
        print(f">>> Comment Text: '{text}'", flush=True)
        print(f"==================================================\n", flush=True)

        self.logger.info(f"Commenting on {link} with text: '{text}'")

        if self.config.dry_run:
            print(f">>> [REDDIT BOT] DRY RUN: Would post comment '{text}'", flush=True)
            return ActionResult(success=True, action="comment", link=link, message=f"Dry run: would comment '{text[:50]}...'")

        self._navigate(link)
        Timeouts.med()
        self._handle_nsfw()

        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        Timeouts.srt()

        textbox = self._find_with_fallbacks(
            (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"),
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div"),
            (By.XPATH, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div'),
        )
        self._click(textbox)
        self._type_like_human(textbox, text)

        submit_btn = self._find_with_fallbacks(
            (By.CSS_SELECTOR, "button[type='submit'][slot='submit-button']"),
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/div[1]/button"),
            (By.XPATH, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/div[1]/button'),
        )
        self._click(submit_btn)
        Timeouts.med()

        print(f"\n==================================================", flush=True)
        print(f">>> [REDDIT BOT] SUCCESS: Comment posted successfully!", flush=True)
        print(f">>> Link: {link}", flush=True)
        print(f">>> Comment: '{text}'", flush=True)
        print(f"==================================================\n", flush=True)

        return ActionResult(success=True, action="comment", link=link, message="Comment posted")

    def _handle_nsfw(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            btn = self.driver.find_element(
                By.CSS_SELECTOR, "button.nsfw-gate-btn, button[name='over18']"
            )
            btn.click()
            Timeouts.srt()
