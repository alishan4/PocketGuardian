# PocketGuardian

A mobile-first AI agent for freelancers, students, and small business owners in Pakistan to track micro-payments, income, and savings with automated reminders and ML-based insights.

## Overview
PocketGuardian parses SMS notifications, stores transactions in Firestore, sends reminders via FCM, and provides ML alerts for overspending. Built with Flask backend, React Native frontend, and scikit-learn ML.

## Features
- SMS parsing with NLP (spaCy).
- Transaction storage and reminders in Firestore.
- ML alerts for overspending (K-Means clustering).
- Dashboard with React Native and Chart.js.

## Tech Stack
- Backend: Flask (Python), Firebase Admin SDK
- Database: Firebase Firestore
- ML/NLP: scikit-learn, spaCy
- Frontend: React Native
- Notifications: FCM
- Testing: Postman
- Deployment: Render

## How We Built It
- **Phase 1 (Sep 12)**: Set up Firestore, tested connectivity.
- **Phase 2 (Sep 12-13)**: Built APIs, optimized schema to update `user_id` (e.g., `user123`) without new collections, added orchestration.
- **Phase 3 (Next)**: NLP and ML agents.
