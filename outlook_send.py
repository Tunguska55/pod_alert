import smtplib
import os
import sys

username = os.getenv('OUTLOOKUSER') if os.getenv('OUTLOOKUSER') else sys.exit('Missing outlook user variable')
password = os.getenv('OUTLOOKPASS') if os.getenv('OUTLOOKPASS') else sys.exit('Missing outlook password variable')

mailServer = smtplib.SMTP('smtp-mail.outlook.com', 587)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(username, password)