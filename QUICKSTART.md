# Quick Start Guide

## 1. Backend Setup (5 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend will run on `http://localhost:8000`

## 2. Frontend Setup (5 minutes)

```bash
cd frontend
npm install
cp env.example .env.local
# Edit .env.local with your Firebase config
npm run dev
```

Frontend will run on `http://localhost:3000`

## 3. Firebase Setup

1. Go to https://console.firebase.google.com
2. Create a new project
3. Enable Authentication → Email/Password
4. Create Firestore database (start in test mode)
5. Copy config to `frontend/.env.local`

## 4. (Optional) Gemini API Key

1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## 5. Test It!

1. Open http://localhost:3000
2. Sign up with email/password
3. Upload `example_data.csv`
4. Generate a forecast
5. Click "Explain Forecast"

That's it! 🚀
