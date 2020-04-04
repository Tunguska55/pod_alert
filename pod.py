from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as CO
from selenium.webdriver.firefox.options import Options as FO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pickle
import time
import os
import sys

username = os.getenv('PPUSER') if os.getenv('PPUSER') else sys.exit('Missing user variable')
password = os.getenv('PPPASS') if os.getenv('PPPASS') else sys.exit('Missing password variable')

chrome_options = CO()
firefox_options = FO()

# Chrome
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--user-data-dir=selenium')
# options.add_argument('--headless')
# driver = webdriver.Chrome(options=chrome_options)

# Firefox
firefox_options.set_preference("browser.privatebrowsing.autostart", 'true')
driver = webdriver.Firefox(firefox_options=firefox_options)
# driver.get("https://www.peapod.com")
driver.get('https://www.peapod.com/shop/auth/login?gateway=1&redirectTo=%2F')
#TODO add option where if page doesn't load it refreshes automatically
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button--third")))
except TimeoutException:
    driver.refresh()

use_sign = driver.find_element_by_name("loginName")
use_sign.clear()
use_sign.send_keys(username)
pass_sign = driver.find_element_by_name("password")
pass_sign.clear()
pass_sign.send_keys(password)
start_shopping = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div/div/div/div[2]/form/div[4]/button[2]')
start_shopping.click()
WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[10]/div/div[2]/div/form/a/button")))
warning_pop = driver.find_element_by_css_selector('.optly-modal-close')
warning_pop.click()
reserve_time = driver.find_element_by_css_selector('a.subnav-shopping-mode_element:nth-child(5)')
reserve_time.click()
# guest = driver.find_element_by_name("zipEntry")
# guest.clear()
# guest.send_keys("10512")
# guest.send_keys(Keys.RETURN)
# # time.sleep(2)
# wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "serviceLocationId")))
# el = driver.find_element_by_name('serviceLocationId')
# for option in el.find_elements_by_tag_name('option'):
#     if option.text == 'Carmel, NY':
#         option.click() # select() in earlier versions of webdriver
#         break
# wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))
# start_shopping = driver.find_element_by_xpath('//*[@id="main-content"]/div/section[1]/div[2]/zipcode-entry/div/form/div[2]/div[2]/div[2]/button')
# start_shopping.click()
# print(driver.page_source)
# # wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "pdl-shopping-mode-tile_text_content pdl-shopping-mode-tile_text_content--standalone")))

# # reserve = driver.find_element_by_class_name("pdl-shopping-mode-tile_text_content pdl-shopping-mode-tile_text_content--standalone")
# # reserve.click()
# # driver.quit()