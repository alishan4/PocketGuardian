# 💰 PocketGuardian: AI Financial Assistant

**PocketGuardian** is a multi-agent, AI-powered app that automatically analyzes your financial SMS messages to protect you from fraud and overspending—designed for mobile banking users in Pakistan.

---

## **The Problem**

Millions in Pakistan use mobile banking (Easypaisa, JazzCash, etc.), but:
- SMS transaction alerts are hard to understand.
- Scams are increasing, and users are vulnerable.
- No easy way to track weekly/monthly spending or stay within budget.

---

## **Our Solution**

**PocketGuardian** uses advanced AI agents to:
- **Parse any SMS** (e.g. "Rs.1500 debited for groceries" or "Congratulations! You won 50,000 rupees") and extract transaction details.
- **Detect fraud/scams** using a fine-tuned Hugging Face Transformer (not every message is fraud! Only suspicious ones are flagged).
- **Track weekly and monthly spending** for each user, updating in real time.
- **Alert users** if they're overspending (e.g. "You have spent 80% of your monthly budget") or if a message is likely a scam.
- **Remind users** about dangerous or costly behavior via push notifications.

---

## **How It Works **

1. **User Registration:**  
   - Register with your phone, email, and set your weekly/monthly budget limits.

2. **Paste or Forward Any Financial SMS:**  
   - The app automatically analyzes the message:
     - Is it a valid transaction? (debited/credited)
     - Is it a potential scam or fraud? (using AI + local rules)

3. **Results Are Displayed Instantly:**
   - **Transaction details** (amount, type, description)
   - **Fraud detection** (with risk level, keywords/patterns found)
   - **Spending analysis** (progress bars for weekly/monthly limits, overspending alerts)
   - **Alerts and reminders** (push notifications, dashboard icons)

4. **All user activity and agent actions are logged in Firestore for transparency.**

---

## **Technical Architecture**

- **Frontend:** Streamlit app (mobile-ready, beautiful UX)
- **Backend:** Flask, multi-agent orchestration (SMS parser, fraud detector, spending analyzer, reminder agent)
- **AI Agents:**
  - *SMS Parser*: spaCy + Regex
  - *Fraud Detector*: Hugging Face Transformers (fine-tuned for Pakistani banking SMS, only real frauds flagged)
  - *Spending Analysis*: Scikit-learn (KMeans), weekly/monthly budget tracking
  - *Reminder Agent*: Firebase Cloud Messaging
- **Database:** Google Firestore (users, transactions, agent logs, alerts, reminders)
- **Flexible:** Works with any SMS text, easy to integrate, real-time dashboard

---

## **How to Check It **

1. **Go to the PocketGuardian Streamlit app.**
2. **Register a user** (set your limits).
3. **Paste an SMS** in the "Analyze" tab (try a transaction and a scam message).
4. **See results:**
   - Fraud? Overspending? Transaction tracked?
   - Progress bars for budgets, alerts for risky behavior.
5. **Add transactions manually or view latest alerts/summary.**
6. **All analysis is instant, AI-powered, and stored securely.**

---

## **Why It Matters**

- Protects vulnerable users from financial scams.
- Empowers users to manage their money smartly, stay on budget, and learn safe habits.
- Shows the power of multi-agent AI for real-world problems.

---

## **Summary**

> **PocketGuardian is your personal AI financial guardian. Paste any SMS—instantly see if it's a scam, track your spending, and get alerts before you overspend. All powered by state-of-the-art AI, beautifully visualized, and ready for Pakistan's mobile banking revolution.**

---

**Try it now and see your financial safety in action!**
