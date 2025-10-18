import json, os
import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from loguru import logger

def set_cookies(browser: webdriver.Chrome):
    with open("../json/cookies.json", "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        # выпиливаем, т.к. вызывает оооочень много проблем..
        cookie.pop("sameSite", None)
        browser.add_cookie(cookie)

def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")

    if os.getenv('NO_GUI').lower() == 'true':
        chrome_options.add_argument("--headless")
        logger.warning("Running in headless mode!")
    
    proxy = os.getenv('PROXY', None)
    if proxy is not None:
        chrome_options.add_argument(f"--proxy-server={proxy}")
        logger.info("⚡ Proxy enabled: " + proxy)
    
    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, config.WD_WAIT_TIMEOUT)

    return browser, wait

def get_all_chats(browser: webdriver.Chrome, wait: WebDriverWait):
    pre_count = -1 # for check counter
    while True:
        div_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config.FIRSTNAME_SELECTOR)))
        
        current_count = len(div_list)
        logger.trace(f"🔎 Found {current_count} elements.")

        if current_count == pre_count:
            logger.debug("😶 New elements not found. Finishing loop..")
            return div_list

        pre_count = current_count

        last_item = div_list[-1]
        logger.trace("🧭 Scrolling chat list..")
        browser.execute_script("arguments[0].scrollIntoView(true);", last_item)

        try:
            wait.until(lambda drv: len(drv.find_elements(By.CSS_SELECTOR, config.FIRSTNAME_SELECTOR)) > current_count)
        except:
            logger.trace("⏰ Timeout! Returning..")
            return div_list

def get_username(wait: WebDriverWait, pre_username: str = None):

    def username_changed(driver):
        el = driver.find_element(By.CSS_SELECTOR, config.USERNAME_SELECTOR)
        text = el.text.strip()
        return text if text and text != pre_username else False
    
    return wait.until(username_changed)

def get_friends_config():
    with open("./config/friends.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return {item["username"]: item["message"] for item in data}

def send_message(wait: WebDriverWait, text: str):
    input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.INPUT_FIELD_SELECTOR)))

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config.INPUT_FIELD_SELECTOR)))
    ActionChains(wait._driver).move_to_element(input_field).click().perform()
    logger.trace("👆 Input field was clicked.")

    input_field.send_keys(text)
    logger.trace(f"⌨️ Message was typed: [{text}]")

    input_field.send_keys(Keys.RETURN)
    logger.trace("◀️ Return was pressed.")