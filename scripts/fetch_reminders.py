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


# Add reminder endpoint
@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    due_date = data.get('due_date')
    if not user_id or not message or not due_date:
        return jsonify({'error': 'Missing required fields'}), 400
    db.collection('reminders').add({
        'user_id': user_id,
        'message': message,
        'due_date': due_date,
        'sent': False
    })
    return jsonify({'success': True})