from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
initialize_app(cred)
db = firestore.client()

# Test write
db.collection('test').document('sample').set({'message': 'Firestore connected!'})
print("Firestore test successful")