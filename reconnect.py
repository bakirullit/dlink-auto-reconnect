import time
import unicodedata
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load env
load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")
NETWORK_NAME = os.getenv("NETWORK_NAME", "Erilium")
URL = "http://192.168.0.1"
CHECK_INTERVAL = 15  # seconds

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Selenium setup
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

def login():
    try:
        driver.get(URL)
        try:
            driver.find_element(By.NAME, "login_name").send_keys(ADMIN_USER)
            driver.find_element(By.NAME, "login_password").send_keys(ADMIN_PASS)
            driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class,'colored')]").click()
            time.sleep(2)
        except:
            logging.info("Login elements not found, possibly already logged in.")
        driver.find_element(By.CLASS_NAME, "go_to_menu").click()
        time.sleep(1)
        wifi_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Wi-Fi')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", wifi_span)
        client_link = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@ui-sref='wifi.client']"))
        )
        driver.execute_script("arguments[0].click();", client_link)
        time.sleep(2)
        logging.info("Logged in and navigated to Wi-Fi client page")
    except Exception as e:
        logging.warning(f"Login failed: {e}")

def is_connected():
    try:
        status = driver.find_element(By.XPATH, "//span[@class='info ng-binding']").text.strip().lower()
        normalized = unicodedata.normalize("NFKD", status).replace("с", "c")
        return normalized == "connected"
    except:
        return False

def update_network_list():
    try:
        update_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Update list')]")
        if 'disabled' not in update_btn.get_attribute('class'):
            driver.execute_script("arguments[0].click();", update_btn)
            logging.info("Network list updated")
            time.sleep(2)
        else:
            logging.debug("Update list button disabled")
    except:
        logging.warning("Update list button not found, retrying login...")
        login()

def connect_to_network():
    while True:
        try:
            td = driver.find_element(By.XPATH, f"//td[contains(text(), '{NETWORK_NAME}')]")
            driver.execute_script("arguments[0].click();", td)
            logging.info(f"{NETWORK_NAME} clicked")

            reconnect_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@ng-bind,'wifi_client')]"))
            )
            driver.execute_script("arguments[0].click();", reconnect_btn)
            logging.info("Reconnect clicked, waiting for status...")

            start = time.time()
            while time.time() - start < 60:
                if is_connected():
                    logging.info(f"{NETWORK_NAME} successfully connected")
                    return
                time.sleep(2)
            return
        except:
            logging.info(f"{NETWORK_NAME} not found, refreshing list...")
            update_network_list()
            time.sleep(5)

def main():
    while True:
        login()
        if is_connected():
            logging.info("Already connected")
        else:
            logging.warning("Not connected, attempting reconnect...")
            connect_to_network()
        logging.info("Sleeping until next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()