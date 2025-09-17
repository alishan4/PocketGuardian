from transformers import pipeline
import logging

logging.basicConfig(level=logging.DEBUG)

# Load sentiment analysis model (proxy for fraud: negative = suspicious)
classifier = pipeline("sentiment-analysis")

def detect_fraud(sms_text):
    try:
        result = classifier(sms_text)[0]
        score = result['score']
        label = result['label']
        if label == 'NEGATIVE' and score > 0.7:
            logging.info(f"Fraud detected in SMS: {sms_text}, score: {score}")
            return {'fraud': True, 'score': score}
        return {'fraud': False, 'score': score}
    except Exception as e:
        logging.error(f"Fraud detection failed: {str(e)}")
        return {'fraud': False, 'score': 0.0}

# Test
if __name__ == '__main__':
    sms = "Rs.500 unauthorized debit from bank"
    print(detect_fraud(sms))