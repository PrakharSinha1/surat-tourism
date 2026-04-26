import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "work@gmail.com"   # 🔥 YOUR ADMIN EMAIL
PASSWORD = "YOUR_APP_PASSWORD"    # 🔐 PUT APP PASSWORD HERE

def send_email(to_email, itinerary):
    subject = "Your Surat Trip Itinerary ✈️"

    body = f"""
🌍 Your Travel Plan

📍 Places:
{", ".join(itinerary['places'])}

🎉 Events:
{", ".join(itinerary['events'])}

🍽️ Food:
{", ".join(itinerary['food'])}

📅 Date:
{itinerary['dates']}

Enjoy your trip 💙
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(SENDER_EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()


# 🔥 SEND ADMIN REQUEST EMAIL
def send_admin_request(user_email):
    subject = "Admin Access Request"

    body = f"{user_email} is requesting admin access."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL   # 🔥 goes to work@gmail.com

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(SENDER_EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()