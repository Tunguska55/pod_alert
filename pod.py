from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as CO
from selenium.webdriver.firefox.options import Options as FO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pickle
import os
import sys
import random

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

# if os.path.exists("cookies.pkl"):
#     cookies = pickle.load(open("cookies.pkl", "rb"))
#     driver.delete_all_cookies()
#     for cookie in cookies:
#         driver.add_cookie(cookie)

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
        break
    except TimeoutException:
        driver.refresh()
        retries+=1

# if not os.path.exists("cookies.pkl"):
#     pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".optly-modal-close")))
warning_pop = driver.find_element_by_css_selector('.optly-modal-close')
warning_pop.click()
reserve_time = driver.find_element_by_css_selector('a.subnav-shopping-mode_element:nth-child(5)')
reserve_time.click()

# Main code, where I check for availability

# Making sure the window pops up
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'aside')))

reserve_time_source = driver.page_source

# Lets grab all of the potential time slot tags
# LEAVE FOR TESTING
# driver.implicitly_wait(3)
# day_slot_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/ul')
# day_slots = day_slot_parent.find_elements_by_tag_name("li")
# print(day_slots)
# print(len(day_slots))
# print("Do the sessions change?")
# driver.implicitly_wait(2)
# day_slots[5].click()
# print(day_slots)
# print(len(day_slots))
# print("ON MORE TIME!")
# driver.implicitly_wait(2)
# day_slot_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/ul')
# day_slots = day_slot_parent.find_elements_by_tag_name("li")
# day_slots[8].click()
# print(day_slots)
# print(len(day_slots))
# driver.quit()
# sys.exit("Done")

slot_search = True
# For testing purposes, to make sure while loop isn't infinite
while_break = 0
completed_options = []
while slot_search or while_break < 20:
    while_break+=1
    # Doing a wait here, just to be safe
    driver.implicitly_wait(3)
    print("*****")
    day_slot_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/ul')
    day_slots = day_slot_parent.find_elements_by_tag_name("li")
    if completed_options:
        day_slots = [ns for ns in day_slots if ns not in completed_options]
        print(day_slots)
    if len(day_slots) == 0:
        print("Went through all options, done")
        break
    # print(completed_options)
    random_index = random.randint(0,len(day_slots))
    al = day_slots[random_index].get_attribute("aria-label")
    if 'unavailable' in al:
        print(al)
        print("Continuing...")
        completed_options.append(day_slots[random_index])
        continue
    else:
        print("Choosing: {}".format(al))
        # Date being chosen
        day_slots[random_index].click()
        # Allows time slots to show
        driver.implicitly_wait(3)
        actual_time_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/ul')
        actual_time = actual_time_parent.find_elements_by_tag_name("li")
        for time in actual_time:
            sl = time.get_attribute("aria-label")
            avail = time.get_attribute("class")
            if 'sold-out' in avail:
                print("{} is sold out".format(sl))
            else:
                print("{} is AVAILABLE".format(sl))
                # ALERTING CODE HERE
        completed_options.append(day_slots[random_index])
driver.quit()    
    

# for slot in day_slots:
#     al = slot.get_attribute("aria-label")
#     print("*****")
#     if 'unavailable' in al:
#         print(al)
#         print("Continuing...")
#         continue
#     else:
#         print("Choosing: {}".format(al))
#         # Date being chosen
#         slot.click()
#         # Allows time slots to show
#         driver.implicitly_wait(3)
#         # Now let's look for time slots
#         actual_time_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/ul')
#         actual_time = actual_time_parent.find_elements_by_tag_name("li")
#         for time in actual_time:
#             sl = time.get_attribute("aria-label")
#             avail = time.get_attribute("class")
#             if 'sold-out' in avail:
#                 print("{} is sold out".format(sl))
#             else:
#                 print("{} is AVAILABLE".format(sl))
#                 # ALERTING CODE HERE
        


# BS4 Implementation


# Keep around as reference

# guest = driver.find_element_by_name("zipEntry")
# guest.clear()
# guest.send_keys("10512")
# guest.send_keys(Keys.RETURN)
# wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "serviceLocationId")))

# Good example of how to loop through options

# el = driver.find_element_by_name('serviceLocationId')
# for option in el.find_elements_by_tag_name('option'):
#     if option.text == 'Carmel, NY':
#         option.click() # select() in earlier versions of webdriver
#         break

# driver.quit()