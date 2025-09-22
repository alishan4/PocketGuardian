import os
import json
from firebase_admin import credentials, initialize_app, firestore
import logging
from flask import Flask, request, jsonify
from agents.sms_parser import parse_sms
from agents.fraud_detector import detect_fraud
from agents.ml_alert import detect_overspending
from agents.reminder_agent import send_reminder
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# --- MODIFIED FIREBASE INITIALIZATION ---
db = None
try:
    firebase_key = os.getenv('FIREBASE_KEY')
    if firebase_key:
        logging.info("Attempting to initialize Firebase from FIREBASE_KEY secret...")
        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)
        initialize_app(cred)
        db = firestore.client()
        logging.info("Firestore initialized successfully from secret in app.py")
    else:
        logging.warning("FIREBASE_KEY secret not found. App will run without Firestore functionality.")
except Exception as e:
    logging.error(f"Firestore initialization failed: {str(e)}")
    # We don't 'raise' the error anymore, allowing the app to run for health checks
    # raise

# --- NEW HEALTH CHECK ENDPOINT ---
@app.route('/', methods=['GET'])
def health_check():
    """A simple endpoint to verify that the server is running."""
    firestore_status = "Initialized" if db else "Not Initialized"
    return jsonify({
        "status": "ok",
        "message": "PocketGuardian backend is running.",
        "firestore_status": firestore_status
    }), 200


@app.route('/api/register', methods=['POST'])
def register_user():
    if not db:
        return jsonify({'success': False, 'error': 'Database not configured'}), 503
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'No user_id provided'}), 400
        db.collection('users').document(user_id).set({
            'phone': data.get('phone', ''),
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'fcm_token': data.get('fcm_token', '')
        })
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"User registration failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    if not db:
        return jsonify({'success': False, 'error': 'Database not configured'}), 503
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')
        type_ = data.get('type')
        description = data.get('description')
        if not all([user_id, amount, type_, description]):
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        transaction_id = hashlib.sha256(f"{user_id}{amount}{description}{datetime.now()}".encode()).hexdigest()
        db.collection('transactions').document(transaction_id).set({
            'user_id': user_id,
            'amount': amount,
            'type': type_,
            'description': description,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({'success': True, 'transaction_hash': transaction_id})
    except Exception as e:
        logging.error(f"Transaction addition failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agent_orchestrate', methods=['POST'])
def orchestrate_agents():
    if not db:
        return jsonify({'success': False, 'error': 'Database not configured'}), 503
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        sms_text = data.get('sms_text')
        if not user_id or not sms_text:
            return jsonify({'success': False, 'error': 'Missing user_id or sms_text'}), 400
        # Step 1: Parse SMS
        parsed_data = parse_sms(sms_text)
        logging.info(f"Parsed SMS: {parsed_data}")
        # Step 2: Add to transactions
        transaction_id = hashlib.sha256(f"{user_id}{parsed_data['amount']}{sms_text}{datetime.now()}".encode()).hexdigest()
        db.collection('transactions').document(transaction_id).set({
            'user_id': user_id,
            'amount': parsed_data['amount'],
            'type': parsed_data['type'],
            'description': parsed_data['description'],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        db.collection('agent_logs').add({
            'agent_name': 'SMS Parser',
            'action': 'Parsed SMS',
            'data': parsed_data,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        # Step 3: Fraud Detection
        fraud_result = detect_fraud(sms_text)
        db.collection('agent_logs').add({
            'agent_name': 'Fraud Detector',
            'action': 'Checked fraud',
            'data': fraud_result,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        # Step 4: Overspending Alert
        alert_result = detect_overspending(user_id)
        db.collection('agent_logs').add({
            'agent_name': 'ML Alert',
            'action': 'Checked overspending',
            'data': alert_result,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        # Step 5: Send Reminder if fraud or overspending
        reminder_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        message = f"Alert: {'Potential fraud detected' if fraud_result['fraud'] else 'Overspending detected' if alert_result['overspending'] else 'Transaction recorded'}"
        db.collection('reminders').document(reminder_id).set({
            'user_id': user_id,
            'message': message,
            'due_date': datetime.now().strftime('%Y-%m-%d'),
            'sent': False
        })
        reminder_result = send_reminder(user_id, reminder_id)
        return jsonify({
            'success': True,
            'parsed': parsed_data,
            'fraud': fraud_result,
            'alert': alert_result,
            'reminder_id': reminder_id,
            'reminder_result': reminder_result
        })
    except Exception as e:
        logging.error(f"Orchestration failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)
