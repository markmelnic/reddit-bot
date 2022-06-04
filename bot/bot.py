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
    def srt() -> None:
        time.sleep(random.random() + random.randint(0, 2))

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
            username_field = self.dv.find_element_by_name("username")
        except:
            WebDriverWait(self.dv, 20).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (
                        By.XPATH,
                        '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div[2]/div/iframe',
                    )
                )
            )
            username_field = self.dv.find_element_by_name("username")

        for ch in username:
            username_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # password
        password_field = self.dv.find_element_by_name("password")

        for ch in password:
            password_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # sign in
        try:
            signin_button = self.dv.find_element_by_xpath(
                "/html/body/div/div/div[2]/div/form/fieldset[5]/button"
            )
            signin_button.click()
        except:
            html_body = self.dv.find_element_by_xpath("/html/body")
            html_body.send_keys(Keys.ENTER)

        Timeouts.med()
        self._popup_handler()
        self._cookies_handler()
        logging.info("Logged in successfully.")

    def vote(self, action: bool, link: str):
        """action: True to upvote, False to downvote"""

        self.dv.get(link)
        Timeouts.med()

        if action:
            button = self.dv.find_element_by_xpath(
                "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div/div[1]/div/button[1]"
            )
        else:
            button = self.dv.find_element_by_xpath(
                "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div/div[1]/div/button[2]"
            )

        button.click()
        Timeouts.med()

    def _popup_handler(self):
        try:
            close_button = self.dv.find_element_by_xpath(
                "/html/body/div[1]/div/div[2]/div[1]/header/div/div[2]/div[2]/div/div[1]/span[2]/div/div[2]/button"
            )
            close_button.click()
        except NoSuchElementException:
            pass

    def _cookies_handler(self):
        try:
            accept_button = self.dv.find_element_by_xpath(
                "/html/body/div[1]/div/div/div/div[3]/div/form/div/button"
            )
            accept_button.click()
        except NoSuchElementException:
            pass

    def _dispose(self):
        self.dv.quit()
