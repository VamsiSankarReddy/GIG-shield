# GigShield

**AI-Powered Parametric Insurance for Gig Economy Workers**

Automatic income protection from weather, pollution, and government-imposed restrictions.

---

## Overview

GigShield is a parametric insurance platform that provides gig economy delivery workers with automatic, instant payouts during income-loss events triggered by external disruptions. By leveraging AI-driven risk assessment and parametric claim mechanisms, GigShield eliminates claim processing delays and fraud while keeping premium costs low and predictable.

**Mission**: Ensure financial resilience for gig workers against forces beyond their control.

---

## Problem Statement

Gig economy workers face unprecedented income volatility:

- **Weather Disruptions**: Heavy rainfall reduces delivery demand by 40-60%
- **Environmental Hazards**: High pollution (AQI > 300) causes lockdowns and reduced activity
- **Government Restrictions**: Curfews, lockdowns, or transport bans eliminate earning opportunities
- **Current Insurance Gap**: Traditional insurance requires manual claims, extended processing, and subjective assessment—making it unaffordable and inaccessible for informal workers

Workers lack a reliable, automated income protection mechanism that doesn't require medical or accident documentation.

---

## Solution Description

GigShield provides **parametric (trigger-based) insurance** that automatically pays out when predefined environmental or administrative conditions are met—*without* requiring claim documentation or manual processing.

### Core Mechanism

1. **Risk Monitoring**: AI engine continuously monitors weather APIs, air quality indices, and government notifications
2. **Trigger Activation**: When conditions breach thresholds (e.g., rainfall > 50mm, AQI > 300, curfew declared), claims auto-activate
3. **Instant Payout**: Pre-calculated payouts transfer to worker accounts within seconds
4. **Fraud Prevention**: Machine learning models detect suspicious claim patterns and anomalies

This model shifts from **"claim reimbursement"** to **"automatic protection,"** making it fast, fair, and fraud-resistant.

---

## Target Users

- **Primary**: Delivery workers on platforms like Zomato, Swiggy, Dunzo
- **Secondary**: BikeShed, Rapido, and local logistics drivers
- **Geographic Focus**: Indian gig economy (extensible to Southeast Asia)
- **Income Profile**: ₹500-1,500/day average earnings; price-sensitive but risk-aware

---

## Key Features

### 1. AI Risk Engine
- **Real-time Risk Scoring**: Proprietary ML models assess immediate income-loss risk based on location, weather, time, and historical patterns
- **Predictive Analytics**: 48-hour forward risk forecasting to notify workers proactively
- **Personalized Profiles**: Risk scores adapt to worker preferences, vehicle type, and earning patterns

### 2. Weekly Pricing Model
- Transparent, predictable weekly premiums (₹49-99/week based on risk zone)
- No hidden fees; simple deductions from worker wallets
- Pay-per-week flexibility; no annual locks

### 3. Multi-Risk Parametric Triggers
Automatic claims activate when:

| Risk Event | Trigger Threshold | Payout |
|---|---|---|
| Heavy Rainfall | >50mm in 2 hours | ₹500-800 (50-80% daily avg) |
| High Pollution (AQI) | AQI > 300 for 4+ hours | ₹400-600 |
| Government Curfew | Notification-based (NDMA/state) | ₹700-1,000 (full day loss) |
| Transport Band | Public announcement (bus/auto strike) | ₹300-500 |

### 4. Instant Payouts
- Blockchain-verified automatic transfers
- Payout confirmation within 5 seconds of trigger
- No claim forms, no documentation, no verification lag

### 5. Fraud Detection
- **Behavioral Anomaly Detection**: ML flags suspicious claim patterns (e.g., claims only during specific hours, geographic clusters)
- **Device Fingerprinting**: Cross-reference worker app location vs. claim trigger zone
- **Temporal Analysis**: Detect workers claiming multiple events simultaneously
- **Third-party Validation**: Cross-check with real-time weather/pollution APIs

### 6. Dashboard
- Real-time account balance and claim history
- Active coverage zones and current risk levels
- Weekly earnings projection vs. protected earnings
- Claim status tracker with notification timeline

---

## System Workflow

```
1. Worker Signs Up
   ├─ Complete KYC (instant mobile verification)
   ├─ Link wallet & bank account
   └─ Select coverage zones (home delivery area)

2. AI Risk Assessment (Continuous)
   ├─ Ingest weather API (OpenWeatherMap), AQI data (CPCB), govt notifications
   ├─ Calculate real-time risk score per zone
   └─ Store risk vectors for pattern analysis

3. Weekly Premium Deduction
   ├─ Calculate premium based on selected zones + historical risk
   ├─ Auto-deduct from wallet each Sunday
   └─ Notify worker of coverage activation

4. External Event Occurs (Rain, Pollution, Curfew)
   ├─ AI detects parametric threshold breach
   ├─ Validate trigger against multiple data sources
   └─ Generate claim record (immutable)

5. Automatic Payout
   ├─ Verify worker eligibility (active coverage, no fraud flags)
   ├─ Calculate payout amount (zone-based, tiered)
   ├─ Initiate blockchain transaction
   └─ Send SMS/Push confirmation to worker

6. Fraud Check (Post-Payout)
   ├─ Run anomaly detection models
   ├─ Flag high-risk claims for review
   └─ Suspend coverage if fraud confirmed
```

---

## AI/ML Components

