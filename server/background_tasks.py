import requests
import firebase_admin
from firebase_admin import messaging, credentials
import os
import json


def send_notification(tokens,detail,type,title,body):
    print(detail)
    cwd= os.getcwd()
    print(cwd)
    cred = credentials.Certificate(f"{cwd}\server\music-5e4d7-firebase-adminsdk-owp1r-6e510201d4.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    message = messaging.MulticastMessage(
        notification= messaging.Notification(
            title=title, 
            body=body
            ),
        tokens= tokens,
         data= {
             "click_action": "FLUTTER_NOTIFICATION_CLICK",
              "sound": "default",
              "type":type,
              "status": "done",
              "body": json.dumps(detail),
            }
         )
    response=messaging.send_multicast(message)
    print(response.success_count)
    
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

