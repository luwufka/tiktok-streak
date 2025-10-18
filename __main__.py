import os, sys
import utils, config
import time
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from colorama import Fore

load_dotenv() # * get env variables

# * set logging level
logger.remove()
logger.add(sys.stderr, level=os.getenv('LOG_LEVEL', 'INFO'))

def prepare():
    # > init browser
    logger.info("🔧 Initializing Selenium...")
    browser, wait = utils.get_browser()
    logger.success("✅ Selenium is ready!")

    # > visit login page (to apply cookie)
    logger.info("🌐 Loading page...")
    browser.get(config.LOGIN_PAGE_URL)

    # > set cookie
    logger.info("🍪 Applying cookies...")
    utils.set_cookies(browser)
    logger.success("✅ Cookies applied!")
    
    # > verify login
    browser.get(config.MESSAGES_PAGE_URL)

    if browser.current_url == config.MESSAGES_PAGE_URL:
        logger.success("🎉 Logged in successfully")
    else:
        logger.error("❌ Login failed! Check your cookies.")

    return browser, wait

if __name__ == '__main__':
    # * prepare: init selenium, set cookies and etc.
    browser, wait = prepare()

    last_run_date = None # last run day

    logger.info("⏳ Waiting for trigger time...")

    while True:
        # ! > verify time
        now = datetime.now()
        today = now.date()
        time_str = now.strftime("%H:%M")

        # not trigger time
        if time_str != os.getenv("TRIGGER_TIME", "00:00"):
            time.sleep(config.TRIGGER_CHECK_TIMEOUT)
            continue
        
        # is already was repeated on this day.
        if last_run_date == today:
            time.sleep(config.TRIGGER_CHECK_TIMEOUT)
            continue
        
        last_run_date = today # set last run date

        # > get all chats
        logger.info("💬 Fetching available chats...")

        try:
            chats = utils.get_all_chats(browser, wait)
            if len(chats) == 0:
                Exception("chats is empty. what?!")
        except Exception as e:
            logger.error("❌ Chats not found.")
            print(f"{Fore.WHITE}{e}{Fore.RESET}")
            # break

        logger.success(f"✅ Found {len(chats)} chats.")
        logger.info("👥 Loading friends config...")
        friends_cfg = utils.get_friends_config()
        logger.success(f"✅ Loaded {len(friends_cfg)} friends.")
        
        # > enum chats
        pre_username = None
        for chat in chats:
            # > open chat
            chat.click()

            # > try get username
            try:
                pre_username = utils.get_username(wait, pre_username)
                if pre_username is None:
                    Exception("username is null. what?!")
                    continue
            except Exception as e:
                logger.error("❌ Unable to get username. Skipping chat..")
                print(f"{Fore.WHITE}{e}{Fore.RESET}")
                continue
            
            # > send message to friend
            if pre_username in friends_cfg:
                utils.send_message(wait, friends_cfg[pre_username])
                logger.success(f"📩 Message sent to {pre_username}!")