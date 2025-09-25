from flask import Blueprint, request, jsonify
import hashlib
from datetime import datetime
import logging
from agents.sms_parser import parse_sms
from agents.fraud_detector import detect_fraud

# Create mobile API blueprint with unique name
mobile_api = Blueprint('mobile_api_v1', __name__)

@mobile_api.route('/api/mobile/analyze', methods=['POST'])
def mobile_analyze_sms():
    """Mobile-optimized SMS analysis endpoint"""
    try:
        data = request.get_json()
        
        # Required fields
        user_id = data.get('user_id', 'mobile_user')
        sms_text = data.get('sms_text', '')
        device_id = data.get('device_id', 'mobile_device')
        
        if not sms_text:
            return jsonify({
                'success': False,
                'error': 'SMS text is required'
            }), 400
        
        # Fast analysis for mobile
        parsed_data = parse_sms(sms_text)
        fraud_result = detect_fraud(sms_text)
        
        # Mobile-optimized response
        response = {
            'success': True,
            'user_id': user_id,
            'device_id': device_id,
            'analysis': {
                'transaction': {
                    'amount': parsed_data['amount'],
                    'type': parsed_data['type'],
                    'description': parsed_data['description'],
                    'currency': parsed_data.get('currency', 'PKR')
                },
                'fraud_analysis': fraud_result,
                'risk_level': fraud_result.get('risk_level', 'LOW'),
                'urgency': 'HIGH' if fraud_result.get('fraud') else 'LOW'
            },
            'recommendations': {
                'block_transaction': fraud_result.get('fraud', False),
                'verify_manually': fraud_result.get('probability', 0) > 0.4,
                'alert_user': fraud_result.get('probability', 0) > 0.2
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Mobile analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Analysis failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@mobile_api.route('/api/mobile/health', methods=['GET'])
def mobile_health():
    """Mobile health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PocketGuardian Mobile API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@mobile_api.route('/api/mobile/demo', methods=['GET'])
def mobile_demo():
    """Demo endpoint for mobile testing"""
    return jsonify({
        'success': True,
        'message': 'PocketGuardian Mobile API is working!',
        'endpoints': {
            'POST /api/mobile/analyze': 'Analyze SMS for fraud',
            'GET /api/mobile/health': 'Health check',
            'GET /api/mobile/demo': 'This demo endpoint'
        },
        'timestamp': datetime.now().isoformat()
    })