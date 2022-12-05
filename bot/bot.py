import contextlib
import time, enum, random, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from ghost_logger import GhostLogger


class DefaultLinksEnum(enum.Enum):
    home = "https://www.reddit.com/"
    login = "https://www.reddit.com/login/"


class Timeouts:
    def srt() -> None:
        """short timeout"""
        time.sleep(random.random() + random.randint(0, 2))

    def med() -> None:
        """medium timeout"""
        time.sleep(random.random() + random.randint(2, 5))

    def lng() -> None:
        """long timeout"""
        time.sleep(random.random() + random.randint(5, 10))


class RedditBot:
    def __init__(self, verbose: bool = False):
        self.logger = GhostLogger
        if verbose:
            self.verbose = True
            # configure logging
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())
            formatter = logging.Formatter(
                "\033[93m[INFO]\033[0m %(asctime)s \033[95m%(message)s\033[0m"
            )
            self.logger.handlers[0].setFormatter(formatter)

        self.logger.info("Booting up webdriver")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("log-level=3")
        chrome_options.add_argument("--lang=en")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )
        self.dv = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=r"chromedriver.exe"
        )
        self.logger.info("Webdriver booted up")

    def login(self, username: str, password: str):
        # clear data first
        self.logout()

        self.logger.info(f"Logging in as \033[4m{username}\033[0m")
        self.dv.get(DefaultLinksEnum.login.value)

        # username
        try:
            username_field = self.dv.find_element(By.NAME, "username")
        except Exception:
            WebDriverWait(self.dv, 20).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (
                        By.XPATH,
                        '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div[2]/div/iframe',
                    )
                )
            )
            username_field = self.dv.find_element(By.NAME, "username")

        for ch in username:
            username_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # password
        password_field = self.dv.find_element(By.NAME, "password")

        for ch in password:
            password_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # sign in
        with contextlib.suppress(Exception):
            password_field.send_keys(Keys.ENTER)
        Timeouts.med()

        assert "https://www.reddit.com/login" not in self.dv.current_url, "Login failed"

        self._popup_handler()
        self._cookies_handler()
        self.logger.info("Logged in successfully.")

    def logout(self) -> None:
        self.logger.info(f"Clearing browser data")

        self.dv.execute_script("window.open('');")
        self.dv.switch_to.window(self.dv.window_handles[-1])
        self.dv.get('chrome://settings/clearBrowserData')
        Timeouts.srt()

        # clear data
        actions = ActionChains(self.dv) 
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)
        actions.perform()
        Timeouts.srt()

        # confirm
        actions = ActionChains(self.dv) 
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER)
        actions.perform()
        Timeouts.med()

        # close current tab
        self.dv.close()

        # switch to the first tab
        self.dv.switch_to.window(self.dv.window_handles[0])

    def vote(self, link: str, action: bool) -> None:
        """action: True to upvote, False to downvote"""
        if action:
            self.logger.info(f"Upvoting \033[4m{link}\033[0m")
        else:
            self.logger.info(f"Downvoting \033[4m{link}\033[0m")

        self.dv.get(link)
        Timeouts.med()

        if action:
            button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div/div[1]/div/button[1]"
            )
        else:
            button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div/div[1]/div/button[2]"
            )

        button.click()
        Timeouts.med()

    def comment(self, link: str, comment: str) -> None:
        """comment: the comment to be posted"""
        self.logger.info(f"Commenting on \033[4m{link}\033[0m")

        self.dv.get(link)
        Timeouts.med()

        html_body = self.dv.find_element(By.XPATH, "/html/body")
        html_body.send_keys(Keys.PAGE_DOWN)
        Timeouts.srt()

        if comment:
            try:
                textbox = self.dv.find_element(By.XPATH,
                    "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div"
                )
            except Exception:
                textbox = self.dv.find_element(By.XPATH,
                    '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div',
                )
            textbox.click()

            for ch in comment:
                textbox.send_keys(ch)
                Timeouts.srt()

            try:
                comment_button = self.dv.find_element(By.XPATH,
                    "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/div[1]/button"
                )
            except Exception:
                comment_button = self.dv.find_element(By.XPATH,
                    '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div/div/div[3]/div[1]/button',
                )
            comment_button.click()

        Timeouts.med()

    def join_community(self, link: str, join: bool) -> None:
        """join: True to join, False to leave"""
        if join:
            self.logger.info(f"Joining \033[4m{link}\033[0m")
        else:
            self.logger.info(f"Leaving \033[4m{link}\033[0m")

        self.dv.get(link)
        Timeouts.med()

        try:
            join_button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div/div[1]/div/div[2]/div/button"
            )
        except Exception:
            join_button = self.dv.find_element(By.XPATH,
                '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[1]/div/div[1]/div/div[2]/div/button',
            )

        button_text = join_button.text.lower()

        if join and button_text == "join" or not join and button_text == "joined":
            join_button.click()
        Timeouts.med()

    def _popup_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            close_button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[1]/header/div/div[2]/div[2]/div/div[1]/span[2]/div/div[2]/button"
            )
            close_button.click()

    def _cookies_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            accept_button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div/div/div[3]/div/form/div/button"
            )
            accept_button.click()

    def _dispose(self) -> None:
        self.logger.info("Disposing webdriver")
        self.dv.quit()
