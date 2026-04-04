# How to Run This Project

A complete step-by-step guide to run the Parametric Insurance demo from scratch.

---

## Prerequisites (Install These First)

You need two things installed on your computer before starting:

### 1. Python (version 3.10 or higher)

- Download from: https://www.python.org/downloads/
- During installation, **CHECK the box that says "Add Python to PATH"** — this is very important
- To verify it installed correctly, open a terminal and type:
  ```
  python --version
  ```
  You should see something like `Python 3.12.x`

### 2. Node.js (version 18 or higher)

- Download from: https://nodejs.org/ (pick the LTS version)
- Install with default settings
- To verify, open a terminal and type:
  ```
  node --version
  npm --version
  ```
  You should see version numbers for both

---

## Step-by-Step Setup

Open a terminal (Command Prompt, PowerShell, or VS Code terminal) and follow these steps.

---

### Step 1: Navigate to the project folder

```
cd path\to\GWDT
```

Replace `path\to\GWDT` with wherever you saved this project folder. For example:
```
cd C:\Users\YourName\Desktop\project\GWDT
```

---

### Step 2: Set up the Backend

#### 2a. Go into the backend folder

```
cd backend
```

#### 2b. Create a virtual environment

```
python -m venv venv
```

This creates a folder called `venv` inside `backend`. It keeps all Python packages isolated.

#### 2c. Activate the virtual environment

**On Windows (Command Prompt):**
```
venv\Scripts\activate
```

**On Windows (PowerShell):**
```
.\venv\Scripts\activate
```

**On Mac/Linux:**
```
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line. That means it worked.

#### 2d. Install Python dependencies

```
pip install fastapi "uvicorn[standard]"
```

Wait for it to finish downloading.

#### 2e. Start the backend server

```
uvicorn app:app --port 8080 --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Started reloader process
```

**Leave this terminal running. Do NOT close it.**

---

### Step 3: Set up the Frontend

Open a **new/second terminal window** (keep the backend terminal running).

#### 3a. Navigate to the frontend folder

```
cd path\to\GWDT\frontend
```

For example:
```
cd C:\Users\YourName\Desktop\project\GWDT\frontend
```

#### 3b. Install Node.js dependencies

```
npm install
```

Wait for it to finish. You might see some warnings — that's fine, ignore them.

#### 3c. Start the frontend dev server

```
npm run dev
```

You should see output like:
```
VITE v8.x.x  ready in 500ms

➜  Local:   http://localhost:5173/
```

**Leave this terminal running too.**

---

### Step 4: Open the App

Open your web browser (Chrome, Edge, Firefox — any works) and go to:

```
http://localhost:5173
```

You should see the Parametric Insurance Engine dashboard.

---

## How to Use the Demo

Once the app is open in your browser, follow this sequence:

1. **Register a Partner** — Type any name (e.g. "Ramesh"), pick a zone, and click **Register Partner**
2. **Create a Policy** — Click **Run Risk Engine** — it will show the premium and risk level
3. **Check Weather** — Click **Check Rain Conditions** or **Check Heat Conditions** — results vary each time
4. **View Claims** — If a disruption was triggered, the claim will appear automatically in Step 4. You can also click **Refresh** to update.

---

## Troubleshooting

### "python is not recognized"
- You didn't add Python to PATH during installation
- Reinstall Python and make sure to check "Add Python to PATH"
- Alternatively, try using `python3` instead of `python`

### "npm is not recognized"
- Node.js is not installed or not added to PATH
- Reinstall Node.js from https://nodejs.org/

### Backend gives "Address already in use" error
- Something is already running on that port
- Try a different port: `uvicorn app:app --port 8090 --reload`
- If you change the port, you also need to update the frontend. Open `frontend/src/App.jsx` and change `http://localhost:8080` to `http://localhost:8090` on line 3

### Frontend shows blank page or errors
- Make sure the backend is running first
- Make sure you ran `npm install` before `npm run dev`
- Check the browser console (press F12) for error messages

### "Module not found" error in Python
- Make sure you activated the virtual environment (Step 2c)
- Make sure you installed dependencies (Step 2d)

---

## Quick Reference (After First Setup)

Once you've done the full setup once, next time you only need:

**Terminal 1 (Backend):**
```
cd backend
.\venv\Scripts\activate
uvicorn app:app --port 8080 --reload
```

**Terminal 2 (Frontend):**
```
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## Project Structure (For Reference)

```
GWDT/
├── backend/
│   ├── app.py                  ← Main API server
│   ├── database.py             ← SQLite database setup
│   ├── mock_data/
│   │   └── mock_services.py    ← Simulated weather/delivery APIs
│   └── services/
│       ├── risk_engine.py      ← Premium calculation logic
│       ├── trigger_engine.py   ← Weather trigger evaluation
│       └── claim_engine.py     ← Payout and fraud checks
├── frontend/
│   ├── src/
│   │   └── App.jsx             ← Main UI component
│   └── index.html
├── README.md
└── How_to_run.md               ← You are here
```
