# 🛡️ ScamShield — AI-Powered Incoming Message Scam Detection & Protection Agent

> **Detect. Understand. Stay Safe.**  
> *Your AI-powered proactive protection against suspicious messages, fake KYC, phishing links, and social engineering.*

---

## 🌟 Executive Overview & Core Philosophy

Traditional spam detectors require the user to copy, paste, and manually submit every suspicious message. **ScamShield is fundamentally different:** it is a **Proactive AI Safety Agent** that automatically inspects incoming messages as they arrive across connected channels before the user interacts with them.

```
       Incoming Message (SMS / Email / Webhook / Stream)
                               ↓
                      SCAMSHIELD AI AGENT
                               ↓
                       Message Ingestion
                               ↓
                ┌──────────────┴──────────────┐
                ↓                             ↓
          NLP & Context                 Safe Server-Side
         Scam Heuristics                  URL Analyzer
                │                             │
                └──────────────┬──────────────┘
                               ↓
                     Transparent Risk Engine
                           (0–100 Score)
                               ↓
                     Explainable AI Engine
                    ("Why did ScamShield warn?")
                               ↓
                     Adaptive Notification
            (🟢 Low: Checked | 🟡 Suspicious | 🔴 High Alert)
                               ↓
                       Action Guidance
                 (❌ What NOT to do | ✅ Recommended)
```

---

## 🚀 Key Features

1. **Proactive Background Inspection**:
   - Zero copy-pasting required in normal operation.
   - Monitors connected channels in real-time.
   - Live WebSocket feed pushes new message analyses and stats instantly without refreshing.

2. **Modular Message Source Connector Architecture**:
   - **Gmail Inbound Safety Inspector**:
     - **Direct Gmail Input**: Web form to paste or type any Gmail message (From, Subject, Body) or load realistic sample phishing/legit presets.
     - **Live IMAP SSL Sync**: Connect directly to `imap.gmail.com:993` with your Gmail address & 16-character Google App Password to inspect unread or recent emails automatically.
   - **Android SMS**: Ingestion bridge simulating background SMS broadcasts.
   - **Email Inbox**: IMAP/OAuth2 inbound monitor.
   - **Security Webhooks**: Automated ingestion for custom feeds and client apps.
   - **Demo Simulator Stream**: Safe live simulator with preset and random test scenarios.
   - **Restricted Messaging Disclosure**: Clear permission warnings for restricted platforms (e.g., WhatsApp, Instagram, Telegram) stating: *"This message source requires permission or an approved integration."*

3. **Multi-Signal Context-Aware Analysis & False-Positive Control**:
   - **Not keyword-dependent**: A legitimate message like *"Your OTP for signing into your university account is 123456. Valid for 10 minutes. Do not share."* is safely recognized as authentic security advice and classified as **🟢 LOW RISK (~10/100)**.
   - Detects nuanced threat vectors: Fake KYC expiration, Bank impersonation, Advance-fee job scams, Lottery prizes, Subscription cancellations, Tech support malware scams.

4. **Safe Server-Side URL Analyzer**:
   - Protocol check (HTTPS vs insecure HTTP).
   - Raw IP address hostname check (e.g. `http://192.168.10.45/...`).
   - Obfuscated URL shortener detection (`bit.ly`, `tinyurl.com`, `t.co`, etc.).
   - Brand look-alike & typosquatting detection (e.g. `sbi-kyc-verify.top` vs official `onlinesbi.sbi`).
   - High-abuse generic TLD filtering (`.xyz`, `.top`, `.online`, `.club`).
   - Deceptive path keywords (`/kyc`, `/auth`, `/login`, `/claim`).

5. **Explainable AI (XAI)**:
   - Plain-English rationale answering: *"Why did ScamShield warn me?"*
   - Breaks down individual reasons: ⚠️ Urgency, 🔐 Sensitive Information, 🔗 Suspicious Link, 🎭 Possible Impersonation.
   - **Action Center**: Clear, non-fearmongering checklist of What NOT to do (❌) and Recommended steps (✅).

6. **Adaptive Alerting & Anti-Fatigue**:
   - **🟢 Low Risk (0–29)**: Quietly logged into timeline without disruptive modals.
   - **🟡 Suspicious (30–69)**: Subtle advisory notification.
   - **🔴 High Risk (70–100)**: Prominent action modal with optional audio chime.

7. **Privacy-First Design**:
   - **Minimal Metadata Mode**: Stores only SHA-256 integrity hashes and sanitized previews on disk.
   - One-click protection pause switch.
   - One-click history purge and source management.

---

## 📂 Architecture & Directory Structure

