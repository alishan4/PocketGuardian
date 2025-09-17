import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from firebase_admin import firestore, get_app, initialize_app, credentials
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Conditional Firebase initialization
try:
    get_app()
except ValueError:
    try:
        firebase_key = os.getenv('FIREBASE_KEY')
        if not os.path.exists(firebase_key):
            raise FileNotFoundError(f"Firebase key file not found at {firebase_key}")
        cred = credentials.Certificate(firebase_key)
        initialize_app(cred)
        logging.info("Firestore initialized in ml_alert.py (standalone)")
    except Exception as e:
        logging.error(f"Firestore initialization failed in ml_alert.py: {str(e)}")
        raise

# Use Firebase client
db = firestore.client()
logging.info("Firestore client accessed in ml_alert.py")

os.environ["OMP_NUM_THREADS"] = "1"

def detect_overspending(user_id):
    try:
        # Fetch transactions
        transactions = db.collection('transactions').where('user_id', '==', user_id).stream()
        data = [{'amount': t.to_dict().get('amount', 0), 'type': t.to_dict().get('type', 'expense')} for t in transactions]
        df = pd.DataFrame(data)
        if df.empty or len(df[df['type'] == 'expense']) < 2:
            logging.info(f"Insufficient data for user_id {user_id}: {len(df)} transactions")
            return {'overspending': False, 'total': 0.0, 'risk_score': 0.0}
        expenses = df[df['type'] == 'expense']['amount'].values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=min(2, len(expenses)), random_state=42)
        kmeans.fit(expenses)
        centers = kmeans.cluster_centers_
        threshold = centers.max() * 1.5
        total_expenses = expenses.sum()
        logging.debug(f"User {user_id}: centers={centers.flatten()}, threshold={threshold}, total={total_expenses}")
        # Logistic Regression for risk scoring
        labels = (expenses > threshold.mean()).astype(int)  # Mock labels
        log_reg = LogisticRegression(random_state=42)
        log_reg.fit(expenses, labels)
        risk_score = log_reg.predict_proba([[total_expenses]])[0][1]
        if total_expenses > threshold or risk_score > 0.7:
            return {'overspending': True, 'total': float(total_expenses), 'risk_score': float(risk_score)}
        return {'overspending': False, 'total': float(total_expenses), 'risk_score': float(risk_score)}
    except Exception as e:
        logging.error(f"Overspending detection failed for user_id {user_id}: {str(e)}")
        return {'overspending': False, 'total': 0.0, 'risk_score': 0.0}

if __name__ == '__main__':
    print(detect_overspending('user123'))