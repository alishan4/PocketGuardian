# # import spacy
# # import re

# # nlp = spacy.load('en_core_web_sm')

# # def parse_sms(sms_text):
# #     doc = nlp(sms_text)
# #     # Extract amount with regex (Pakistan-specific)
# #     amount_match = re.search(r'Rs\.?[\s]*(\d+[\.,]?\d*)', sms_text)
# #     amount = float(amount_match.group(1).replace(',', '')) if amount_match else 500.0
# #     type_ = 'income' if 'credited' in sms_text.lower() else 'expense'
# #     description = sms_text
# #     return {'type': type_, 'amount': amount, 'description': description}

# # # Test
# # if __name__ == '__main__':
# #     sms = "Rs.500 credited from Easypaisa"
# #     print(parse_sms(sms))


# import spacy
# import re
# import logging

# logging.basicConfig(level=logging.DEBUG)

# # Load spaCy model
# try:
#     nlp = spacy.load('en_core_web_sm')
# except OSError:
#     logging.warning("spaCy model not found. Installing...")
#     import os
#     os.system("python -m spacy download en_core_web_sm")
#     nlp = spacy.load('en_core_web_sm')

# def parse_sms(sms_text):
#     try:
#         doc = nlp(sms_text)
#         # Enhanced regex for Pakistani SMS formats
#         amount_match = re.search(r'Rs\.?[\s]*(\d+[\.,]?\d*)', sms_text)
#         amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
        
#         # Detect transaction type
#         sms_lower = sms_text.lower()
#         if any(word in sms_lower for word in ['credited', 'received', 'deposit']):
#             type_ = 'income'
#         elif any(word in sms_lower for word in ['debited', 'paid', 'purchase', 'withdrawal']):
#             type_ = 'expense'
#         else:
#             type_ = 'expense'  # default
            
#         description = sms_text[:100]  # Limit description length
        
#         return {
#             'type': type_, 
#             'amount': amount, 
#             'description': description,
#             'currency': 'PKR'
#         }
#     except Exception as e:
#         logging.error(f"SMS parsing failed: {str(e)}")
#         return {'type': 'expense', 'amount': 0.0, 'description': 'Parsing failed', 'currency': 'PKR'}

# # Test
# if __name__ == '__main__':
#     test_sms = [
#         "Rs.500 credited from Easypaisa",
#         "Rs.1500 debited for utility bill",
#         "You have received Rs.25000 salary"
#     ]
#     for sms in test_sms:
#         print(f"SMS: {sms}")
#         print(f"Parsed: {parse_sms(sms)}\n")

import spacy
import re
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.warning("spaCy model not found. Installing...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load('en_core_web_sm')

def parse_sms(sms_text):
    try:
        doc = nlp(sms_text)
        amount_match = re.search(r'Rs\.?[\s]*(\d+[\.,]?\d*)', sms_text)
        amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
        sms_lower = sms_text.lower()
        if any(word in sms_lower for word in ['credited', 'received', 'deposit']):
            type_ = 'income'
        elif any(word in sms_lower for word in ['debited', 'paid', 'purchase', 'withdrawal']):
            type_ = 'expense'
        else:
            type_ = 'expense'
        description = sms_text[:100]
        return {
            'type': type_,
            'amount': amount,
            'description': description,
            'currency': 'PKR'
        }
    except Exception as e:
        logging.error(f"SMS parsing failed: {str(e)}")
        return {'type': 'expense', 'amount': 0.0, 'description': 'Parsing failed', 'currency': 'PKR'}

if __name__ == '__main__':
    test_sms = [
        "Rs.500 credited from Easypaisa",
        "Rs.1500 debited for utility bill",
        "You have received Rs.25000 salary"
    ]
    for sms in test_sms:
        print(f"SMS: {sms}")
        print(f"Parsed: {parse_sms(sms)}\n")