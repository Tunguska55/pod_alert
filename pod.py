from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as CO
from selenium.webdriver.firefox.options import Options as FO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import pickle
import os
import sys
import random

# Rate limit exists, not sure what the amount is and how long it lasts
# Currently at 35 minutes and still can't login

# Check every 15 minutes would be ideal to prevent rate limiting I would imagine

def send_alert(ts):
    username = os.getenv('OUTLOOKUSER') if os.getenv('OUTLOOKUSER') else sys.exit('Missing outlook user variable')
    password = os.getenv('OUTLOOKPASS') if os.getenv('OUTLOOKPASS') else sys.exit('Missing outlook password variable')
    receivers = os.getenv('RECEIVERS').split(',') if os.getenv('RECEIVERS') else sys.exit('Missing receivers variable')
    sender_email = username
    receiver_email = receivers

    msg = MIMEMultipart("alternative")
    msg['From'] = username
    msg['To'] = receiver_email
    msg['Subject'] = "Delivery Slot Available"

    text = str(ts)
    html = """\
    <html>
    <body>
        <p> <strong> {} </strong> </p>
    </body>
    </html>
    """.format(str(ts))

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    msg.attach(part1)
    msg.attach(part2)

    mailServer = smtplib.SMTP('smtp-mail.outlook.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    try:
        mailServer.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent")
    except:
        print("Email failed to send")
    finally:
        mailServer.quit()

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
firefox_options.headless = True
driver = webdriver.Firefox(firefox_options=firefox_options)

# This might need to get changed since it's a redirect
# Option 1

# During peak hours the load times increase significantly, so I will raise the
# initial wait time to compensate
print("Webdriver loaded with options, attempting URL")
driver.get('https://www.peapod.com/shop/auth/login?gateway=1&redirectTo=%2F')

try:
    WebDriverWait(driver, 45).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button--third")))
    print("Initial page open successfully")
except TimeoutException:
    print("Initial page load took too long")
    print("If it wont load here, a refresh won't help, quitting application instead")
    driver.quit()
    sys.exit("Failed to open page properly")

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

retries = 0
max_retries = 3
while retries < max_retries:
    print("Signing in, attempt {} out of {}".format(retries+1, max_retries))
    use_sign = driver.find_element_by_name("loginName")
    use_sign.clear()
    use_sign.send_keys(username)
    pass_sign = driver.find_element_by_name("password")
    pass_sign.clear()
    pass_sign.send_keys(password)
    start_shopping = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div/div/div/div[2]/form/div[4]/button[2]')
    start_shopping.click()
    try:
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.subnav-shopping-mode_element:nth-child(5)")))
        print("Sign in successful")
        break
    except TimeoutException:
        print("XXXX")
        print("Sign in failed, timed out")
        print("Refreshing sign in page")
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

# Not sure if this is still necessary
reserve_time_source = driver.page_source

initial_pass = False
time_slot_found = False
open_time_slot = {}
while True:
    # Doing a wait here, just to be safe
    driver.implicitly_wait(5)
    print("*****")
    # day_slot_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/ul')
    day_slot_parent = driver.find_element_by_css_selector('.slot-headers-collection')
    day_slots = day_slot_parent.find_elements_by_tag_name("li")

    # Work inversely through a list, subtracting rather than adding
    if not initial_pass:
        uncompleted_options = list(range(0,len(day_slots)))
        initial_pass = True
    if not uncompleted_options:
        print("All of the days and times have been checked")
        break
    try:
        random_index = uncompleted_options.pop(uncompleted_options.index(random.choice(uncompleted_options)))
    except NameError:
        print("Unable to find uncompleted_options, breaking")
        break
    except IndexError:
        print("Index is out of range, check random_index")
        break
    al = day_slots[random_index].get_attribute("aria-label")
    if 'unavailable' in al:
        print(al)
        print("Continuing...")
        continue
    else:
        print("Choosing: {}".format(al))
        # Date being chosen
        day_slots[random_index].click()
        # Allows time slots to show, 8 works great here
        driver.implicitly_wait(8)
        # actual_time_parent = driver.find_element_by_xpath('/html/body/aside/div/div/div/div/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/ul')
        actual_time_parent = driver.find_element_by_css_selector('.slot_times')
        actual_time = actual_time_parent.find_elements_by_tag_name("li")
        # TODO add code to prevent stalereferenceexception
        driver.implicitly_wait(4)
        for time in actual_time:
            sl = time.get_attribute("aria-label")
            avail = time.get_attribute("class")
            if 'sold-out' in avail:
                print("{} is sold out".format(sl))
                continue
            else:
                print("{} is AVAILABLE".format(sl))
                print("Sending email now")
                time_slot_found = True
                time.click()
                send_alert("{} {}".format(al, sl))
                # TODO add reserve time interactivity, not just an alert
    # DEBUG
    # print(uncompleted_options)
print("-------------")
if time_slot_found:
    print("Time slot found!")
else:
    print("No available time slots.")

# Clean up
driver.quit()     

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