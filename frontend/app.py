# # import streamlit as st
# # import requests
# # import json

# # st.title("PocketGuardian: Financial Assistant")

# # # Input form
# # st.header("Enter SMS for Analysis")
# # user_id = st.text_input("User ID", value="user123")
# # sms_text = st.text_area("SMS Text", value="Rs.1500 unauthorized debit from bank")

# # if st.button("Analyze SMS"):
# #     # Call backend API
# #     try:
# #         response = requests.post(
# #             "http://localhost:5000/api/agent_orchestrate",
# #             json={"user_id": user_id, "sms_text": sms_text}
# #         )
# #         if response.status_code == 200:
# #             result = response.json()
# #             st.success("Analysis Complete!")
            
# #             # Display results
# #             st.subheader("Parsed Data")
# #             st.json(result.get("parsed", {}))
            
# #             st.subheader("Fraud Detection")
# #             fraud = result.get("fraud", {})
# #             st.write(f"Fraud Detected: {fraud.get('fraud', False)} (Score: {fraud.get('score', 0.0)})")
            
# #             st.subheader("Overspending Alert")
# #             alert = result.get("alert", {})
# #             st.write(f"Overspending: {alert.get('overspending', False)} (Total: {alert.get('total', 0.0)}, Risk Score: {alert.get('risk_score', 0.0)})")
            
# #             st.subheader("Reminder Status")
# #             reminder = result.get("reminder_result", {})
# #             st.write(f"Reminder ID: {result.get('reminder_id', 'N/A')}")
# #             st.write(f"Status: {'Success' if reminder.get('success', False) else 'Failed'}")
# #             if not reminder.get("success"):
# #                 st.write(f"Error: {reminder.get('error', 'Unknown')}")
# #         else:
# #             st.error(f"API Error: {response.text}")
# #     except Exception as e:
# #         st.error(f"Request failed: {str(e)}")

# # # Footer
# # st.markdown("---")
# # st.write("PocketGuardian © 2025 | Built by Ali Shan for financial inclusion in Pakistan")

# import streamlit as st
# import requests
# import json
# from datetime import datetime

# st.set_page_config(page_title="PocketGuardian", page_icon="💰", layout="wide")

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         color: #1E88E5;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .alert-box {
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin: 1rem 0;
#     }
#     .fraud-alert {
#         background-color: #ffebee;
#         border-left: 4px solid #f44336;
#     }
#     .spending-alert {
#         background-color: #fff3e0;
#         border-left: 4px solid #ff9800;
#     }
#     .success-alert {
#         background-color: #e8f5e8;
#         border-left: 4px solid #4caf50;
#     }
# </style>
# """, unsafe_allow_html=True)


# if st.button("Analyze SMS"):
#     # Call backend API
#     try:
#         # CORRECTED INDENTATION: The following lines are now correctly placed inside the 'try' block.
#         # backend_url = "https://alishan4-pocketguardian-backend.hf.space/api/agent_orchestrate"
#         backend_url = "https://alishan4-pocketguardian-backend.hf.space/api/analyze-sms"

#         response = requests.post(
#             backend_url,
#             json={"user_id": user_id, "sms_text": sms_text}
#         )
        
        
#         if response.status_code == 200:
#             result = response.json()
#             st.success("Analysis Complete!")
            
#             # Display results
#             st.subheader("Parsed Data")
#             st.json(result.get("parsed", {}))
            
#             st.subheader("Fraud Detection")
#             fraud = result.get("fraud", {})
#             st.write(f"Fraud Detected: {fraud.get('fraud', False)} (Score: {fraud.get('score', 0.0)})")
            
#             st.subheader("Overspending Alert")
#             alert = result.get("alert", {})
#             st.write(f"Overspending: {alert.get('overspending', False)} (Total: {alert.get('total', 0.0)}, Risk Score: {alert.get('risk_score', 0.0)})")
            
#             st.subheader("Reminder Status")
#             reminder = result.get("reminder_result", {})
#             st.write(f"Reminder ID: {result.get('reminder_id', 'N/A')}")
#             st.write(f"Status: {'Success' if reminder.get('success', False) else 'Failed'}")
#             if not reminder.get("success"):
#                 st.write(f"Error: {reminder.get('error', 'Unknown')}")
#         else:
#             st.error(f"API Error: {response.status_code} - {response.text}")
            
#     except requests.exceptions.RequestException as e:
#         st.error(f"Network request failed: Could not connect to the backend. Please ensure it is running. Error: {e}")
#     except Exception as e:
#         st.error(f"An unexpected error occurred: {e}")

