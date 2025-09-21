# PocketGuardian

A mobile-first AI agent to help freelancers, students, and small business owners in Pakistan track micro-payments, income, and savings, with automated reminders and spending insights.

## Overview
PocketGuardian uses AI (NLP and ML) to parse SMS/wallet notifications (e.g., Easypaisa, JazzCash), track transactions, send reminders for bills, and alert users about overspending. Built for scalability and demonstrated at AI hackathons.

## Features
- **Transaction Tracking**: Parses SMS for income/expense data using NLP (spaCy with Urdu support).
- **Automated Reminders**: Sends email/push notifications for bills and subscriptions.
- **Overspending Alerts**: ML-based anomaly detection (scikit-learn IsolationForest).
- **Dashboard**: Visualizes spending trends with Chart.js in a React Native app.

## Tech Stack
- **Backend**: Flask (Python) for REST API
- **Database**: Firebase Firestore (free tier) or SQLite
- **NLP**: spaCy + urduhack for English/Urdu SMS parsing
- **ML**: scikit-learn/TensorFlow for overspending prediction
- **Frontend**: React Native with react-native-chart-kit
- **Notifications**: Gmail SMTP (email) and Firebase Cloud Messaging (push)


