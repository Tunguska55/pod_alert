from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

options = Options()
# options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
# options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get("https://www.peapod.com")

guest = driver.find_element_by_name("zipEntry")
guest.clear()
guest.send_keys("10512")
guest.send_keys(Keys.RETURN)
# time.sleep(2)
wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "serviceLocationId")))
el = driver.find_element_by_name('serviceLocationId')
for option in el.find_elements_by_tag_name('option'):
    if option.text == 'Carmel, NY':
        option.click() # select() in earlier versions of webdriver
        break
wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))
start_shopping = driver.find_element_by_xpath('//*[@id="main-content"]/div/section[1]/div[2]/zipcode-entry/div/form/div[2]/div[2]/div[2]/button')
start_shopping.click()
time.sleep(20)
# wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "pdl-shopping-mode-tile_text_content pdl-shopping-mode-tile_text_content--standalone")))
reserve = driver.find_element_by_class_name("pdl-shopping-mode-tile_text_content pdl-shopping-mode-tile_text_content--standalone")
reserve.click()
driver.quit()