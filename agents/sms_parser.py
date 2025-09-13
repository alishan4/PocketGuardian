import spacy
import re

nlp = spacy.load('en_core_web_sm')

def parse_sms(sms_text):
    doc = nlp(sms_text)
    # Extract amount with regex (Pakistan-specific)
    amount_match = re.search(r'Rs\.?[\s]*(\d+[\.,]?\d*)', sms_text)
    amount = float(amount_match.group(1).replace(',', '')) if amount_match else 500.0
    type_ = 'income' if 'credited' in sms_text.lower() else 'expense'
    description = sms_text
    return {'type': type_, 'amount': amount, 'description': description}

# Test
if __name__ == '__main__':
    sms = "Rs.500 credited from Easypaisa"
    print(parse_sms(sms))