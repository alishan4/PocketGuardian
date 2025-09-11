# PocketGuardian
AI agent for tracking micro-payments and sending alerts.

## Setup
1. Clone repo: `git clone https://github.com/your-username/pocketguardian.git`
2. Create virtual env: `python -m venv venv; source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Add `service-account.json` for Firebase.
5. Run: `python backend/app.py`



## Backend API
- **POST /api/register**: Registers a user with phone, email, name, and FCM token.
- **POST /api/transactions**: Stores transaction data (user_id, type, amount, description, timestamp) in Firestore. Validates type (income/expense) and user existence. Tested with Postman.
- **POST /api/reminders**: Stores reminder data (user_id, message, due_date, sent, timestamp) in Firestore. Validates inputs and user existence. Tested with Postman.