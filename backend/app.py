from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv
import logging

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Firebase
try:
    cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
    initialize_app(cred)
    db = firestore.client()
    logging.info("Firestore initialized successfully")
except Exception as e:
    logging.error(f"Firestore initialization failed: {str(e)}")
    raise

# Register user endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    if not phone:
        logging.warning("Missing phone in register request")
        return jsonify({'error': 'Phone required'}), 400
    user_ref = db.collection('users').where('phone', '==', phone).get()
    if user_ref:
        logging.warning(f"User with phone {phone} already exists")
        return jsonify({'error': 'User already exists'}), 409
    try:
        db.collection('users').add({
            'phone': phone,
            'email': data.get('email', ''),
            'name': data.get('name', ''),
            'fcm_token': data.get('fcm_token', 'test-token')
        })
        logging.info(f"User registered with phone {phone}")
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Failed to register user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Add transaction endpoint
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    logging.debug(f"Received transaction data: {data}")
    user_id = data.get('user_id')
    amount = data.get('amount')
    type_ = data.get('type')

    if not user_id:
        logging.warning("Missing user_id in transaction request")
        return jsonify({'error': 'User ID required'}), 400
    if not isinstance(amount, (int, float)) or amount < 0:
        logging.warning(f"Invalid amount: {amount}")
        return jsonify({'error': 'Valid amount required'}), 400
    if type_ not in ['income', 'expense']:
        logging.warning(f"Invalid type: {type_}")
        return jsonify({'error': 'Type must be income or expense'}), 400
    if not data.get('description') or not isinstance(data.get('description'), str):
        logging.warning("Invalid or missing description")
        return jsonify({'error': 'Valid description required'}), 400

    try:
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            logging.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error checking user existence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    try:
        db.collection('transactions').add({
            'user_id': user_id,
            'type': type_,
            'amount': amount,
            'description': data.get('description', ''),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"Transaction stored for user_id: {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Failed to store transaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Add reminder endpoint (new)
@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    data = request.json
    logging.debug(f"Received reminder data: {data}")
    user_id = data.get('user_id')
    message = data.get('message')
    due_date = data.get('due_date')

    # Validate inputs
    if not user_id:
        logging.warning("Missing user_id in reminder request")
        return jsonify({'error': 'User ID required'}), 400
    if not message or not isinstance(message, str):
        logging.warning("Invalid or missing message")
        return jsonify({'error': 'Valid message required'}), 400
    if not due_date or not isinstance(due_date, str):
        logging.warning("Invalid or missing due_date")
        return jsonify({'error': 'Valid due_date required'}), 400

    # Check if user exists
    try:
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            logging.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error checking user existence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Store reminder
    try:
        db.collection('reminders').add({
            'user_id': user_id,
            'message': message,
            'due_date': due_date,
            'sent': False,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"Reminder stored for user_id: {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Failed to store reminder: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5000)