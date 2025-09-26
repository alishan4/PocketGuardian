# # from firebase_admin import firestore, get_app, initialize_app, credentials
# # from google.oauth2 import service_account
# # import requests
# # from dotenv import load_dotenv
# # import os
# # import logging
# # from datetime import datetime

# # logging.basicConfig(level=logging.DEBUG)

# # load_dotenv()

# # # Conditional Firebase initialization
# # try:
# #     get_app()
# # except ValueError:
# #     try:
# #         firebase_key = os.getenv('FIREBASE_KEY')
# #         if not os.path.exists(firebase_key):
# #             raise FileNotFoundError(f"Firebase key file not found at {firebase_key}")
# #         cred = credentials.Certificate(firebase_key)
# #         initialize_app(cred)
# #         logging.info("Firestore initialized in reminder_agent.py (standalone)")
# #     except Exception as e:
# #         logging.error(f"Firestore initialization failed in reminder_agent.py: {str(e)}")
# #         raise

# # # Use Firebase client
# # db = firestore.client()
# # logging.info("Firestore client accessed in reminder_agent.py")

# # # FCM HTTP v1 setup
# # def get_access_token():
# #     scopes = ["https://www.googleapis.com/auth/firebase.messaging"]
# #     credentials = service_account.Credentials.from_service_account_file(
# #         os.getenv('FIREBASE_KEY'), scopes=scopes
# #     )
# #     request = requests.Request()
# #     credentials.refresh(request)
# #     return credentials.token

# # def send_reminder(user_id, reminder_id):
# #     try:
# #         reminder_ref = db.collection('reminders').document(reminder_id)
# #         reminder = reminder_ref.get()
# #         if not reminder.exists:
# #             logging.warning(f"Reminder {reminder_id} not found")
# #             return {'success': False, 'error': 'Reminder not found'}
# #         reminder_data = reminder.to_dict()
# #         if reminder_data['sent']:
# #             logging.info(f"Reminder {reminder_id} already sent")
# #             return {'success': True, 'message': 'Already sent'}
# #         user_ref = db.collection('users').document(user_id).get()
# #         if not user_ref.exists:
# #             logging.warning(f"User {user_id} not found")
# #             return {'success': False, 'error': 'User not found'}
# #         fcm_token = user_ref.to_dict().get('fcm_token')
# #         if not fcm_token:
# #             logging.warning(f"No FCM token for user {user_id}")
# #             return {'success': False, 'error': 'No FCM token'}
# #         due_date = datetime.strptime(reminder_data['due_date'], '%Y-%m-%d')
# #         if due_date.date() > datetime.now().date():
# #             logging.info(f"Reminder {reminder_id} not due yet")
# #             return {'success': True, 'message': 'Not due'}
# #         # Send FCM notification
# #         access_token = get_access_token()
# #         headers = {
# #             'Authorization': f'Bearer {access_token}',
# #             'Content-Type': 'application/json; UTF-8'
# #         }
# #         payload = {
# #             'message': {
# #                 'token': fcm_token,
# #                 'notification': {
# #                     'title': 'PocketGuardian Alert',
# #                     'body': reminder_data['message']
# #                 }
# #             }
# #         }
# #         response = requests.post(
# #             'https://fcm.googleapis.com/v1/projects/pocketguardian-7563c/messages:send',
# #             headers=headers,
# #             json=payload
# #         )
# #         if response.status_code == 200:
# #             reminder_ref.update({'sent': True})
# #             db.collection('agent_logs').add({
# #                 'agent_name': 'Reminder Agent',
# #                 'action': 'Sent FCM notification',
# #                 'data': {'reminder_id': reminder_id, 'user_id': user_id},
# #                 'timestamp': firestore.SERVER_TIMESTAMP
# #             })
# #             logging.info(f"Sent reminder {reminder_id} to user {user_id}")
# #             return {'success': True}
# #         else:
# #             logging.error(f"FCM failed for reminder {reminder_id}: {response.text}")
# #             return {'success': False, 'error': response.text}
# #     except Exception as e:
# #         logging.error(f"Reminder failed for {reminder_id}: {str(e)}")
# #         return {'success': False, 'error': str(e)}

# # if __name__ == '__main__':
# #     print(send_reminder('user123', 'user123_20250914'))


# from firebase_admin import firestore
# import logging
# from datetime import datetime, timedelta

# logging.basicConfig(level=logging.DEBUG)

# # def send_reminder(user_id, reminder_id, db):

#     # Change the function signature to accept db parameter
# def send_reminder(user_id, reminder_id, db=None):
#     # ... existing code ...
#     try:
#         # Get reminder data
#         reminder_ref = db.collection('reminders').document(reminder_id)
#         reminder = reminder_ref.get()
        
#         if not reminder.exists:
#             return {'success': False, 'error': 'Reminder not found'}
        
#         reminder_data = reminder.to_dict()
        
#         # Check if already sent
#         if reminder_data.get('sent', False):
#             return {'success': True, 'message': 'Reminder already sent'}
        
#         # Get user data
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
        
#         if not user.exists:
#             return {'success': False, 'error': 'User not found'}
        
#         # Simulate sending reminder (in real app, this would send FCM notification)
#         reminder_ref.update({
#             'sent': True,
#             'sent_at': firestore.SERVER_TIMESTAMP
#         })
        
#         # Log the reminder action
#         db.collection('agent_logs').add({
#             'agent_name': 'Reminder Agent',
#             'action': 'Sent financial reminder',
#             'user_id': user_id,
#             'reminder_id': reminder_id,
#             'message': reminder_data.get('message', ''),
#             'timestamp': firestore.SERVER_TIMESTAMP
#         })
        
#         logging.info(f"Reminder sent: {reminder_id} for user {user_id}")
        
#         return {
#             'success': True,
#             'reminder_id': reminder_id,
#             'message': reminder_data.get('message', ''),
#             'sent_at': datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         logging.error(f"Reminder failed: {str(e)}")
#         return {'success': False, 'error': str(e)}

# if __name__ == '__main__':
#     print("Reminder Agent module loaded")


from firebase_admin import firestore
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

def send_reminder(user_id, reminder_id, db=None):
    try:
        reminder_ref = db.collection('reminders').document(reminder_id)
        reminder = reminder_ref.get()
        if not reminder.exists:
            return {'success': False, 'error': 'Reminder not found'}
        reminder_data = reminder.to_dict()
        if reminder_data.get('sent', False):
            return {'success': True, 'message': 'Reminder already sent'}
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists:
            return {'success': False, 'error': 'User not found'}
        reminder_ref.update({
            'sent': True,
            'sent_at': firestore.SERVER_TIMESTAMP
        })
        db.collection('agent_logs').add({
            'agent_name': 'Reminder Agent',
            'action': 'Sent financial reminder',
            'user_id': user_id,
            'reminder_id': reminder_id,
            'message': reminder_data.get('message', ''),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"Reminder sent: {reminder_id} for user {user_id}")
        return {
            'success': True,
            'reminder_id': reminder_id,
            'message': reminder_data.get('message', ''),
            'sent_at': datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Reminder failed: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    print("Reminder Agent module loaded")