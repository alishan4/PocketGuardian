import axios from 'axios';

const API_BASE_URL = 'http://192.168.1.79:5000/api/mobile'; // Your backend IP

class PocketGuardianAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Analyze SMS
  async analyzeSMS(userId, deviceId, smsText) {
    try {
      const response = await this.client.post('/analyze', {
        user_id: userId,
        device_id: deviceId,
        sms_text: smsText,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('SMS Analysis Error:', error);
      throw error;
    }
  }

  // Get user summary
  async getUserSummary(userId) {
    try {
      const response = await this.client.get(`/user/${userId}/summary`);
      return response.data;
    } catch (error) {
      console.error('Summary Error:', error);
      throw error;
    }
  }

  // Add transaction
  async addTransaction(transactionData) {
    try {
      const response = await this.client.post('/transactions', transactionData);
      return response.data;
    } catch (error) {
      console.error('Transaction Error:', error);
      throw error;
    }
  }

  // Get alerts
  async getAlerts(userId, deviceId) {
    try {
      const response = await this.client.get('/alerts', {
        params: { user_id: userId, device_id: deviceId },
      });
      return response.data;
    } catch (error) {
      console.error('Alerts Error:', error);
      throw error;
    }
  }
}

export default new PocketGuardianAPI();