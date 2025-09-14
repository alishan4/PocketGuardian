import pandas as pd
from sklearn.cluster import KMeans
from firebase_admin import firestore, get_app
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.DEBUG)

# Use existing Firebase app
try:
    db = firestore.client()
    logging.info("Firestore client accessed in ml_alert.py")
except Exception as e:
    logging.error(f"Firestore access failed in ml_alert.py: {str(e)}")
    raise

def detect_overspending(user_id):
    try:
        # Fetch transactions
        transactions = db.collection('transactions').where('user_id', '==', user_id).stream()
        data = [{'amount': t.to_dict().get('amount', 0), 'type': t.to_dict().get('type', 'expense')} for t in transactions]
        df = pd.DataFrame(data)
        if df.empty or len(df[df['type'] == 'expense']) < 2:
            logging.info(f"Insufficient data for user_id {user_id}: {len(df)} transactions")
            return {'overspending': False, 'total': 0.0}
        expenses = df[df['type'] == 'expense']['amount'].values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=min(2, len(expenses)), random_state=42)
        kmeans.fit(expenses)
        centers = kmeans.cluster_centers_
        threshold = centers.max() * 1.5  # Anomaly threshold
        total_expenses = expenses.sum()
        logging.debug(f"User {user_id}: centers={centers.flatten()}, threshold={threshold}, total={total_expenses}")
        if total_expenses > threshold:
            return {'overspending': True, 'total': float(total_expenses)}
        return {'overspending': False, 'total': float(total_expenses)}
    except Exception as e:
        logging.error(f"Overspending detection failed for user_id {user_id}: {str(e)}")
        return {'overspending': False, 'total': 0.0}

if __name__ == '__main__':
    print(detect_overspending('user123'))