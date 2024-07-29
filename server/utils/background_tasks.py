import requests
import firebase_admin
from firebase_admin import messaging, credentials
import os
import json
from email.message import EmailMessage
import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path


def send_notification(tokens, detail, type, title, body):
    cwd = os.getcwd()
    cred = credentials.Certificate(
        f"{cwd}\server\musecstacy-92e6a-firebase-adminsdk-6zn68-7d46fedb28.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=tokens,
        data={
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "sound": "default",
            "type": type,
            "status": "done",
            "body": json.dumps(detail),
        }
    )
    response = messaging.send_multicast(message)

    return response

# def send_notification():
#     detail = {
#     "to": "fipAWcdJQOKn6b7PK_N06L:APA91bGa06euoa4LbP6PlscDEfgFZ73FhckA76UFGEjAS1s_myMZ7YQAEKllBvJz87fIg-7QiFLdSbDNurv_qsU25pIElJ8afVkjx5C61AzgL-siF7DKmOlHI6579iDLXgXt7_JYOQS2",
#     "notification": {
#       "title": "Check this Mobile (title)",
#       "body": "Rich Notification testing (body)",
#       "mutable_content": True,
#       "sound": "Tri-tone"
#       },

#    "data": { "click_action": "FLUTTER_NOTIFICATION_CLICK", "sound": "default",  "type":"grow","status": "done", "body": "hello world" }
# }
#     headers = {
#         #'Content-Type':'application/json',
#         'Authorization': 'bearer AAAAqpqCn6Q:APA91bH6fSBl7yxosDF8vPvl5Cv1al8Dq8O6gVtza6f0Hr1PzhHb0ucEAs7AOLh0RZug2VBqOXZPP45d8HchVPn3WxZY-YascNc6Hn0cLf6DkLkh_9V5Y3hNNEwf2dTFZD04wtQuDa67'
#     }
#     url = "https://fcm.googleapis.com/fcm/send"
#     response = requests.request("POST", url, headers=headers, data=detail)
#     print(response.json())


async def send_email(email: str, message: str):
    sender_email = os.environ.get("EMAIL_EMAIL")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    mail_smtp = os.environ.get("EMAIL_SMTP")
    mail_port = os.environ.get("EMAIL_PORT")
    message_to_send = EmailMessage()
    message_to_send['From'] = sender_email
    message_to_send['To'] = email
    message_to_send['Subject'] = "Confirmation Code for account creation"
    message_to_send.set_content((message))

    with smtplib.SMTP_SSL(mail_smtp, mail_port) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(message_to_send)

    with smtplib.SMTP_SSL(mail_smtp, mail_port) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(message_to_send)
