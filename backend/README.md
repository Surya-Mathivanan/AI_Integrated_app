# Career Prep AI - Backend (Flask)

Now using Firebase Firestore (via firebase-admin) instead of MongoDB.

## Setup

1. Python env

```
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
```

2. Environment

- `FIREBASE_PROJECT_ID` (required)
- `GOOGLE_APPLICATION_CREDENTIALS` (recommended) path to your Firebase service account JSON (or use Application Default Credentials).
- `JWT_SECRET` (any string; internal use)
- `GEMINI_API_KEY` (optional)
- `MODEL_NAME` (optional; default gemini-1.5-flash)

3. Run

```
python -m backend.app
```

Health: GET /health → shows firebaseEnabled and geminiEnabled.
