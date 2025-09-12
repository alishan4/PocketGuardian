from flask import Flask, jsonify, request
    from firebase_admin import credentials, firestore, initialize_app
    import os
    from dotenv import load_dotenv
    import logging
    import re
    from datetime import datetime, timedelta

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
        user_id = data.get('user_id')
        if not phone or not user_id:
            logging.warning("Missing phone or user_id in register request")
            return jsonify({'error': 'Phone and user_id required'}), 400
        user_ref = db.collection('users').document(user_id)
        if user_ref.get().exists:
            logging.warning(f"User with user_id {user_id} already exists")
            return jsonify({'error': 'User already exists'}), 409
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

        # Check for duplicate transaction (within last minute)
        try:
            recent_time = datetime.now() - timedelta(minutes=1)
            duplicates = db.collection('transactions')\
                .where('user_id', '==', user_id)\
                .where('type', '==', type_)\
                .where('amount', '==', amount)\
                .where('description', '==', description)\
                .where('timestamp', '>=', recent_time)\
                .get()
            if duplicates:
                logging.warning(f"Duplicate transaction detected for user_id: {user_id}")
                return jsonify({'error': 'Duplicate transaction'}), 409
        except Exception as e:
            logging.error(f"Error checking duplicates: {str(e)}")

        try:
            db.collection('transactions').add({
                'user_id': user_id,
                'type': type_,
                'amount': amount,
                'description': description,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Transaction stored for user_id: {user_id}")
            return jsonify({'success': True})
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
        if not due_date or not isinstance(due_date, str):
            logging.warning("Invalid or missing due_date")
            return jsonify({'error': 'Valid due_date required'}), 400

        try:
            user_ref = db.collection('users').document(user_id).get()
            if not user_ref.exists:
                logging.warning(f"User not found: {user_id}")
                return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            logging.error(f"Error checking user existence: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

        # Check for existing reminder with same user_id, message, due_date
        try:
            existing_reminder = db.collection('reminders')\
                .where('user_id', '==', user_id)\
                .where('message', '==', message)\
                .where('due_date', '==', due_date)\
                .limit(1).get()
            if existing_reminder:
                reminder_ref = existing_reminder[0].reference
                reminder_ref.update({
                    'sent': False,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                logging.info(f"Updated existing reminder for user_id: {user_id}")
            else:
                db.collection('reminders').add({
                    'user_id': user_id,
                    'message': message,
                    'due_date': due_date,
                    'sent': False,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                logging.info(f"New reminder stored for user_id: {user_id}")
            return jsonify({'success': True})
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

        # Agent 1: SMS Parser (regex for Pakistan SMS)
        try:
            amount_match = re.search(r'Rs\.?[\s]*(\d+[\.,]?\d*)', sms_text)
            amount = float(amount_match.group(1).replace(',', '')) if amount_match else 500.0
            type_ = 'income' if 'credited' in sms_text.lower() else 'expense'
            parsed = {'type': type_, 'amount': amount, 'description': sms_text}
            # Check for duplicate transaction
            recent_time = datetime.now() - timedelta(minutes=1)
            duplicates = db.collection('transactions')\
                .where('user_id', '==', user_id)\
                .where('type', '==', type_)\
                .where('amount', '==', amount)\
                .where('description', '==', sms_text)\
                .where('timestamp', '>=', recent_time)\
                .get()
            if duplicates:
                logging.warning(f"Duplicate transaction detected for user_id: {user_id}")
                return jsonify({'error': 'Duplicate transaction'}), 409
            db.collection('transactions').add({
                'user_id': user_id,
                'type': type_,
                'amount': amount,
                'description': sms_text,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            db.collection('agent_logs').add({
                'agent_name': 'SMS Parser',
                'action': 'Parsed SMS',
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
            existing_reminder = db.collection('reminders')\
                .where('user_id', '==', user_id)\
                .where('message', '==', message)\
                .where('due_date', '==', '2025-09-15')\
                .limit(1).get()
            if existing_reminder:
                reminder_ref = existing_reminder[0].reference
                reminder_ref.update({
                    'sent': False,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                logging.info(f"Updated existing reminder for user_id: {user_id}")
            else:
                db.collection('reminders').add({
                    'user_id': user_id,
                    'message': message,
                    'due_date': '2025-09-15',
                    'sent': False,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                logging.info(f"New reminder stored for user_id: {user_id}")
            db.collection('agent_logs').add({
                'agent_name': 'Reminder Orchestrator',
                'action': 'Queued reminder',
                'data': {'sent': False},
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Reminder Orchestrator completed for user_id: {user_id}")
        except Exception as e:
            logging.error(f"Reminder Orchestrator failed: {str(e)}")

        return jsonify({'success': True, 'parsed': parsed, 'alert': alert})

    if __name__ == '__main__':
        app.run(port=5000)