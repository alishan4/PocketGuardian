import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Button, TextInput, Appbar, List, Chip } from 'react-native-paper';
import api from './src/services/api';

const PocketGuardianApp = () => {
  const [userId] = useState('user123');
  const [deviceId] = useState('device001');
  const [smsText, setSmsText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [userSummary, setUserSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const summary = await api.getUserSummary(userId);
      setUserSummary(summary);
      
      const alertsData = await api.getAlerts(userId, deviceId);
      setAlerts(alertsData.alerts || []);
    } catch (error) {
      Alert.alert('Error', 'Failed to load user data');
    }
  };

  const analyzeSMS = async () => {
    if (!smsText.trim()) {
      Alert.alert('Error', 'Please enter SMS text');
      return;
    }

    setLoading(true);
    try {
      const result = await api.analyzeSMS(userId, deviceId, smsText);
      setAnalysisResult(result);
      
      // Reload data after analysis
      loadUserData();
    } catch (error) {
      Alert.alert('Analysis Error', 'Failed to analyze SMS');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH': return '#ff4444';
      case 'MEDIUM': return '#ffaa00';
      case 'LOW': return '#00aa00';
      default: return '#666666';
    }
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="PocketGuardian" subtitle="Financial Protection" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {/* User Summary Card */}
        <Card style={styles.card}>
          <Card.Title title="Financial Summary" />
          <Card.Content>
            {userSummary ? (
              <View>
                <Text style={styles.summaryText}>
                  Today's Spending: Rs. {userSummary.summary?.today_spent?.toFixed(2)}
                </Text>
                <Text style={styles.summaryText}>
                  Remaining Budget: Rs. {userSummary.summary?.remaining_budget?.toFixed(2)}
                </Text>
                <Text style={styles.summaryText}>
                  Fraud Alerts: {userSummary.summary?.fraud_alerts}
                </Text>
              </View>
            ) : (
              <Text>Loading summary...</Text>
            )}
          </Card.Content>
        </Card>

        {/* SMS Analysis Card */}
        <Card style={styles.card}>
          <Card.Title title="Analyze Financial SMS" />
          <Card.Content>
            <TextInput
              label="Paste SMS here"
              value={smsText}
              onChangeText={setSmsText}
              multiline
              numberOfLines={3}
              style={styles.textInput}
            />
            <Button 
              mode="contained" 
              onPress={analyzeSMS}
              loading={loading}
              style={styles.button}
            >
              Analyze SMS
            </Button>
          </Card.Content>
        </Card>

        {/* Analysis Results */}
        {analysisResult && (
          <Card style={styles.card}>
            <Card.Title title="Analysis Results" />
            <Card.Content>
              <View style={styles.resultSection}>
                <Text style={styles.resultTitle}>Transaction Details:</Text>
                <Text>Amount: Rs. {analysisResult.analysis?.transaction?.amount}</Text>
                <Text>Type: {analysisResult.analysis?.transaction?.type}</Text>
              </View>

              <View style={styles.resultSection}>
                <Text style={styles.resultTitle}>Fraud Analysis:</Text>
                <Chip 
                  textStyle={{color: 'white'}}
                  style={{backgroundColor: getRiskColor(analysisResult.analysis?.risk_level)}}
                >
                  Risk: {analysisResult.analysis?.risk_level}
                </Chip>
                <Text>Fraud Detected: {analysisResult.analysis?.fraud_alert?.fraud ? 'YES' : 'NO'}</Text>
              </View>

              {analysisResult.actions?.block_transaction && (
                <View style={[styles.alertBox, {backgroundColor: '#ffebee'}]}>
                  <Text style={styles.alertText}>🚨 BLOCK RECOMMENDED: Potential fraud detected!</Text>
                </View>
              )}
            </Card.Content>
          </Card>
        )}

        {/* Alerts Section */}
        <Card style={styles.card}>
          <Card.Title title="Recent Alerts" />
          <Card.Content>
            {alerts.length > 0 ? (
              alerts.slice(0, 3).map((alert, index) => (
                <List.Item
                  key={index}
                  title={alert.type}
                  description={alert.message}
                  left={props => <List.Icon {...props} icon="alert" />}
                />
              ))
            ) : (
              <Text>No recent alerts</Text>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 10,
  },
  card: {
    marginVertical: 5,
    elevation: 2,
  },
  textInput: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
  resultSection: {
    marginVertical: 5,
  },
  resultTitle: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  alertBox: {
    padding: 10,
    borderRadius: 5,
    marginTop: 10,
  },
  alertText: {
    fontWeight: 'bold',
    color: '#d32f2f',
  },
  summaryText: {
    marginVertical: 2,
  },
});

export default PocketGuardianApp;