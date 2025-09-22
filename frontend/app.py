import streamlit as st
import requests
import json

st.title("PocketGuardian: Financial Assistant")

# Input form
st.header("Enter SMS for Analysis")
user_id = st.text_input("User ID", value="user123")
sms_text = st.text_area("SMS Text", value="Rs.1500 unauthorized debit from bank")

if st.button("Analyze SMS"):
    # Call backend API
    try:
       # This is the CORRECT line
backend_url = "https://alishan4-pocketguardian-backend.hf.space/api/agent_orchestrate"
response = requests.post(
    backend_url,
    json={"user_id": user_id, "sms_text": sms_text}
)
        if response.status_code == 200:
            result = response.json()
            st.success("Analysis Complete!")
            
            # Display results
            st.subheader("Parsed Data")
            st.json(result.get("parsed", {}))
            
            st.subheader("Fraud Detection")
            fraud = result.get("fraud", {})
            st.write(f"Fraud Detected: {fraud.get('fraud', False)} (Score: {fraud.get('score', 0.0)})")
            
            st.subheader("Overspending Alert")
            alert = result.get("alert", {})
            st.write(f"Overspending: {alert.get('overspending', False)} (Total: {alert.get('total', 0.0)}, Risk Score: {alert.get('risk_score', 0.0)})")
            
            st.subheader("Reminder Status")
            reminder = result.get("reminder_result", {})
            st.write(f"Reminder ID: {result.get('reminder_id', 'N/A')}")
            st.write(f"Status: {'Success' if reminder.get('success', False) else 'Failed'}")
            if not reminder.get("success"):
                st.write(f"Error: {reminder.get('error', 'Unknown')}")
        else:
            st.error(f"API Error: {response.text}")
    except Exception as e:
        st.error(f"Request failed: {str(e)}")

# Footer
st.markdown("---")
st.write("PocketGuardian © 2025 | Built by Ali Shan for financial inclusion in Pakistan")