```
ScamShield/
├── run_scamshield.bat             # One-click Windows launcher
├── README.md
├── backend/
│   ├── main.py                    # FastAPI entrypoint, WebSockets, SPA static hosting
│   ├── requirements.txt           # Dependencies (fastapi, uvicorn, pydantic, aiofiles)
│   ├── api/                       # REST API route controllers
│   │   ├── agent.py               # /api/agent/start, /pause, /status
│   │   ├── messages.py            # /api/messages/incoming, /simulate-scenario
│   │   ├── alerts.py              # /api/alerts, /read, /mark-all-read
│   │   ├── history.py             # /api/history, /clear, search & filter
│   │   ├── sources.py             # /api/sources, /connect, /disconnect
│   │   └── settings.py            # /api/settings GET & POST
│   ├── agents/
│   │   └── scamshield_agent.py    # Master AI Agent orchestrating pipeline
│   ├── services/
│   │   ├── message_ingestion.py   # Normalization of message payloads
│   │   ├── message_analyzer.py    # Context NLP, threat patterns & false-positive filters
│   │   ├── url_analyzer.py        # Safe URL & lookalike inspection
│   │   ├── risk_engine.py         # Transparent 0-100 scoring
│   │   ├── explanation_engine.py  # Human-readable rationale & Don't/Do actions
│   │   └── notification_service.py # WebSocket real-time broadcast & adaptive tiers
│   ├── connectors/
│   │   ├── base_connector.py      # Abstract connector interface
│   │   ├── demo_connector.py      # Built-in simulator with preset scenarios
│   │   ├── sms_connector.py       # Android SMS background bridge
│   │   ├── email_connector.py     # OAuth2 IMAP inbox connector
│   │   └── webhook_connector.py   # Generic API webhook receiver
│   ├── ml/
│   │   └── classifier.py          # Hybrid local classifier (zero external cloud dependencies)
│   └── database/
│       ├── connection.py          # SQLite schema, migrations & privacy hashing
│       └── scamshield.db
└── frontend/                      # Modern React + Vite + Tailwind CSS dashboard
    ├── src/
    │   ├── components/            # Navbar, BottomNav, ProtectionHero, MetricCards, etc.
    │   ├── views/                 # Dashboard, Alerts, History, Sources, Safety, Settings
    │   ├── services/api.js        # API client, WebSocket subscriber & Web Audio chimes
    │   ├── App.jsx                # Core state & modal coordinator
    │   └── index.css              # Dark cybersecurity styling & animations
    └── dist/                      # Production compiled SPA bundle
```

---

## ⚡ Quick Start Guide

### 1. Launch with One Click
Double-click `run_scamshield.bat` in this folder, or run:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Then open your browser to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

*(The FastAPI server serves both the complete React UI and all backend APIs seamlessly!)*

### 2. Frontend Development Mode (Optional)
If you want to edit the React frontend with hot reload:
```bash
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** (automatically proxies to backend port 8000).

---

## 🧪 Testing & Demonstration Walkthrough

1. **Dashboard Overview**:
   - Notice the status: `🟢 Protection Active (Monitoring connected message sources)`.
   - Observe the 4 KPI metric cards: Messages Checked, Threats Detected, High Risk, Suspicious.
   - Click `Pause Protection` to see the status switch to `⚪ Protection Paused`. Click `Enable Protection` to resume.

2. **Simulate Preset Threat Scenarios**:
   - In the **Incoming Message Simulator** bar on the dashboard, click:
     - **Fake KYC**: Notice the instantaneous 🔴 **HIGH-RISK ALERT** modal popping up with Risk Score 95+/100, explaining the artificial urgency, fake SBI domain, and credential harvesting threat.
     - **Legitimate OTP (Test Safe)**: Notice that ScamShield recognizes the university sign-in OTP as **🟢 LOW RISK (10/100)** and records it quietly without panic modals!
     - **Job Scam**: Triggers a 🟡 **SUSPICIOUS / HIGH-RISK** warning for advance-fee requests.
     - **Normal Delivery**: Amazon delivery update verified as safe (8/100).

3. **Inspect Full Analysis**:
   - Click **View Full Analysis** on any card or alert modal.
   - See the 3-metric score header, executive summary, breakdown of reasons with severity icons, What NOT to do vs Recommended steps, and expandable **Technical Inspection Details** (revealing extracted URLs, domain lookalikes, IP address checks, and signal vectors).

4. **Interactive Simulator Studio**:
   - Navigate to the **Sources & Simulator** tab.
   - Type any custom sender (e.g. `Your Bank`, `Boss`, `Unknown`) and write any custom text.
   - Click **Simulate Incoming Message** to watch the AI Agent ingest and inspect your custom input in real-time.

5. **Alerts Center**:
   - Open **Alerts** to review unread warnings, mark as read, or filter by unresolved items.

6. **Safety Hub**:
   - Switch to **Safety Hub** to browse essential cyber-hygiene cards or use the **Spot The Scam** side-by-side comparison tool.

7. **Settings & Privacy**:
   - Adjust High-Risk and Suspicious sensitivity sliders.
   - Toggle **Minimal Metadata Mode** to enforce strict zero-storage of raw messages.
   - Click **Purge Logs** to wipe all historical records with a single click.

---

## 🔒 Privacy & Security Commitments

- **No Unauthorized Access**: ScamShield never falsely claims access to private third-party apps without explicit OS permissions or approved enterprise API keys.
- **Minimal Metadata**: Raw message content is never stored by default in privacy mode; only irreversible SHA-256 integrity hashes are retained.
- **Zero Cloud Dependence**: The detection and URL inspection pipeline runs entirely locally, safeguarding user data from third-party tracking.
