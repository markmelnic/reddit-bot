"""Core Reddit bot — orchestrates browser, actions, and all features."""

from __future__ import annotations

import contextlib
import enum
import logging
import os
import random
import time
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from .config import BotConfig
from .ghost_logger import GhostLogger
from .database import BotDatabase
from .reporting import ExecutionSummary
from .actions.base import ActionResult
from .actions.registry import ActionRegistry
from .utils.timeouts import Timeouts
from .utils.retry import retry_action
from .utils.user_agents import get_random_user_agent
from .utils.proxy import load_proxies, get_next_proxy
from .utils.validators import validate_reddit_url


class DefaultLinksEnum(enum.Enum):
    HOME = "https://www.reddit.com/"
    LOGIN = "https://www.reddit.com/login/"


class RedditBot:
    """Feature-rich Reddit automation bot.

    Supports context manager usage:
        with RedditBot(config) as bot:
            bot.login(username, password)
            result = bot.perform_action("upvote", link="...")
    """

    def __init__(self, config: Optional[BotConfig] = None, verbose: bool = False):
        self.config = config or BotConfig(verbose=verbose)
        self.summary = ExecutionSummary()
        self.db: Optional[BotDatabase] = None
        self._current_account: Optional[str] = None

        # Logger setup
        if self.config.verbose:
            self.logger = logging.getLogger("reddit-bot")
            self.logger.setLevel(logging.INFO)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "\033[93m[INFO]\033[0m %(asctime)s \033[95m%(message)s\033[0m"
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = GhostLogger()

        # Database
        self.db = BotDatabase(self.config.db_path)

        # Proxy setup
        if self.config.proxy.enabled and self.config.proxy.proxy_list_path:
            load_proxies(self.config.proxy.proxy_list_path)
            self.logger.info("Proxies loaded")

        # Screenshot directory
        if self.config.screenshot_on_failure:
            Path(self.config.screenshot_dir).mkdir(parents=True, exist_ok=True)

        # Session directory
        if self.config.session_persistence:
            Path(self.config.session_dir).mkdir(parents=True, exist_ok=True)

        # Initialize webdriver
        self._init_driver()

    def _init_driver(self) -> None:
        """Initialize Chrome webdriver with undetected-chromedriver to bypass Cloudflare/bot detection."""
        self.logger.info("Booting up undetected webdriver")
        print(f">>> [REDDIT BOT] Booting up undetected-chromedriver to bypass Cloudflare...", flush=True)
        
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        options.add_argument("--lang=en")
        
        # Headless mode
        if self.config.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        # User-Agent rotation
        if self.config.rotate_user_agent:
            ua = get_random_user_agent()
            options.add_argument(f"--user-agent={ua}")
            self.logger.info(f"Using user agent: {ua[:60]}...")

        # Proxy
        proxy = get_next_proxy() if self.config.proxy.enabled else None
        if proxy:
            options.add_argument(proxy.chrome_arg)
            self.logger.info(f"Using proxy: {proxy.address}")

        try:
            self.dv = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            print(f">>> [REDDIT BOT] Undetected Chromedriver booted successfully", flush=True)
        except Exception as e:
            print(f">>> [REDDIT BOT] Failed to boot uc.Chrome: {e}, falling back to standard selenium", flush=True)
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--lang=en")
            if self.config.headless:
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
            self.dv = webdriver.Chrome(service=service, options=chrome_options)

        self.logger.info("Webdriver booted up")

    def __enter__(self) -> "RedditBot":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.dispose()
        return False

    # ─── Authentication ──────────────────────────────────────────

    def login(self, username: str, password: str) -> None:
        """Log into a Reddit account."""
        self.logout()
        self._current_account = username

        self.logger.info(f"Logging in as {username}")
        print(f">>> [REDDIT BOT] Navigating to login page...", flush=True)
        self.dv.get(DefaultLinksEnum.LOGIN.value)
        Timeouts.med()

        def find_element_with_all_fallbacks(selectors, max_wait=20):
            start = time.time()
            while time.time() - start < max_wait:
                # 1. Try in default main frame
                for by, selector in selectors:
                    try:
                        el = self.dv.find_element(by, selector)
                        if el.is_displayed():
                            return el, None
                    except Exception:
                        continue
                
                # 2. Try inside iframes
                try:
                    iframes = self.dv.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        try:
                            self.dv.switch_to.frame(iframe)
                            for by, selector in selectors:
                                try:
                                    el = self.dv.find_element(by, selector)
                                    if el.is_displayed():
                                        return el, iframe
                                except Exception:
                                    continue
                        except Exception:
                            pass
                        finally:
                            self.dv.switch_to.default_content()
                except Exception:
                    pass
                
                time.sleep(1)
            return None, None

        # Username field
        username_selectors = [
            (By.NAME, "username"),
            (By.ID, "loginUsername"),
            (By.ID, "login-username"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "input[name='username']"),
            (By.XPATH, "//input[@type='text']"),
            (By.XPATH, "//input[@type='email']"),
        ]

        print(f">>> [REDDIT BOT] Searching for username field with advanced fallback search...", flush=True)
        username_field, u_iframe = find_element_with_all_fallbacks(username_selectors, max_wait=20)
        
        if not username_field:
            print(f">>> [REDDIT BOT] Error: Username field not found anywhere on the page!", flush=True)
            print(f">>> [REDDIT BOT] Current URL: {self.dv.current_url}", flush=True)
            print(f">>> [REDDIT BOT] Page Title: {self.dv.title}", flush=True)
            try:
                inputs = self.dv.execute_script("""
                    var elms = document.getElementsByTagName('input');
                    var res = [];
                    for(var i=0; i<elms.length; i++) {
                        res.push({
                            id: elms[i].id,
                            name: elms[i].name,
                            type: elms[i].type,
                            placeholder: elms[i].placeholder,
                            className: elms[i].className
                        });
                    }
                    return JSON.stringify(res);
                """)
                print(f">>> [REDDIT BOT] Main page inputs: {inputs}", flush=True)
            except Exception as js_err:
                print(f">>> [REDDIT BOT] Could not extract inputs: {js_err}", flush=True)
            raise RuntimeError("Username field not found on page.")

        # Switch to correct frame
        if u_iframe:
            print(f">>> [REDDIT BOT] Username field is in an iframe, switching to it...", flush=True)
            self.dv.switch_to.frame(u_iframe)
        else:
            print(f">>> [REDDIT BOT] Username field is on the main page.", flush=True)
            self.dv.switch_to.default_content()

        print(f">>> [REDDIT BOT] Typing username...", flush=True)
        for ch in username:
            username_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # Switch back to default content to search for password field (just in case)
        self.dv.switch_to.default_content()

        # Search for password field
        password_selectors = [
            (By.NAME, "password"),
            (By.ID, "loginPassword"),
            (By.ID, "login-password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
            (By.XPATH, "//input[@type='password']"),
        ]

        print(f">>> [REDDIT BOT] Searching for password field with advanced fallback search...", flush=True)
        password_field, p_iframe = find_element_with_all_fallbacks(password_selectors, max_wait=15)

        if not password_field:
            print(f">>> [REDDIT BOT] Error: Password field not found anywhere on the page!", flush=True)
            raise RuntimeError("Password field not found on page.")

        if p_iframe:
            print(f">>> [REDDIT BOT] Password field is in an iframe, switching to it...", flush=True)
            self.dv.switch_to.frame(p_iframe)
        else:
            print(f">>> [REDDIT BOT] Password field is on the main page.", flush=True)
            self.dv.switch_to.default_content()

        print(f">>> [REDDIT BOT] Typing password...", flush=True)
        for ch in password:
            password_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # Submit
        print(f">>> [REDDIT BOT] Submitting login form...", flush=True)
        with contextlib.suppress(Exception):
            password_field.send_keys(Keys.ENTER)
        Timeouts.med()

        # Always switch back to default content after typing/submitting
        self.dv.switch_to.default_content()

        if "login" in self.dv.current_url:
            print(f">>> [REDDIT BOT] Login failed, still on login page. Current URL: {self.dv.current_url}", flush=True)
            raise RuntimeError(f"Login failed for user: {username}")

        print(f">>> [REDDIT BOT] Login successful! Handling popups...", flush=True)
        self._popup_handler()
        self._cookies_handler()

        # Save session if persistence is enabled
        if self.config.session_persistence:
            print(f">>> [REDDIT BOT] Saving session...", flush=True)
            self._save_session(username)

        print(f">>> [REDDIT BOT] Login sequence completed.", flush=True)
        self.logger.info("Logged in successfully.")

    def login_with_session(self, username: str) -> bool:
        """Attempt to restore a saved session. Returns True if successful."""
        if not self.config.session_persistence:
            return False

        session_file = Path(self.config.session_dir) / f"{username}.cookies"
        if not session_file.exists():
            return False

        self.logger.info(f"Restoring session for {username}")
        # Load robots.txt first to set cookies without triggering dynamic bot checks on home page
        try:
            self.dv.get("https://www.reddit.com/robots.txt")
        except Exception:
            try:
                self.dv.get(DefaultLinksEnum.HOME.value)
            except Exception:
                pass
        Timeouts.srt()

        import json
        with open(session_file, "r") as f:
            cookies = json.load(f)

        for cookie in cookies:
            if "domain" not in cookie or not cookie["domain"]:
                cookie["domain"] = ".reddit.com"
            with contextlib.suppress(Exception):
                self.dv.add_cookie(cookie)

        # Now navigate to the actual Home page with the cookies already sent in the request header!
        try:
            self.dv.get(DefaultLinksEnum.HOME.value)
        except Exception:
            pass
        Timeouts.med()

        # Verify login
        current_url = self.dv.current_url
        if "login" not in current_url:
            self._current_account = username
            self.logger.info("Session restored successfully.")
            return True

        self.logger.info("Session expired, need fresh login.")
        return False

    def logout(self) -> None:
        """Clear browser data between accounts."""
        self.logger.info("Clearing browser data")
        with contextlib.suppress(Exception):
            self.dv.delete_all_cookies()
        with contextlib.suppress(Exception):
            self.dv.execute_script("window.localStorage.clear();")
        with contextlib.suppress(Exception):
            self.dv.execute_script("window.sessionStorage.clear();")

    # ─── Action Execution ────────────────────────────────────────

    def perform_action(self, action_name: str, **kwargs) -> ActionResult:
        """Execute a named action with retry logic, validation, and tracking.

        This is the primary method for executing any bot action.
        """
        link = kwargs.get("link", "")

        # URL validation
        if link and not validate_reddit_url(link) and action_name not in ("update_bio", "dm"):
            self.logger.warning(f"Invalid Reddit URL: {link}")

        # Duplicate check
        if self.db and self._current_account:
            if self.db.was_action_performed(self._current_account, action_name, link):
                msg = f"Action already performed by {self._current_account}"
                self.logger.info(msg)
                result = ActionResult(success=True, action=action_name, link=link, message=msg)
                self.summary.add(result)
                return result

        # Quota check
        if self.config.rate_limit.daily_action_quota > 0 and self.db and self._current_account:
            count = self.db.get_daily_action_count(self._current_account)
            if count >= self.config.rate_limit.daily_action_quota:
                msg = f"Daily quota ({self.config.rate_limit.daily_action_quota}) reached for {self._current_account}"
                self.logger.warning(msg)
                result = ActionResult(success=False, action=action_name, link=link, message=msg)
                self.summary.add(result)
                return result

        # Execute with retry
        registry = ActionRegistry(self.dv, self.config, self.logger)
        result = self._execute_with_retry(registry, action_name, **kwargs)

        # Log to database
        if self.db and self._current_account:
            screenshot_path = None
            if not result.success and self.config.screenshot_on_failure:
                screenshot_path = self._take_screenshot(action_name, link)
                result.screenshot_path = screenshot_path

            self.db.log_action(
                account=self._current_account,
                action=action_name,
                link=link,
                success=result.success,
                error_message=result.message if not result.success else None,
                screenshot_path=screenshot_path,
            )

        self.summary.add(result)

        # Rate limiting delay between actions
        Timeouts.custom(
            self.config.rate_limit.min_action_delay,
            self.config.rate_limit.max_action_delay,
        )

        return result

    def _execute_with_retry(self, registry: ActionRegistry, action_name: str, **kwargs) -> ActionResult:
        """Execute an action with retry on failure."""
        last_result = None
        for attempt in range(3):
            result = registry.execute(action_name, **kwargs)
            if result.success:
                return result
            last_result = result
            if attempt < 2:
                delay = 2.0 * (2 ** attempt)
                self.logger.warning(
                    f"Action '{action_name}' failed (attempt {attempt + 1}/3): {result.message}. "
                    f"Retrying in {delay:.0f}s..."
                )
                time.sleep(delay)
        return last_result

    # ─── Legacy convenience methods (delegate to perform_action) ─

    def vote(self, link: str, action: bool) -> ActionResult:
        """Upvote or downvote a post."""
        return self.perform_action("upvote" if action else "downvote", link=link)

    def comment(self, link: str, text: str) -> ActionResult:
        """Post a comment on a post."""
        return self.perform_action("comment", link=link, comment=text)

    def join_community(self, link: str, join: bool) -> ActionResult:
        """Join or leave a community."""
        return self.perform_action("join" if join else "leave", link=link)

    # ─── Utility ─────────────────────────────────────────────────

    def _save_session(self, username: str) -> None:
        """Save cookies to disk for session persistence."""
        import json
        cookies = self.dv.get_cookies()
        session_file = Path(self.config.session_dir) / f"{username}.cookies"
        with open(session_file, "w") as f:
            json.dump(cookies, f)

    def _take_screenshot(self, action: str, link: str) -> str:
        """Capture a screenshot on failure."""
        import re
        safe_name = re.sub(r'[^\w\-.]', '_', f"{action}_{link[:50]}")
        ts = int(time.time())
        path = str(Path(self.config.screenshot_dir) / f"{safe_name}_{ts}.png")
        try:
            self.dv.save_screenshot(path)
            self.logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""
        return path

    def _popup_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            btn = self.dv.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
            btn.click()
        with contextlib.suppress(NoSuchElementException):
            btn = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[1]/header/div/div[2]/div[2]/div/div[1]/span[2]/div/div[2]/button"
            )
            btn.click()

    def _cookies_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            btn = self.dv.find_element(By.CSS_SELECTOR, "button[name='accept']")
            btn.click()
        with contextlib.suppress(NoSuchElementException):
            btn = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div/div/div[3]/div/form/div/button"
            )
            btn.click()

    def reinit_driver(self) -> None:
        """Reinitialize the webdriver (e.g., for proxy rotation per account)."""
        self.logger.info("Reinitializing webdriver for new session")
        try:
            self.dv.quit()
        except Exception:
            pass
        self._init_driver()

    def dispose(self) -> None:
        """Shut down the webdriver and close the database."""
        self.summary.finalize()
        self.logger.info("Disposing webdriver")
        try:
            self.dv.quit()
        except Exception:
            pass
        if self.db:
            self.db.close()
