
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

"""
backend/app.py
Clean, robust PocketGuardian Flask app with mobile-ready endpoints.
- Graceful fallbacks if heavy ML libs are missing (spaCy/transformers)
- Firestore optional (service-account.json OR FIREBASE_KEY env)
- CORS enabled
- Route debug endpoint
- Clear __main__ (single entrypoint)
"""

import os
import json
import logging
from datetime import datetime
import hashlib

from flask import Flask, request, jsonify
from flask_cors import CORS

# Try to import Firestore (optional)
db = None
try:
    from firebase_admin import credentials, initialize_app, firestore
except Exception:
    firestore = None  # used only if available

# Try to import agents. If unavailable, provide safe stubs so app keeps running.
try:
    from agents.sms_parser import parse_sms
except Exception as e:
    logging.warning(f"Could not import agents.sms_parser: {e}")
    def parse_sms(text):
        # Minimal safe fallback parser
        # Attempt to extract a number as amount, fallback values kept simple
        amount = 0.0
        currency = "PKR"
        description = text[:140]
        tx_type = "unknown"
        # crude numeric extraction
        import re
        m = re.search(r'(\d+[,\d]*\.?\d*)', text.replace(',', ''))
        if m:
            try:
                amount = float(m.group(1))
            except Exception:
                amount = 0.0
        return {"amount": amount, "currency": currency, "description": description, "type": tx_type}

try:
    from agents.fraud_detector import detect_fraud
except Exception as e:
    logging.warning(f"Could not import agents.fraud_detector: {e}")
    def detect_fraud(text):
        # Safe fallback: no fraud
        return {"fraud": False, "probability": 0.0, "risk_level": "LOW", "score": 0.0, "keywords_found": []}

try:
    from agents.ml_alert import detect_overspending
except Exception as e:
    logging.warning(f"Could not import agents.ml_alert: {e}")
    def detect_overspending(user_id, db=None):
        return {"overspending": False, "message": "no-db", "daily_average": None}

try:
    from agents.reminder_agent import send_reminder
except Exception as e:
    logging.warning(f"Could not import agents.reminder_agent: {e}")
    def send_reminder(user_id, reminder_id, db=None):
        return {"success": False, "error": "reminder-agent-missing"}

# App and logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pocketguardian")
app = Flask(__name__)
CORS(app)  # Allow cross-origin for mobile dev

# Firestore initialization (optional). Supports service-account.json or FIREBASE_KEY env var.
try:
    if firestore is not None:
        firebase_key = os.getenv("FIREBASE_KEY")
        if firebase_key:
            # If FIREBASE_KEY is a path to file, or JSON string
            if os.path.exists(firebase_key):
                cred = credentials.Certificate(firebase_key)
            else:
                cred_dict = json.loads(firebase_key)
                cred = credentials.Certificate(cred_dict)
            initialize_app(cred)
            db = firestore.client()
            logger.info("✅ Firestore initialized from FIREBASE_KEY")
        elif os.path.exists("service-account.json"):
            cred = credentials.Certificate("service-account.json")
            initialize_app(cred)
            db = firestore.client()
            logger.info("✅ Firestore initialized from service-account.json")
        else:
            logger.warning("Firestore not configured (no service-account.json and no FIREBASE_KEY). Running in demo mode.")
    else:
        logger.warning("firebase_admin not installed — continuing in demo mode.")
except Exception as e:
    logger.error(f"Firestore initialization failed: {e}")
    db = None

# -------------------------
# Health & debug endpoints
# -------------------------
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PocketGuardian Backend",
        "database": "connected" if db else "demo_mode",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/debug/routes", methods=["GET"])
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": sorted([m for m in rule.methods if m not in ("HEAD", "OPTIONS")]),
            "path": str(rule)
        })
    return jsonify({"routes": routes}), 200

