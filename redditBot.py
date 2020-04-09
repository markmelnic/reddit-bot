
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.chrome.options
import random
import time


#================== special elements ===================#
# random elements
class rds:
    def srt(): #short timer
        return time.sleep((random.random() / 1.5) + (random.randint(0, 1) / 5))
    def med(): #medium timer
        return time.sleep(random.random() + (random.randint(1, 2) / 1.5))
    def long(): #long timer
        return time.sleep(random.random() + random.randint(2, 5))
    def very(): #very long timer
        return time.sleep(random.random() + random.randint(4, 10))


# ================== driver procedure ===================#
# driver boot procedure
def boot():
    # manage notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)

    # driver itself
    dv = webdriver.Chrome(chrome_options = chrome_options, executable_path = r"C:\Users\markh\source\repos\redditBot\drivers\chromedriver80.exe")
    return dv

# kill the driver
def killb(dv):
    #print("|-----------Killing the Driver-----------|")
    dv.quit()

def cookiesHandler():
    try:
        acceptCookies = dv.find_element_by_xpath("/html/body/div[1]/div/div/div/div[3]/div/form/div/button")
        acceptCookies.click()
    except:
        None

# login protocol
def loginProc(dv, username, password):
    dv.get(login_link)
    rds.long()

    # username
    try:
        loginUsername = dv.find_element_by_name("username")
    except:
        WebDriverWait(dv, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//*[@id=\"SHORTCUT_FOCUSABLE_DIV\"]/div[3]/div[2]/div/iframe")))
        loginUsername = dv.find_element_by_name("username")

    for i in range(len(username)):
        loginUsername.send_keys(username[i])
        rds.srt()
    rds.med()

    # password
    loginPassword = dv.find_element_by_name("password")
    for i in range(len(password)):
        loginPassword.send_keys(password[i])
        rds.srt()
    rds.med()

    # sign in
    signInClick = dv.find_element_by_xpath("/html/body/div/div/div[2]/div/form/fieldset[5]/button")
    signInClick.click()
    rds.long()

    """
    #coming out of the iframe if needed
    try:
        windowChecker = dv.find_element_by_xpath("/html/body")
    except:
        dv.switch_to.default_content()
    """

# upvoter
def upvoter(dv, action_link):
    rds.med()
    dv.get(action_link)
    rds.long()
    # cookiesHandler()
    """
    try:
        login_button = dv.find_element_by_xpath("/html/body/div[1]/div/div/div/div[1]/header/div/div[2]/div/div[1]/a[1]")
        login_button.click()
    except:
        None
    """

    rds.med()
    try:
        upvote_button = dv.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div/div[1]/div/button[1]/span/i")
        upvote_button.click()
    except:
        upvote_button = dv.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div[1]/div[1]")
        upvote_button.click()
    else:
        None
    rds.med()

#downvoter
def downvoter(dv, action_link):
    dv.get(action_link)
    rds.long()
    cookiesHandler()
    try:
        login_button = dv.find_element_by_xpath("/html/body/div[1]/div/div/div/div[1]/header/div/div[2]/div/div[1]/a[1]")
        login_button.click()
    except:
        None
    
    rds.med()
    downvote_button = dv.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div[1]/div[5]")
    downvote_button.click()
    rds.med()


#==================== data ===================#
# links
login_link = "https://www.reddit.com/login/"
action_link = "https://www.reddit.com/r/TrollYChromosome/comments/fdxd0z/not_my_meme_but_we_seriously_need_to_recognise/?utm_source=share&utm_medium=web2x"

# define credentials
def credentials():
    credentials = open("credentials.txt", "r")
    creds = []
    for line in credentials:
        creds.append(line.strip())
    return creds