### 1. Risk Scoring Engine
- **Input**: Worker location, platform activity logs, weather forecast, historical claims
- **Model**: Gradient Boosting (XGBoost) + LSTM for temporal trends
- **Output**: Risk percentile (0-100) and recommended premium
- **Update Frequency**: Real-time (15-minute intervals)

### 2. Parametric Trigger Engine
- **Logic**: Rule-based thresholds + confidence scoring
- **Data Sources**: 
  - Weather: OpenWeatherMap, IMD APIs
  - AQI: Central Pollution Control Board (CPCB) real-time feeds
  - Government: NDMA notifications, state traffic police alerts
- **Validation**: Multi-source confirmation before claim activation

### 3. Fraud Detection Module
- **Isolation Forest**: Detect outlier claim patterns
- **Connection Analysis**: Identify collusion clusters (multiple workers claiming simultaneously)
- **Temporal Profiling**: Flag claims outside worker's active earning hours
- **Geospatial Validation**: Cross-check GPS location vs. trigger zone
- **Model Retraining**: Weekly updates with new claim data

---

## Integrations

### External APIs
- **Weather**: OpenWeatherMap (real-time & forecast)
- **Air Quality**: CPCB AQI feeds, BreezoMeter
- **Government Notifications**: NDMA (National Disaster Management Authority) APIs, state police portals
- **Payment**: Razorpay, UPI for instant payouts
- **SMS/Push**: Twilio, Firebase Cloud Messaging

### Mock Services (Development)
- Weather Simulator: Configurable rainfall/AQI events for testing
- Government Alert Simulator: Fake curfew/transport band notifications
- Blockchain Mock: Simulated claim recording (Ethereum Goerli testnet for demo)

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React.js + TypeScript | Worker dashboard & mobile web |
| **Backend** | Node.js (Express) / Python (FastAPI) | API gateway, claim processing |
| **Database** | PostgreSQL + Redis | Claim records, risk cache |
| **ML/AI** | Python (scikit-learn, XGBoost, TensorFlow) | Risk scoring, fraud detection |
| **Message Queue** | RabbitMQ / Kafka | Async event processing |
| **Blockchain** | Ethereum / Polygon | Immutable claim ledger (optional) |
| **DevOps** | Docker, Kubernetes, GitHub Actions | Containerization & deployment |
| **Monitoring** | Prometheus + Grafana | Real-time system health |

---

## Platform Justification

**Why Web App (Not Mobile-First)?**

1. **Instant Accessibility**: No app store dependencies; workers access via browser on any device
2. **Seamless Integration**: Embedded directly in Zomato/Swiggy ecosystem via WebView
3. **Lower Friction**: No installation required; reduces adoption barrier for price-sensitive users
4. **Real-time Syncing**: Automatic updates without manual app upgrades
5. **Cost Efficiency**: Reduced maintenance overhead for multiple mobile OS versions

**Responsive Design**: Mobile-optimized UI ensures excellent UX on 4" to 7" screens (primary access devices).

---

## Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- [ ] Worker authentication & KYC flow
- [ ] Weekly premium subscription (manual payout)
- [ ] Weather API integration (rainfall trigger only)
- [ ] Basic dashboard (balance, claim history)
- [ ] Manual fraud review interface

### Phase 2: AI-Driven Automation (Weeks 5-8)
- [ ] AI risk scoring engine (XGBoost model)
- [ ] Automated trigger logic (multi-risk: rainfall + AQI)
- [ ] Fraud detection (Isolation Forest model)
- [ ] Instant blockchain-based payouts (Polygon testnet)
- [ ] Admin dashboard for monitoring & model tuning

### Phase 3: Scale & Integration (Weeks 9-12)
- [ ] Live integration with Zomato/Swiggy APIs
- [ ] Government alert ingestion (NDMA, state police)
- [ ] Multi-zone coverage expansion
- [ ] A/B testing of premium pricing models
- [ ] Push notification system
- [ ] Advanced reporting & analytics

---

## Future Scope

### Extended Coverage (Post-MVP)
- **LPG/Fuel Price Surges**: Parametric triggers when fuel prices spike >20% weekly
- **Vehicle Maintenance**: Coverage for emergency repairs (engine failure, brake malfunction)
- **Health Micro-Insurance**: Optional add-on for hospitalization (>3 days) linked to claim events

### Geographic Expansion
- Indonesia, Philippines (Southeast Asia gig markets)
- Latin America (Brazil, Colombia delivery platforms)

### Platform Extensions
- B2B partnerships with delivery platforms for employer-subsidized premiums
- Integration with financial inclusion programs (microfinance linkage)
- Parametric bonds for platform operators to hedge payroll risk

---

## Conclusion

GigShield transforms income protection for gig workers from a reactive, bureaucratic process into an automatic, intelligent system. By combining parametric insurance mechanics with AI-driven risk assessment and fraud detection, we create a sustainable, scalable solution that protects workers *and* keeps premiums affordable.

**In a world where gig work is increasingly informal and volatile, GigShield ensures that external disruptions don't become personal financial crises.**

---

## Demo & Links

- **Live Dashboard**: [Link to hosted demo](#)
- **API Documentation**: [Link to API docs](#)
- **GitHub Repository**: [github.com/gigshield](#)
- **Pitch Deck**: [Link to presentation](#)
- **Contact**: team@gigshield.io

---

**GigShield: Delivering Security, One Delivery at a Time.**
