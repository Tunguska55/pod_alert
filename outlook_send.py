from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import ssl
import sys

username = os.getenv('OUTLOOKUSER') if os.getenv('OUTLOOKUSER') else sys.exit('Missing outlook user variable')
password = os.getenv('OUTLOOKPASS') if os.getenv('OUTLOOKPASS') else sys.exit('Missing outlook password variable')
sender_email = input("Sender Email")
receiver_email = input("Receiver Email")

msg = MIMEMultipart("alternative")
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Delivery Slot Available"

text = "INSERT DATE AND TIME HERE"
html = """\
<html>
  <body>
    <p> <strong> {} </strong> </p>
  </body>
</html>
""".format("INSERT DATE AND TIME HERE")

part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

msg.attach(part1)
msg.attach(part2)

mailServer = smtplib.SMTP('smtp-mail.outlook.com', 587)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(username, password)
mailServer.sendmail(sender_email, receiver_email, msg.as_string())
mailServer.quit()