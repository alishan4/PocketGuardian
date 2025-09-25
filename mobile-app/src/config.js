export const CONFIG = {
  // Development
  DEVELOPMENT: {
    API_BASE_URL: 'http://192.168.1.79:5000/api/mobile',
    LOG_LEVEL: 'debug'
  },
  
  // Production
  PRODUCTION: {
    API_BASE_URL: 'https://your-backend.herokuapp.com/api/mobile',
    LOG_LEVEL: 'error'
  }
};

export const getConfig = () => {
  return __DEV__ ? CONFIG.DEVELOPMENT : CONFIG.PRODUCTION;
};