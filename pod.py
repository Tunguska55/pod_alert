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

# Rate limit exists, not sure what the amount is and how long it lasts
# Currently at 35 minutes and still can't login

# Check every 15 minutes would be ideal to prevent rate limiting I would imagine

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
driver.get("https://www.peapod.com")

# This might need to get changed since it's a redirect
# Option 1
driver.get('https://www.peapod.com/shop/auth/login?gateway=1&redirectTo=%2F')

try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button--third")))
except TimeoutException:
    driver.refresh()

# Option 2
# driver.get('https://www.peapod.com/shop/auth/login')

# try:
#     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button:nth-child(1)")))
# except TimeoutException:
#     driver.refresh()
# account_exists = driver.find_element_by_css_selector('button.button:nth-child(1)')
# account_exists.click()

if os.path.exists("cookies.pkl"):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)

sign_in = False
retries = 0
while not sign_in or retries < 3:
    use_sign = driver.find_element_by_name("loginName")
    use_sign.clear()
    use_sign.send_keys(username)
    pass_sign = driver.find_element_by_name("password")
    pass_sign.clear()
    pass_sign.send_keys(password)
    start_shopping = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div/div/div/div[2]/form/div[4]/button[2]')
    start_shopping.click()
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[10]/div/div[2]/div/form/a/button")))
        sign_in = True
    except TimeoutException:
        driver.refresh()
        retries+=1

if not os.path.exists("cookies.pkl"):
    pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

warning_pop = driver.find_element_by_css_selector('.optly-modal-close')
warning_pop.click()
reserve_time = driver.find_element_by_css_selector('a.subnav-shopping-mode_element:nth-child(5)')
reserve_time.click()

# Main code, where I check for availability

# Making sure the window pops up
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'slot-selection-header-title')))



# Keep around as reference

# guest = driver.find_element_by_name("zipEntry")
# guest.clear()
# guest.send_keys("10512")
# guest.send_keys(Keys.RETURN)
# # time.sleep(2)
# wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "serviceLocationId")))

# Good example of how to loop through options

# el = driver.find_element_by_name('serviceLocationId')
# for option in el.find_elements_by_tag_name('option'):
#     if option.text == 'Carmel, NY':
#         option.click() # select() in earlier versions of webdriver
#         break

# driver.quit()