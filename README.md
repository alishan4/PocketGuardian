#PocketGuardian: AI Multi-Agent Fintech System
Domain: Fintech (Financial Inclusion for Pakistan's freelancers/small businesses).
Overview: A multi-agent AI system parsing SMS for micro-payments, detecting overspending with ML, and sending reminders via FCM. Optimized for scalability with efficient Firestore updates.
Multi-Agent System:

SMS Parser Agent: Regex-based parsing for Pakistan SMS (e.g., Easypaisa).
ML Alert Agent: Threshold-based overspending detection.
Reminder Orchestrator Agent: Queues FCM notifications.

Google Integration: Firestore (database), FCM (notifications).
Database Schema:

users: {user_id, phone, email, name, fcm_token} (single doc per user, updated via set/update).
transactions: {user_id, type, amount, description, timestamp} (deduplicated by user_id, type, amount, description).
reminders: {user_id, message, due_date, sent, timestamp} (updated if matching user_id, message, due_date).
agent_logs: {agent_name, action, data, timestamp} (time-series logs).

Tech Stack

Backend: Flask (Python)
Database: Firestore
AI/ML: scikit-learn, spaCy (planned)
Notifications: FCM
Testing: Postman
Deployment: Render


How We Built It

Phase 1 : Set up Firestore, tested connectivity.
Phase 2 : Built APIs, optimized schema to entries and deduplicate transactions/reminders, added orchestration.
Phase 3 : NLP and ML agents.

