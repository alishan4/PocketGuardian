from firebase_admin import firestore, get_app
from google.oauth2 import service_account
import requests
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

# Use existing Firebase app
try:
    db = firestore.client()
    logging.info("Firestore client accessed in reminder_agent.py")
except Exception as e:
    logging.error(f"Firestore access failed in reminder_agent.py: {str(e)}")
    raise

# FCM HTTP v1 setup
def get_access_token():
    scopes = ["https://www.googleapis.com/auth/firebase.messaging"]
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('FIREBASE_KEY'), scopes=scopes
    )
    request = requests.Request()
    credentials.refresh(request)
    return credentials.token

def send_reminder(user_id, reminder_id):
    try:
        reminder_ref = db.collection('reminders').document(reminder_id)
        reminder = reminder_ref.get()
        if not reminder.exists:
            logging.warning(f"Reminder {reminder_id} not found")
            return {'success': False, 'error': 'Reminder not found'}
        reminder_data = reminder.to_dict()
        if reminder_data['sent']:
            logging.info(f"Reminder {reminder_id} already sent")
            return {'success': True, 'message': 'Already sent'}
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            logging.warning(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}
        fcm_token = user_ref.to_dict().get('fcm_token')
        if not fcm_token:
            logging.warning(f"No FCM token for user {user_id}")
            return {'success': False, 'error': 'No FCM token'}
        due_date = datetime.strptime(reminder_data['due_date'], '%Y-%m-%d')
        if due_date.date() > datetime.now().date():
            logging.info(f"Reminder {reminder_id} not due yet")
            return {'success': True, 'message': 'Not due'}
        # Send FCM notification
        access_token = get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8'
        }
        payload = {
            'message': {
                'token': fcm_token,
                'notification': {
                    'title': 'PocketGuardian Alert',
                    'body': reminder_data['message']
                }
            }
        }
        response = requests.post(
            'https://fcm.googleapis.com/v1/projects/pocketguardian-7563c/messages:send',
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            reminder_ref.update({'sent': True})
            db.collection('agent_logs').add({
                'agent_name': 'Reminder Agent',
                'action': 'Sent FCM notification',
                'data': {'reminder_id': reminder_id, 'user_id': user_id},
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Sent reminder {reminder_id} to user {user_id}")
            return {'success': True}
        else:
            logging.error(f"FCM failed for reminder {reminder_id}: {response.text}")
            return {'success': False, 'error': response.text}
    except Exception as e:
        logging.error(f"Reminder failed for {reminder_id}: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    print(send_reminder('user123', 'user123_20250914'))