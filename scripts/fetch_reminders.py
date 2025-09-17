import pandas as pd
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import os

load_dotenv()
cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
initialize_app(cred)
db = firestore.client()

user_id = 'user123'
reminders = db.collection('reminders').where('user_id', '==', user_id).stream()
data = [{'id': t.id, **t.to_dict()} for t in reminders]
df = pd.DataFrame(data)
df.to_csv('reminders.csv', index=False)
print("Saved to reminders.csv")


