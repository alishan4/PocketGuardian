# # import pandas as pd
# # from sklearn.cluster import KMeans
# # from sklearn.linear_model import LogisticRegression
# # from firebase_admin import firestore, get_app, initialize_app, credentials
# # from dotenv import load_dotenv
# # import os
# # import logging

# # logging.basicConfig(level=logging.DEBUG)

# # load_dotenv()

# # # Conditional Firebase initialization
# # try:
# #     get_app()
# # except ValueError:
# #     try:
# #         firebase_key = os.getenv('FIREBASE_KEY')
# #         if not os.path.exists(firebase_key):
# #             raise FileNotFoundError(f"Firebase key file not found at {firebase_key}")
# #         cred = credentials.Certificate(firebase_key)
# #         initialize_app(cred)
# #         logging.info("Firestore initialized in ml_alert.py (standalone)")
# #     except Exception as e:
# #         logging.error(f"Firestore initialization failed in ml_alert.py: {str(e)}")
# #         raise

# # # Use Firebase client
# # db = firestore.client()
# # logging.info("Firestore client accessed in ml_alert.py")

# # os.environ["OMP_NUM_THREADS"] = "1"

# # def detect_overspending(user_id):
# #     try:
# #         # Fetch transactions
# #         transactions = db.collection('transactions').where('user_id', '==', user_id).stream()
# #         data = [{'amount': t.to_dict().get('amount', 0), 'type': t.to_dict().get('type', 'expense')} for t in transactions]
# #         df = pd.DataFrame(data)
# #         if df.empty or len(df[df['type'] == 'expense']) < 2:
# #             logging.info(f"Insufficient data for user_id {user_id}: {len(df)} transactions")
# #             return {'overspending': False, 'total': 0.0, 'risk_score': 0.0}
# #         expenses = df[df['type'] == 'expense']['amount'].values.reshape(-1, 1)
# #         kmeans = KMeans(n_clusters=min(2, len(expenses)), random_state=42)
# #         kmeans.fit(expenses)
# #         centers = kmeans.cluster_centers_
# #         threshold = centers.max() * 1.5
# #         total_expenses = expenses.sum()
# #         logging.debug(f"User {user_id}: centers={centers.flatten()}, threshold={threshold}, total={total_expenses}")
# #         # Logistic Regression for risk scoring
# #         labels = (expenses > threshold.mean()).astype(int)  # Mock labels
# #         log_reg = LogisticRegression(random_state=42)
# #         log_reg.fit(expenses, labels)
# #         risk_score = log_reg.predict_proba([[total_expenses]])[0][1]
# #         if total_expenses > threshold or risk_score > 0.7:
# #             return {'overspending': True, 'total': float(total_expenses), 'risk_score': float(risk_score)}
# #         return {'overspending': False, 'total': float(total_expenses), 'risk_score': float(risk_score)}
# #     except Exception as e:
# #         logging.error(f"Overspending detection failed for user_id {user_id}: {str(e)}")
# #         return {'overspending': False, 'total': 0.0, 'risk_score': 0.0}

# # if __name__ == '__main__':
# #     print(detect_overspending('user123'))

# import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.linear_model import LogisticRegression
# from firebase_admin import firestore
# import logging
# import os

# logging.basicConfig(level=logging.DEBUG)

# # def detect_overspending(user_id, db):

# def detect_overspending(user_id, db=None):
#     try:
#         # Fetch recent transactions (last 30 days)
#         transactions_ref = db.collection('transactions').where('user_id', '==', user_id)
#         transactions = transactions_ref.stream()
        
#         data = []
#         for t in transactions:
#             trans_data = t.to_dict()
#             data.append({
#                 'amount': float(trans_data.get('amount', 0)),
#                 'type': trans_data.get('type', 'expense'),
#                 'timestamp': trans_data.get('timestamp')
#             })
        
#         if not data or len([d for d in data if d['type'] == 'expense']) < 3:
#             return {
#                 'overspending': False, 
#                 'total_expenses': 0.0, 
#                 'risk_score': 0.0,
#                 'message': 'Insufficient data for analysis'
#             }
        
#         # Convert to DataFrame
#         df = pd.DataFrame(data)
#         expenses = df[df['type'] == 'expense']['amount']
        