# # Footer
# st.markdown("---")
# st.write("PocketGuardian © 2025 | Built by Ali Shan for financial inclusion in Pakistan")

# # Header
# st.markdown('<div class="main-header">💰 PocketGuardian AI</div>', unsafe_allow_html=True)
# st.markdown("### Smart Financial Protection for Pakistan")

# # Sidebar
# st.sidebar.title("Configuration")
# backend_url = st.sidebar.text_input("Backend URL", "http://localhost:7860")

# user_id = st.sidebar.text_input("User ID", "user123")

# # Main interface
# tab1, tab2, tab3 = st.tabs(["SMS Analysis", "Transaction History", "Demo"])

# with tab1:
#     st.header("📱 Analyze Financial SMS")
    
#     # Sample SMS templates
#     sample_sms = st.selectbox("Choose a sample SMS or write your own:", [
#         "Custom SMS",
#         "Rs.500 credited from Easypaisa",
#         "Rs.1500 unauthorized debit from HBL",
#         "You have received Rs.25000 salary",
#         "Rs.750 debited for Uber ride",
#         "Congratulations! You won 50000 rupees. Call now!",
#         "Rs.3000 paid for utility bills"
#     ])
    
#     if sample_sms == "Custom SMS":
#         sms_text = st.text_area("Enter your SMS text:", 
#                                "Rs.1500 debited for groceries at Al-Fatah")
#     else:
#         sms_text = st.text_area("SMS Text:", sample_sms)
    
#     if st.button("🔍 Analyze SMS", type="primary"):
#         with st.spinner("Analyzing transaction..."):
#             try:
#                 # response = requests.post(
#                 #     f"{backend_url}/api/analyze-sms",
#                 #     json={"user_id": user_id, "sms_text": sms_text},
#                 #     timeout=30

#                 response = requests.post(
#     backend_url,
#     json={"user_id": user_id, "sms_text": sms_text},
#     timeout=30
# )

                
                
#                 if response.status_code == 200:
#                     result = response.json()
                    
#                     if result['success']:
#                         st.success("✅ Analysis Complete!")
                        
#                         # Display results in columns
#                         col1, col2, col3 = st.columns(3)
                        
#                         with col1:
#                             st.subheader("💳 Transaction Details")
#                             parsed = result['analysis']['parsed_transaction']
#                             st.write(f"**Amount:** Rs. {parsed['amount']:,.2f}")
#                             st.write(f"**Type:** {parsed['type'].title()}")
#                             st.write(f"**Description:** {parsed['description']}")
                        
#                         with col2:
#                             st.subheader("🕵️ Fraud Analysis")
#                             fraud = result['analysis']['fraud_detection']
#                             risk_color = "red" if fraud['fraud'] else "orange" if fraud['probability'] > 0.4 else "green"
#                             st.write(f"**Risk Level:** :{risk_color}[{fraud['risk_level']}]")
#                             st.write(f"**Probability:** {fraud['probability']:.0%}")
#                             if fraud['keywords_found']:
#                                 st.write(f"**Keywords:** {', '.join(fraud['keywords_found'])}")
                        
#                         with col3:
#                             st.subheader("💰 Spending Analysis")
#                             spending = result['analysis']['spending_analysis']
#                             if spending.get('overspending'):
#                                 st.error(f"🚨 {spending['message']}")
#                             else:
#                                 st.success("✅ Spending normal")
#                             if spending.get('daily_average'):
#                                 st.write(f"**Daily Avg:** Rs. {spending['daily_average']:,.2f}")
                        
#                         # Actions taken
#                         st.subheader("📋 Actions Taken")
#                         actions = result['actions_taken']
#                         if actions['transaction_stored']:
#                             st.success(f"✅ Transaction stored (ID: {actions['transaction_id'][:8]}...)")
#                         if actions['reminder_created']:
#                             if actions['reminder_sent']:
#                                 st.success(f"✅ Reminder sent (ID: {actions['reminder_id'][:8]}...)")
#                             else:
#                                 st.info(f"ℹ️ Reminder created but not sent")
                        
#                         # Alert boxes
#                         if fraud['fraud']:
#                             st.markdown(f"""
#                             <div class="alert-box fraud-alert">
#                                 <h4>🚨 FRAUD ALERT DETECTED!</h4>
#                                 <p>This transaction shows signs of potential fraud. Please verify immediately.</p>
#                                 <p><strong>Risk Level:</strong> {fraud['risk_level']}</p>
#                                 <p><strong>Probability:</strong> {fraud['probability']:.0%}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
                        
