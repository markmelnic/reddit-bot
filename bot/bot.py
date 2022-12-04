import contextlib
import time, enum, random, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException


class DefaultLinksEnum(enum.Enum):
    home = "https://www.reddit.com/"
    login = "https://www.reddit.com/login/"


class Timeouts:
    def tp() -> None:
        time.sleep(random.random())
    
    def srt() -> None:
        time.sleep(random.random() + random(0, 2))

    def med() -> None:
        time.sleep(random.random() + random.randint(2, 5))

    def lng() -> None:
        time.sleep(random.random() + random.randint(5, 10))


class RedditBot:
    def __init__(self, verbose: bool = False):
        if verbose:
            logging.basicConfig(
                level=logging.INFO, format="[INFO] %(asctime)s: %(message)s"
            )

        logging.info("Booting up webdriver...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("log-level=3")
        chrome_options.add_argument("--lang=en")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )
        self.dv = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=r"chromedriver.exe"
        )
        logging.info("Webdriver booted up.")

    def login(self, username: str, password: str):
        logging.info(f"Logging in as {username}...")
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
            Timeouts.tp()
        Timeouts.med()

        # password
        password_field = self.dv.find_element(By.NAME, "password")

        for ch in password:
            password_field.send_keys(ch)
            Timeouts.tp()
        Timeouts.med()

        # sign in
        password_field.send_keys(Keys.ENTER)

        Timeouts.med()
        self._popup_handler()
        self._cookies_handler()
        logging.info("Logged in successfully.")

    def vote(self, link: str, action: bool) -> None:
        """action: True to upvote, False to downvote"""

        separator = '/?'
        cLink = link.split(separator, 1)[0]
        #finds post id
        fLast = ""
        for i in cLink[::-1]:
            if i != '/':
                fLast += i
            else:
                break
        last = fLast[::-1]

        self.dv.get(cLink)
        Timeouts.med()

        if action:
            button = self.dv.find_element(By.XPATH,
                f'//*[@id="vote-arrows-t1_{last}"]/button[1]'
            )
        else:
            button = self.dv.find_element(By.XPATH,
                f'//*[@id="vote-arrows-t1_{last}"]/button[2]'
            )

        button.click()
        Timeouts.med()

    def comment(self, link: str, comment: str) -> None:
        """comment: the comment to be posted"""

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
        self.dv.quit()