#         if len(expenses) < 2:
#             return {
#                 'overspending': False,
#                 'total_expenses': float(expenses.sum()),
#                 'risk_score': 0.0,
#                 'message': 'Not enough expense data'
#             }
        
#         # Calculate spending patterns
#         daily_avg = expenses.mean()
#         spending_std = expenses.std()
#         total_expenses = expenses.sum()
        
#         # Simple rule-based detection
#         overspending_threshold = daily_avg * 3  # 3x average spending
        
#         # Cluster analysis for spending patterns
#         expense_values = expenses.values.reshape(-1, 1)
#         kmeans = KMeans(n_clusters=min(3, len(expense_values)), random_state=42, n_init=10)
#         clusters = kmeans.fit_predict(expense_values)
        
#         # Risk scoring based on outliers
#         latest_expense = expense_values[-1][0] if len(expense_values) > 0 else 0
#         is_outlier = latest_expense > overspending_threshold
        
#         # Simple risk score (0-1)
#         risk_score = min(1.0, latest_expense / max(overspending_threshold, 1))
        
#         overspending_detected = is_outlier or risk_score > 0.7
        
#         return {
#             'overspending': overspending_detected,
#             'total_expenses': float(total_expenses),
#             'daily_average': float(daily_avg),
#             'latest_expense': float(latest_expense),
#             'risk_score': round(risk_score, 2),
#             'threshold': float(overspending_threshold),
#             'message': f"High spending alert! {latest_expense} PKR exceeds average" if overspending_detected else "Spending normal"
#         }
        
#     except Exception as e:
#         logging.error(f"Overspending detection failed: {str(e)}")
#         return {
#             'overspending': False,
#             'total_expenses': 0.0,
#             'risk_score': 0.0,
#             'message': f'Analysis error: {str(e)}'
#         }

# if __name__ == '__main__':
#     # This would require Firebase initialization
#     print("ML Alert module loaded")

import pandas as pd
from sklearn.cluster import KMeans
from firebase_admin import firestore
import logging

logging.basicConfig(level=logging.DEBUG)

def detect_overspending(user_id, db=None):
    try:
        transactions_ref = db.collection('transactions').where('user_id', '==', user_id)
        transactions = transactions_ref.stream()

        data = []
        for t in transactions:
            trans_data = t.to_dict()
            data.append({
                'amount': float(trans_data.get('amount', 0)),
                'type': trans_data.get('type', 'expense'),
                'timestamp': trans_data.get('timestamp')
            })

        if not data or len([d for d in data if d['type'] == 'expense']) < 3:
            return {
                'overspending': False,
                'total_expenses': 0.0,
                'risk_score': 0.0,
                'message': 'Insufficient data for analysis'
            }

        df = pd.DataFrame(data)
        expenses = df[df['type'] == 'expense']['amount']

        if len(expenses) < 2:
            return {
                'overspending': False,
                'total_expenses': float(expenses.sum()),
                'risk_score': 0.0,
                'message': 'Not enough expense data'
            }

        daily_avg = expenses.mean()
        overspending_threshold = daily_avg * 3
        expense_values = expenses.values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=min(3, len(expense_values)), random_state=42, n_init=10)
        clusters = kmeans.fit_predict(expense_values)

        latest_expense = expense_values[-1][0] if len(expense_values) > 0 else 0
        is_outlier = latest_expense > overspending_threshold
        risk_score = min(1.0, latest_expense / max(overspending_threshold, 1))
        overspending_detected = is_outlier or risk_score > 0.7

        return {
            'overspending': overspending_detected,
            'total_expenses': float(expenses.sum()),
            'daily_average': float(daily_avg),
            'latest_expense': float(latest_expense),
            'risk_score': round(risk_score, 2),
            'threshold': float(overspending_threshold),
            'message': f"High spending alert! {latest_expense} PKR exceeds average" if overspending_detected else "Spending normal"
        }
    except Exception as e:
        logging.error(f"Overspending detection failed: {str(e)}")
        return {
            'overspending': False,
            'total_expenses': 0.0,
            'risk_score': 0.0,
            'message': f'Analysis error: {str(e)}'
        }

if __name__ == '__main__':
    print("ML Alert module loaded")