#                         if spending.get('overspending'):
#                             st.markdown(f"""
#                             <div class="alert-box spending-alert">
#                                 <h4>⚠️ OVERSPENDING DETECTED!</h4>
#                                 <p>{spending['message']}</p>
#                                 <p><strong>Current Spending:</strong> Rs. {spending.get('latest_expense', 0):,.2f}</p>
#                                 <p><strong>Daily Average:</strong> Rs. {spending.get('daily_average', 0):,.2f}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
                    
#                     else:
#                         st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
#                 else:
#                     st.error(f"API Error {response.status_code}: {response.text}")
                    
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Connection error: {str(e)}")
#                 st.info("💡 Make sure the backend server is running on the specified URL")

# with tab2:
#     st.header("📊 Transaction History")
    
#     if st.button("🔄 Refresh Transactions"):
#         try:
#             response = requests.get(f"{backend_url}/api/user/{user_id}/transactions")
#             if response.status_code == 200:
#                 data = response.json()
#                 if data['success']:
#                     transactions = data['transactions']
                    
#                     if transactions:
#                         st.write(f"Found {len(transactions)} transactions")
                        
#                         # Display transactions in a table
#                         for i, trans in enumerate(transactions[:10]):  # Show last 10
#                             col1, col2, col3 = st.columns([1, 2, 1])
#                             with col1:
#                                 st.write(f"**Rs. {trans['amount']:,.2f}**")
#                             with col2:
#                                 st.write(trans['description'])
#                             with col3:
#                                 st.write(trans['type'].title())
#                             st.divider()
#                     else:
#                         st.info("No transactions found for this user")
#                 else:
#                     st.error(f"Failed to fetch transactions: {data.get('error')}")
#             else:
#                 st.error(f"API Error: {response.status_code}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# with tab3:
#     st.header("🎯 Hackathon Demo")
    
#     st.markdown("""
#     ### 🏆 AI-Powered Financial Protection
    
#     **PocketGuardian** demonstrates:
#     - ✅ **Real-time SMS parsing** for Pakistani financial messages
#     - ✅ **AI-powered fraud detection** using sentiment analysis and pattern matching
#     - ✅ **Smart spending alerts** using machine learning clustering
#     - ✅ **Automated reminders** for suspicious activities
#     - ✅ **Multi-agent orchestration** for comprehensive financial protection
    
#     ### 🚀 Quick Demo Steps:
#     1. Go to **SMS Analysis** tab
#     2. Select a sample SMS or write your own
#     3. Click **"Analyze SMS"** to see AI agents in action
#     4. View **fraud detection**, **spending analysis**, and **automated actions**
    
#     ### 💡 Use Cases for Pakistan:
#     - **Fraud Prevention**: Detect scam messages and unauthorized transactions
#     - **Budget Management**: Get alerts for unusual spending patterns
#     - **Financial Inclusion**: Help users understand their spending habits
#     - **Automated Protection**: 24/7 monitoring without user intervention
#     """)
    
#     # Demo statistics
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("SMS Parsing Accuracy", "95%", "2%")
#     with col2:
#         st.metric("Fraud Detection", "87%", "5%")
#     with col3:
#         st.metric("Response Time", "<2s", "-0.5s")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center;">
#     <p>Built with ❤️ for AI Hackathon | PocketGuardian © 2025</p>
#     <p>Empowering financial security in Pakistan through AI</p>
# </div>
# """, unsafe_allow_html=True)

import streamlit as st
import requests
from datetime import datetime

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="PocketGuardian", page_icon="💰", layout="wide")

# Sidebar config
st.sidebar.title("⚙️ Configuration")
backend_url = st.sidebar.text_input("Backend URL", "http://localhost:7860")
user_id = st.sidebar.text_input("User ID", "user123")

# ---------------------------
# STYLING
# ---------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .alert-danger {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 1rem;
        border-radius: 6px;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 1rem;
        border-radius: 6px;
    }
    .alert-success {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# API HELPERS
# ---------------------------
def api_post(path, payload):
    try:
        res = requests.post(f"{backend_url}{path}", json=payload, timeout=30)
        return res.status_code, res.json()
    except Exception as e:
        return 500, {"error": str(e)}

def api_get(path, params=None):
    try:
        res = requests.get(f"{backend_url}{path}", params=params, timeout=30)
        return res.status_code, res.json()
    except Exception as e:
        return 500, {"error": str(e)}

# ---------------------------
# HEADER
# ---------------------------
st.markdown('<div class="main-header">💰 PocketGuardian AI</div>', unsafe_allow_html=True)
st.markdown("### Smart Financial Protection for Pakistan 🇵🇰")

# ---------------------------
# TABS
# ---------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📱 SMS Analysis", "💳 Transactions", "🚨 Alerts", "📊 Summary", "👤 User Management"
])

