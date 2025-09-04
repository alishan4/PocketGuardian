from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
initialize_app(cred)
db = firestore.client()

# Add sample user
db.collection('users').document('user123').set({
    'phone': '+923001234567',
    'email': 'alihayat0049@gmail.com',
    'name': 'Ali Hayat',
    'fcm_token': 'test-token'
})

# Add sample transaction
db.collection('transactions').add({
    'user_id': 'user123',
    'type': 'income',
    'amount': 500.0,
    'description': 'Rs.500 credited from Easypaisa',
    'timestamp': firestore.SERVER_TIMESTAMP
})

# Add sample reminder
db.collection('reminders').add({
    'user_id': 'user123',
    'message': 'Pay utility bill',
    'due_date': '2025-09-10',
    'sent': False
})

print("Firestore schema test successful")