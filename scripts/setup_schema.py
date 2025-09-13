from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv

load_dotenv()
cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
initialize_app(cred)
db = firestore.client()

# Add sample user (if not exists)
user_ref = db.collection('users').document('user123').get()
if not user_ref.exists:
    db.collection('users').document('user123').set({
        'phone': '+923001234567',
        'email': 'alihayat0049@gmail.com',
        'name': 'Ali Shan',
        'fcm_token': 'test-token'
    })
    print("Sample user added")

# Add sample transaction
db.collection('transactions').add({
    'user_id': 'user123',
    'type': 'expense',
    'amount': 200.0,
    'description': 'Bought groceries',
    'timestamp': firestore.SERVER_TIMESTAMP
})
print("Sample transaction added")

# Add sample reminder
db.collection('reminders').add({
    'user_id': 'user123',
    'message': 'Pay utility bill',
    'due_date': '2025-09-15',
    'sent': False,
    'timestamp': firestore.SERVER_TIMESTAMP
})
print("Sample reminder added")

# Add agent_logs collection for multi-agent tracking
db.collection('agent_logs').add({
    'agent_name': 'SMS Parser',
    'action': 'Parsed SMS',
    'timestamp': firestore.SERVER_TIMESTAMP
})
print("Sample agent log added")

print("Schema setup complete!")