# ---------------------------
# TAB 1: SMS ANALYSIS
# ---------------------------
with tab1:
    st.subheader("Analyze Financial SMS")

    sms_text = st.text_area("Paste your SMS text", "Rs.1500 unauthorized debit from bank")

    if st.button("🔍 Analyze SMS", type="primary"):
        status, result = api_post("/api/analyze-sms", {"user_id": user_id, "sms_text": sms_text})
        
        if status == 200 and result.get("success"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("#### 💳 Transaction")
                parsed = result["analysis"]["parsed_transaction"]
                st.write(f"**Amount:** Rs. {parsed['amount']:,.2f}")
                st.write(f"**Type:** {parsed['type'].title()}")
                st.write(f"**Description:** {parsed['description']}")

            with col2:
                st.markdown("#### 🕵️ Fraud Detection")
                fraud = result["analysis"]["fraud_detection"]
                if fraud["fraud"]:
                    st.markdown(f"<div class='alert-danger'><b>🚨 FRAUD DETECTED!</b><br>Risk: {fraud['risk_level']}<br>Probability: {fraud['probability']:.0%}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='alert-success'><b>✅ Safe</b><br>Risk: {fraud['risk_level']} ({fraud['probability']:.0%})</div>", unsafe_allow_html=True)

            with col3:
                st.markdown("#### 💰 Spending Analysis")
                spend = result["analysis"]["spending_analysis"]
                if spend.get("overspending"):
                    st.markdown(f"<div class='alert-warning'><b>⚠️ Overspending Alert</b><br>{spend['message']}</div>", unsafe_allow_html=True)
                else:
                    st.success("Spending within normal range")

            st.divider()
            st.markdown("#### 📋 Actions Taken")
            st.json(result["actions_taken"])
        else:
            st.error(f"Error {status}: {result.get('error')}")

# ---------------------------
# TAB 2: TRANSACTIONS
# ---------------------------
with tab2:
    st.subheader("Add Transaction")

    amount = st.number_input("Amount", min_value=0.0)
    tx_type = st.selectbox("Type", ["income", "expense"])
    description = st.text_input("Description", "Test transaction")

    if st.button("➕ Add Transaction"):
        status, result = api_post("/api/mobile/transactions", {
            "user_id": user_id,
            "amount": amount,
            "type": tx_type,
            "description": description,
            "device_id": "streamlit"
        })
        if status in [200, 201]:
            st.success("Transaction saved ✅")
            st.json(result)
        else:
            st.error(result)

# ---------------------------
# TAB 3: ALERTS
# ---------------------------
with tab3:
    st.subheader("Latest Alerts")
    if st.button("🔄 Refresh Alerts"):
        status, result = api_get("/api/mobile/alerts", {"user_id": user_id})
        if status == 200 and result.get("success"):
            for alert in result["alerts"]:
                st.markdown(f"""
                <div class='card'>
                    <b>{alert['type']}</b>: {alert['message']} <br>
                    <small>{alert['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(result)

# ---------------------------
# TAB 4: SUMMARY
# ---------------------------
with tab4:
    st.subheader("User Summary")
    if st.button("📊 Load Summary"):
        status, result = api_get(f"/api/mobile/user/{user_id}/summary")
        if status == 200 and result.get("success"):
            col1, col2, col3, col4 = st.columns(4)
            summary = result["summary"]
            col1.metric("Today Spent", f"Rs {summary['today_spent']:,.2f}")
            col2.metric("Monthly Budget", f"Rs {summary['monthly_budget']:,.2f}")
            col3.metric("Remaining", f"Rs {summary['remaining_budget']:,.2f}")
            col4.metric("Fraud Alerts", summary['fraud_alerts'])
        else:
            st.error(result)

# ---------------------------
# TAB 5: USER MGMT
# ---------------------------
with tab5:
    st.subheader("Register New User")

    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("👤 Register User"):
        status, result = api_post("/api/register", {
            "user_id": user_id,
            "name": name,
            "phone": phone,
            "email": email
        })
        if status == 200 and result.get("success"):
            st.success("User registered ✅")
            st.json(result)
        else:
            st.error(result)

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.markdown("<div style='text-align:center'>Built with ❤️ for AI Hackathon | PocketGuardian © 2025</div>", unsafe_allow_html=True)
