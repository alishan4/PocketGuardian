from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv
import logging
import re
from datetime import timedelta, datetime
import hashlib
import sys

# Set up sys.path for agents
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Firebase
try:
    firebase_key = os.getenv('FIREBASE_KEY')
    if not os.path.exists(firebase_key):
        raise FileNotFoundError(f"Firebase key file not found at {firebase_key}")
    cred = credentials.Certificate(firebase_key)
    initialize_app(cred)
    db = firestore.client()
    logging.info("Firestore initialized successfully in app.py")
except Exception as e:
    logging.error(f"Firestore initialization failed in app.py: {str(e)}")
    raise

# Import agents after Firebase initialization
from agents.sms_parser import parse_sms
from agents.ml_alert import detect_overspending
from agents.reminder_agent import send_reminder

# Register user endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    user_id = data.get('user_id')
    if not phone or not user_id:
        logging.warning("Missing phone or user_id in register request")
        return jsonify({'error': 'Phone and user_id required'}), 400
    user_ref = db.collection('users').document(user_id)
    if user_ref.get().exists:
        logging.warning(f"User with user_id {user_id} already exists")
        return jsonify({'error': 'User already exists'}), 400
    try:
        user_ref.set({
            'phone': phone,
            'email': data.get('email', ''),
            'name': data.get('name', ''),
            'fcm_token': data.get('fcm_token', 'test-token')
        })
        logging.info(f"User registered with user_id {user_id}")
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
    description = data.get('description')

    if not user_id:
        logging.warning("Missing user_id in transaction request")
        return jsonify({'error': 'User ID required'}), 400
    if not isinstance(amount, (int, float)) or amount < 0:
        logging.warning(f"Invalid amount: {amount}")
        return jsonify({'error': 'Valid amount required'}), 400
    if type_ not in ['income', 'expense']:
        logging.warning(f"Invalid type: {type_}")
        return jsonify({'error': 'Type must be income or expense'}), 400
    if not description or not isinstance(description, str):
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

    # Generate transaction hash for deduplication
    transaction_hash = hashlib.sha256(f"{user_id}_{type_}_{amount}_{description}".encode()).hexdigest()
    try:
        recent_time = datetime.now() - timedelta(hours=1)  # Wider window
        duplicates = db.collection('transactions')\
            .where('user_id', '==', user_id)\
            .where('transaction_hash', '==', transaction_hash)\
            .where('timestamp', '>=', recent_time)\
            .get()
        if duplicates:
            logging.warning(f"Duplicate transaction detected for user_id: {user_id}")
            return jsonify({'error': 'Duplicate transaction'}), 409
    except Exception as e:
        logging.error(f"Error checking duplicates: {str(e)}")

    try:
        batch = db.batch()
        trans_ref = db.collection('transactions').document()
        batch.set(trans_ref, {
            'user_id': user_id,
            'type': type_,
            'amount': amount,
            'description': description,
            'transaction_hash': transaction_hash,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        log_ref = db.collection('agent_logs').document()
        batch.set(log_ref, {
            'agent_name': 'Transaction Handler',
            'action': 'Stored transaction',
            'data': {'user_id': user_id, 'transaction_hash': transaction_hash},
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        batch.commit()
        logging.info(f"Transaction stored for user_id: {user_id}")
        return jsonify({'success': True, 'transaction_hash': transaction_hash})
    except Exception as e:
        logging.error(f"Failed to store transaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Add reminder endpoint
@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    data = request.json
    logging.debug(f"Received reminder data: {data}")
    user_id = data.get('user_id')
    message = data.get('message')
    due_date = data.get('due_date')

    if not user_id:
        logging.warning("Missing user_id in reminder request")
        return jsonify({'error': 'User ID required'}), 400
    if not message or not isinstance(message, str):
        logging.warning("Invalid or missing message")
        return jsonify({'error': 'Valid message required'}), 400
    if not due_date or not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
        logging.warning(f"Invalid due_date format: {due_date}")
        return jsonify({'error': 'Valid due_date required (YYYY-MM-DD)'}), 400

    try:
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            logging.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error checking user existence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Use deterministic document ID: user_id_due_date
    reminder_id = f"{user_id}_{due_date.replace('-', '')}"
    try:
        batch = db.batch()
        reminder_ref = db.collection('reminders').document(reminder_id)
        reminder_data = {
            'user_id': user_id,
            'message': message,
            'due_date': due_date,
            'sent': False,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        if reminder_ref.get().exists:
            batch.update(reminder_ref, {
                'message': message,
                'sent': False,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Updated reminder {reminder_id} for user_id: {user_id}")
        else:
            batch.set(reminder_ref, reminder_data)
            logging.info(f"Created new reminder {reminder_id} for user_id: {user_id}")
        log_ref = db.collection('agent_logs').document()
        batch.set(log_ref, {
            'agent_name': 'Reminder Handler',
            'action': 'Processed reminder',
            'data': {'reminder_id': reminder_id, 'user_id': user_id},
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        batch.commit()
        return jsonify({'success': True, 'reminder_id': reminder_id})
    except Exception as e:
        logging.error(f"Failed to store/update reminder: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Orchestration endpoint for multi-agent system
@app.route('/api/agent_orchestrate', methods=['POST'])
def orchestrate_agents():
    data = request.json
    sms_text = data.get('sms_text')
    user_id = data.get('user_id')
    if not sms_text or not user_id:
        logging.warning("Missing sms_text or user_id in orchestrate request")
        return jsonify({'error': 'SMS text and user_id required'}), 400

    # Verify user exists
    try:
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            logging.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        if 'fcm_token' in data:
            user_ref.reference.update({'fcm_token': data['fcm_token']})
            logging.info(f"Updated fcm_token for user_id: {user_id}")
    except Exception as e:
        logging.error(f"Error checking/updating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Agent 1: SMS Parser (NLP with spaCy)
    try:
        parsed = parse_sms(sms_text)
        # Deduplication
        transaction_hash = hashlib.sha256(f"{user_id}_{parsed['type']}_{parsed['amount']}_{parsed['description']}".encode()).hexdigest()
        recent_time = datetime.now() - timedelta(hours=1)
        duplicates = db.collection('transactions')\
            .where('user_id', '==', user_id)\
            .where('transaction_hash', '==', transaction_hash)\
            .where('timestamp', '>=', recent_time)\
            .get()
        if duplicates:
            logging.warning(f"Duplicate transaction detected for user_id: {user_id}")
            return jsonify({'error': 'Duplicate transaction'}), 409
        # Store transaction
        db.collection('transactions').add({
            'user_id': user_id,
            'type': parsed['type'],
            'amount': parsed['amount'],
            'description': parsed['description'],
            'transaction_hash': transaction_hash,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        db.collection('agent_logs').add({
            'agent_name': 'SMS Parser',
            'action': 'Parsed SMS with spaCy',
            'data': parsed,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"SMS Parser completed for user_id: {user_id}")
    except Exception as e:
        logging.error(f"SMS Parser failed: {str(e)}")
        return jsonify({'error': 'Parser agent failed'}), 500

    # Agent 2: ML Alert (threshold-based)
    try:
        transactions = db.collection('transactions').where('user_id', '==', user_id).get()
        total_expenses = sum(doc.to_dict().get('amount', 0) for doc in transactions if doc.to_dict().get('type') == 'expense')
        if total_expenses > 1000:
            alert = {'overspending': True, 'total': total_expenses}
            db.collection('agent_logs').add({
                'agent_name': 'ML Alert',
                'action': 'Generated alert',
                'data': alert,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        else:
            alert = {'overspending': False}
        logging.info(f"ML Alert completed for user_id: {user_id}, overspending: {alert['overspending']}")
    except Exception as e:
        logging.error(f"ML Alert failed: {str(e)}")
        alert = {'overspending': False}

    # Agent 3: Reminder Orchestrator
    try:
        message = f"Overspending alert: {alert['total'] if alert['overspending'] else 'All good'}"
        due_date = '2025-09-15'
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
            logging.warning(f"Invalid due_date format in orchestration: {due_date}")
            return jsonify({'error': 'Valid due_date required (YYYY-MM-DD)'}), 400
        reminder_id = f"{user_id}_{due_date.replace('-', '')}"
        batch = db.batch()
        reminder_ref = db.collection('reminders').document(reminder_id)
        reminder_data = {
            'user_id': user_id,
            'message': message,
            'due_date': due_date,
            'sent': False,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        if reminder_ref.get().exists:
            batch.update(reminder_ref, {
                'message': message,
                'sent': False,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Updated reminder {reminder_id} for user_id: {user_id}")
        else:
            batch.set(reminder_ref, reminder_data)
            logging.info(f"Created new reminder {reminder_id} for user_id: {user_id}")
        log_ref = db.collection('agent_logs').document()
        batch.set(log_ref, {
            'agent_name': 'Reminder Orchestrator',
            'action': 'Queued reminder',
            'data': {'reminder_id': reminder_id, 'sent': False},
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        batch.commit()
        logging.info(f"Reminder Orchestrator completed for user_id: {user_id}")
    except Exception as e:
        logging.error(f"Reminder Orchestrator failed: {str(e)}")
        return jsonify({'error': 'Reminder Orchestrator failed'}), 500

    # Agent 4: Reminder Sender (FCM)
    try:
        reminder_result = send_reminder(user_id, reminder_id)
        logging.info(f"Reminder Agent result: {reminder_result}")
    except Exception as e:
        logging.error(f"Reminder Agent failed: {str(e)}")
        reminder_result = {'success': False, 'error': str(e)}

    return jsonify({
        'success': True,
        'parsed': parsed,
        'alert': alert,
        'reminder_id': reminder_id,
        'reminder_result': reminder_result
    })
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