# -------------------------
# Mobile endpoints (fast)
# -------------------------
@app.route("/api/mobile/health", methods=["GET"])
def mobile_health():
    return jsonify({
        "status": "healthy",
        "service": "PocketGuardian Mobile API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/mobile/demo", methods=["GET"])
def mobile_demo():
    return jsonify({
        "success": True,
        "message": "PocketGuardian Mobile API is working!",
        "endpoints": {
            "POST /api/mobile/analyze": "Analyze SMS for fraud",
            "GET /api/mobile/health": "Health check",
            "GET /api/mobile/demo": "This demo endpoint"
        },
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/mobile/analyze", methods=["POST"])
def mobile_analyze_sms():
    """Mobile-optimized SMS analysis: quick parse + fraud check + lightweight response"""
    try:
        data = request.get_json(silent=True) or {}
        sms_text = data.get("sms_text")
        user_id = data.get("user_id", "mobile_user")
        device_id = data.get("device_id", "mobile_device")
        timestamp = data.get("timestamp", datetime.now().isoformat())

        if not sms_text:
            return jsonify({"success": False, "error": "sms_text is required"}), 400

        # fast local analysis
        parsed = parse_sms(sms_text)
        fraud = detect_fraud(sms_text)

        response = {
            "success": True,
            "user_id": user_id,
            "device_id": device_id,
            "analysis": {
                "transaction": {
                    "amount": parsed.get("amount", 0.0),
                    "type": parsed.get("type", "unknown"),
                    "description": parsed.get("description", "")[:200],
                    "currency": parsed.get("currency", "PKR")
                },
                "fraud_analysis": fraud,
                "risk_level": fraud.get("risk_level", "LOW"),
                "urgency": "HIGH" if fraud.get("fraud") else "LOW"
            },
            "recommendations": {
                "block_transaction": fraud.get("fraud", False),
                "verify_manually": fraud.get("probability", 0) > 0.4,
                "alert_user": fraud.get("probability", 0) > 0.2
            },
            "timestamp": datetime.now().isoformat()
        }

        # light-write to Firestore (non-blocking best-effort)
        if db:
            try:
                tx_hash = hashlib.sha256(f"{user_id}{parsed.get('amount', 0)}{device_id}{timestamp}".encode()).hexdigest()
                db.collection("mobile_transactions").document(tx_hash).set({
                    "user_id": user_id,
                    "device_id": device_id,
                    "sms_text": sms_text,
                    "parsed_data": parsed,
                    "fraud_result": fraud,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "processed": False
                }, merge=True)
            except Exception as e:
                logger.warning(f"Failed to write mobile transaction to Firestore: {e}")

        return jsonify(response), 200

    except Exception as e:
        logger.exception("mobile_analyze_sms failed")
        return jsonify({"success": False, "error": "analysis failed", "details": str(e)}), 500

@app.route("/api/mobile/user/<user_id>/summary", methods=["GET"])
def mobile_user_summary(user_id):
    """Return a quick mobile dashboard summary"""
    try:
        summary = {
            "success": True,
            "user_id": user_id,
            "summary": {
                "today_spent": 0.0,
                "monthly_budget": 50000.0,
                "remaining_budget": 50000.0,
                "fraud_alerts": 0,
                "transactions_today": 0
            },
            "alerts": [],
            "timestamp": datetime.now().isoformat()
        }

        if db:
            try:
                today = datetime.now().date()
                transactions_ref = db.collection("transactions").where("user_id", "==", user_id)
                transactions = transactions_ref.stream()
                today_spent = 0.0
                today_count = 0
                for doc in transactions:
                    d = doc.to_dict()
                    tstamp = d.get("timestamp")
                    if tstamp and hasattr(tstamp, "date") and tstamp.date() == today:
                        if d.get("type") == "expense":
                            today_spent += float(d.get("amount", 0) or 0)
                        today_count += 1

                # fraud alerts count
                alerts_ref = db.collection("agent_logs").where("user_id", "==", user_id)
                alerts_q = alerts_ref.where("agent_name", "==", "Fraud Detector").stream()
                fraud_count = sum(1 for a in alerts_q if (a.to_dict().get("data", {}).get("fraud")))
                summary["summary"].update({
                    "today_spent": today_spent,
                    "remaining_budget": 50000.0 - today_spent,
                    "fraud_alerts": fraud_count,
                    "transactions_today": today_count
                })
            except Exception as e:
                logger.warning(f"Could not compute user summary from Firestore: {e}")

        return jsonify(summary), 200

    except Exception as e:
        logger.exception("mobile_user_summary failed")
        return jsonify({"success": False, "error": "summary failed", "details": str(e)}), 500

@app.route("/api/mobile/transactions", methods=["POST"])
def mobile_add_transaction():
    try:
        data = request.get_json(silent=True) or {}
        required = ["user_id", "amount", "type", "description", "device_id"]
        if not all(k in data for k in required):
            return jsonify({"success": False, "error": f"Missing required fields. Required: {required}"}), 400

        tx_id = hashlib.sha256(f"{data['user_id']}{data['amount']}{data['device_id']}{datetime.utcnow()}".encode()).hexdigest()
        tx_doc = {
            "user_id": data["user_id"],
            "amount": float(data["amount"]),
            "type": data["type"],
            "description": data["description"],
            "device_id": data["device_id"],
            "currency": data.get("currency", "PKR"),
            "category": data.get("category", "other"),
            "location": data.get("location", ""),
            "timestamp": firestore.SERVER_TIMESTAMP if firestore else datetime.utcnow(),
            "source": "mobile_app"
        }

        if db:
            try:
                db.collection("transactions").document(tx_id).set(tx_doc)
            except Exception as e:
                logger.warning(f"Failed to store transaction: {e}")

        return jsonify({"success": True, "transaction_id": tx_id, "timestamp": datetime.now().isoformat()}), 201

    except Exception as e:
        logger.exception("mobile_add_transaction failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/mobile/alerts", methods=["GET"])
def mobile_get_alerts():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "user_id required"}), 400

        alerts = []
        if db:
            try:
                alerts_ref = db.collection("agent_logs").where("user_id", "==", user_id)
                docs = alerts_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
                for doc in docs:
                    d = doc.to_dict()
                    alerts.append({
                        "id": doc.id,
                        "type": d.get("agent_name", "System"),
                        "message": d.get("action", "Alert"),
                        "data": d.get("data", {}),
                        "timestamp": d.get("timestamp"),
                        "read": False
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch alerts from Firestore: {e}")

        return jsonify({
            "success": True,
            "user_id": user_id,
            "alerts": alerts,
            "unread_count": len([a for a in alerts if not a.get("read", False)]),
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.exception("mobile_get_alerts failed")
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------
# Original / Dev endpoints
# -------------------------
@app.route("/api/analyze-sms", methods=["POST"])
def analyze_sms_full():
    """Full SMS analysis orchestration (used by Streamlit / web demo)"""
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id", "demo_user")
        sms_text = data.get("sms_text", "")
        if not sms_text:
            return jsonify({"success": False, "error": "sms_text required"}), 400

        parsed = parse_sms(sms_text)
        fraud = detect_fraud(sms_text)

        transaction_stored = False
        transaction_id = None
        if db and parsed.get("amount", 0) > 0:
            try:
                transaction_id = hashlib.sha256(f"{user_id}{parsed.get('amount')}{sms_text}{datetime.utcnow()}".encode()).hexdigest()
                db.collection("transactions").document(transaction_id).set({
                    "user_id": user_id,
                    "amount": parsed.get("amount"),
                    "type": parsed.get("type"),
                    "description": parsed.get("description"),
                    "currency": parsed.get("currency", "PKR"),
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                transaction_stored = True
            except Exception as e:
                logger.warning(f"Failed to store transaction: {e}")

        overspending = detect_overspending(user_id, db) if callable(detect_overspending) else {"overspending": False}

        needs_reminder = fraud.get("fraud") or overspending.get("overspending", False)
        reminder_created = False
        reminder_id = None
        reminder_result = None
        if needs_reminder and db:
            try:
                reminder_id = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                reminder_data = {
                    "user_id": user_id,
                    "message": "Fraud or overspending detected",
                    "type": "alert",
                    "priority": "high",
                    "due_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "sent": False,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                db.collection("reminders").document(reminder_id).set(reminder_data)
                reminder_created = True
                reminder_result = send_reminder(user_id, reminder_id, db)
            except Exception as e:
                logger.warning(f"Failed to create/send reminder: {e}")

        return jsonify({
            "success": True,
            "user_id": user_id,
            "analysis": {
                "parsed_transaction": parsed,
                "fraud_detection": fraud,
                "spending_analysis": overspending
            },
            "actions_taken": {
                "transaction_stored": transaction_stored,
                "transaction_id": transaction_id,
                "reminder_created": reminder_created,
                "reminder_id": reminder_id,
                "reminder_sent": reminder_result.get("success") if isinstance(reminder_result, dict) else False
            },
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.exception("analyze_sms_full failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/register", methods=["POST"])
def register_user_minimal():
    return jsonify({
        "success": True,
        "message": "Registration endpoint - use mobile endpoints for full functionality",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/transactions", methods=["POST"])
def add_transaction_minimal():
    return jsonify({
        "success": True,
        "message": "Transaction endpoint - use mobile endpoints for full functionality",
        "timestamp": datetime.now().isoformat()
    }), 200

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")
    logger.info(f"Starting PocketGuardian on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)

