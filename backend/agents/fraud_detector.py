# from transformers import pipeline
# import logging

# logging.basicConfig(level=logging.DEBUG)

# # Load sentiment analysis model (proxy for fraud: negative = suspicious)
# classifier = pipeline("sentiment-analysis")

# def detect_fraud(sms_text):
#     try:
#         result = classifier(sms_text)[0]
#         score = result['score']
#         label = result['label']
#         if label == 'NEGATIVE' and score > 0.7:
#             logging.info(f"Fraud detected in SMS: {sms_text}, score: {score}")
#             return {'fraud': True, 'score': score}
#         return {'fraud': False, 'score': score}
#     except Exception as e:
#         logging.error(f"Fraud detection failed: {str(e)}")
#         return {'fraud': False, 'score': 0.0}

# # Test
# if __name__ == '__main__':
#     sms = "Rs.500 unauthorized debit from bank"
#     print(detect_fraud(sms))


from transformers import pipeline
import re
import logging

logging.basicConfig(level=logging.DEBUG)

# Fraud keywords commonly found in Pakistani scam messages
FRAUD_KEYWORDS = [
    'unauthorized', 'suspicious', 'verify', 'urgent', 'immediately',
    'account blocked', 'password expired', 'winning', 'prize', 'lottery',
    'free offer', 'click link', 'call now', 'urgent action'
]

try:
    classifier = pipeline("sentiment-analysis")
except Exception as e:
    logging.warning(f"Transformers model loading failed: {e}")
    classifier = None

def detect_fraud(sms_text):
    try:
        # Keyword-based detection
        sms_lower = sms_text.lower()
        keyword_matches = [word for word in FRAUD_KEYWORDS if word in sms_lower]
        
        # Pattern-based detection for common scams
        scam_patterns = [
            r'win\w*\s*\d+',  # winning messages
            r'prize\s*\d+',   # prize messages
            r'click\s*http',  # clickable links
            r'call\s*\d+'     # call now messages
        ]
        
        pattern_matches = []
        for pattern in scam_patterns:
            if re.search(pattern, sms_lower):
                pattern_matches.append(pattern)
        
        # Sentiment analysis if model available
        sentiment_score = 0.0
        if classifier:
            try:
                result = classifier(sms_text)[0]
                sentiment_score = result['score']
                # Negative sentiment + high confidence might indicate fraud
                if result['label'] == 'NEGATIVE' and sentiment_score > 0.8:
                    sentiment_score *= 1.5  # Boost score for negative sentiment
            except:
                pass
        
        # Calculate fraud probability
        fraud_probability = min(1.0, 
            (len(keyword_matches) * 0.2 + 
             len(pattern_matches) * 0.3 + 
             sentiment_score * 0.5)
        )
        
        is_fraud = fraud_probability > 0.6
        
        return {
            'fraud': is_fraud,
            'probability': round(fraud_probability, 2),
            'keywords_found': keyword_matches,
            'patterns_found': pattern_matches,
            'risk_level': 'HIGH' if is_fraud else 'MEDIUM' if fraud_probability > 0.4 else 'LOW'
        }
        
    except Exception as e:
        logging.error(f"Fraud detection failed: {str(e)}")
        return {'fraud': False, 'probability': 0.0, 'keywords_found': [], 'patterns_found': [], 'risk_level': 'UNKNOWN'}

# Test
if __name__ == '__main__':
    test_cases = [
        "Rs.500 unauthorized debit from bank",
        "Congratulations! You won 50000 rupees. Call 03001234567",
        "Your account will be blocked. Verify now: http://fake-bank.com",
        "Rs.1500 debited for groceries at Al-Fatah"
    ]
    
    for sms in test_cases:
        result = detect_fraud(sms)
        print(f"SMS: {sms}")
        print(f"Fraud Detection: {result}\n")