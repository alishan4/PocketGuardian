# PocketGuardian: Your AI Financial Assistant

**PocketGuardian is an intelligent financial assistant designed to promote financial inclusion in Pakistan by automatically analyzing SMS messages for fraud and spending habits.**



## The Problem
In Pakistan, millions rely on mobile banking and services like Easypaisa, but financial literacy can be a challenge. Users are often overwhelmed by transaction messages, are vulnerable to sophisticated scams, and lack easy-to-use tools for tracking their spending.

## Our Solution
PocketGuardian is a multi-agent AI system that acts as a personal financial guardian. A user simply provides a financial SMS, and our system automatically:
1.  **Parses** the message to extract key data (amount, type, description).
2.  **Detects** potential fraud using a Transformer-based sentiment model.
3.  **Analyzes** spending patterns with machine learning to alert users of overspending.
4.  **Notifies** the user immediately with actionable alerts via push notifications.

---

## Technical Architecture
Our system uses a microservice-oriented, multi-agent architecture:
- **Frontend:** Streamlit, for a simple and interactive user interface.
- **Backend:** Flask, orchestrated as a multi-agent system on Hugging Face Spaces.
- **Database:** Google Firestore, for scalable and real-time data storage.
- **AI Agents:**
  - **SMS Parser:** spaCy & Regex
  - **Fraud Detector:** Hugging Face Transformers (Sentiment Analysis)
  - **Overspending Alert:** Scikit-learn (KMeans Clustering)
  - **Reminder Agent:** Firebase Cloud Messaging (FCM)

---

## How to Use
1.  Visit our live app: [Link to your Streamlit App]
2.  Enter a User ID (e.g., `user123`).
3.  Paste a financial SMS message.
4.  Click "Analyze SMS" to see the AI agents in action!
