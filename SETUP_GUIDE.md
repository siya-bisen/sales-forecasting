# 🚀 SalesForecast Pro - Setup & Running Guide

## 🎯 What's New

### ✨ Frontend Enhancements
- **Landing Page**: Beautiful animated homepage with features, pricing, and CTAs
- **Dark/Light Mode**: Full theme support with smooth transitions
- **Enhanced Animations**: Smooth transitions using Framer Motion
- **Sales Color Scheme**: Green (growth), Blue (insights), Purple (AI features)
- **Responsive Design**: Optimized for mobile, tablet, and desktop
- **Gemini Analysis**: Prominent AI explanation section with source attribution

### 🔧 Backend Improvements
- Fixed Gemini API integration (updated model to `gemini-1.5-flash`)
- Proper response handling with `resolve()` for async API
- Added safety settings for content generation
- Explanation engine properly initialized on startup

---

## 📦 Installation Steps

### 1️⃣ Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Check your .env file has GEMINI_API_KEY (optional but recommended)
# cat .env
# Should show: GEMINI_API_KEY=your-key-here
```

### 2️⃣ Frontend Setup (IMPORTANT)

```bash
cd frontend

# Install new dependencies
npm install

# This will install:
# - framer-motion: For animations
# - next-themes: For dark/light mode
# Plus all other dependencies
```

### 3️⃣ Start the Backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ Backend is ready at: `http://localhost:8000`

### 4️⃣ Start the Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.1.6
- Local:        http://localhost:3000
- Environments: .env.local
```

✅ Frontend is ready at: `http://localhost:3000`

---

## 🌐 Accessing the App

### Landing Page
Visit: **http://localhost:3000**

Features:
- Beautiful hero section with gradient
- Feature cards
- Pricing plans
- Theme toggle (top right)
- Sign In / Create Account buttons

### Login Page
- Custom designed with gradient
- Email/Password authentication
- Sign up option
- Dark mode support

### Dashboard
- Upload CSV data
- Generate forecasts with 3 model choices
- Beautiful forecast visualization
- **🤖 AI Analysis Section** - Prominently shows:
  - Gemini explanation (if available)
  - Rule-based fallback explanation
  - Source attribution badge

---

## 🎨 Design Features

### Color Scheme
- **Green (#10b981)**: Growth, positive trends, CTA buttons
- **Blue (#3b82f6)**: Analytics, insights, information
- **Purple (#9333ea)**: AI/Gemini features
- **Dark Mode**: Slate colors (#0f172a to #334155)

### Animations
- Fade-in transitions on page load
- Hover effects on cards
- Floating animations on hero section
- Loading spinners
- Smooth theme transitions

---

## 🤖 Gemini AI Integration

### Setup (Optional but Recommended)

1. **Get API Key**:
   - Visit: https://ai.google.dev
   - Click "Get API Key"
   - Create new key
   - Copy the key

2. **Add to Backend**:
   ```bash
   cd backend
   # Edit .env file
   echo "GEMINI_API_KEY=your-api-key-here" >> .env
   ```

3. **Verify It Works**:
   - Generate a forecast
   - Check if explanation shows "✨ AI-Generated" badge
   - If not, it's using rule-based (still works great!)

### What You'll See

**With Gemini (AI-Generated):**
- Purple gradient background box
- Natural language explanation
- Badge shows "✨ AI-Generated (Gemini)"

**Without Gemini (Rule-Based):**
- Amber gradient background box
- Structured explanation from logic
- Badge shows "📋 Rule-Based"

Both are high-quality and informative!

---

## 📊 Example Workflow

1. **Visit http://localhost:3000**
   - See beautiful landing page
   - Toggle dark mode with 🌙 button

2. **Sign In or Create Account**
   - Use any email/password
   - Firebase handles authentication

3. **Upload Data**
   - Drag and drop CSV or click to select
   - Use `example_data.csv` from project root

4. **Generate Forecast**
   - Select horizon (7, 30, or 90 days)
   - Choose model (Auto recommended)
   - Click "Generate Forecast"

5. **View Results**
   - See beautiful chart with confidence intervals
   - 5 info cards: Data Points, Model, Confidence, MAPE, Trend
   - **🤖 Scroll down for AI Analysis**
   - Source badge shows if Gemini or rule-based

---

## 🐛 Troubleshooting

### Issue: npm install fails

```bash
# Clear cache and retry
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Cannot find module 'framer-motion'"

```bash
# Make sure npm install completed
npm install
npm install framer-motion next-themes
```

### Issue: Dark mode not working

- Make sure browser supports `<html class="dark">`
- Clear browser cache
- Restart dev server

### Issue: Gemini explanation shows "Rule-Based"

- Check if GEMINI_API_KEY is set: `echo $GEMINI_API_KEY`
- Restart backend after setting key
- Check for errors in backend terminal

### Issue: Forecast generation fails

- Ensure at least 2 data points
- Check backend is running on port 8000
- Check API URL in `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── login/page.tsx        # Login route
│   ├── dashboard/page.tsx    # Dashboard route
│   └── globals.css           # Global styles + animations
├── components/
│   ├── LandingPage.tsx       # NEW: Hero + Features + Pricing
│   ├── LoginPage.tsx         # ENHANCED: Dark mode
│   ├── Dashboard.tsx         # ENHANCED: Dark mode, animations
│   ├── ForecastChart.tsx     # ENHANCED: Gemini prominence
│   └── CSVUpload.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── firebase.ts          # Firebase config
│   └── firestore.ts         # Firestore utilities
└── package.json             # UPDATED: framer-motion, next-themes

backend/
├── main.py                  # FastAPI app
├── routes/
│   ├── forecast.py         # FIXED: Uses forecasting module
│   └── explain.py          # FIXED: Uses gemini-1.5-flash
├── services/
│   ├── gemini_client.py    # FIXED: Model + response handling
│   ├── explanation_engine.py
│   ├── forecasting.py      # FIXED: Global engine initialized
│   ├── model_selector.py
│   ├── model_eligibility.py
│   ├── data_validation.py
│   ├── preprocessing.py
│   └── evaluation.py
├── models/
│   ├── moving_average.py
│   ├── prophet_model.py
│   └── sarima_model.py
└── .env                    # GEMINI_API_KEY here

```

---

## 🎓 Key Files Changed

### Frontend
- `frontend/package.json` - Added framer-motion, next-themes
- `frontend/app/layout.tsx` - Added ThemeProvider
- `frontend/app/globals.css` - Enhanced animations + dark mode
- `frontend/app/page.tsx` - Now shows landing page
- `frontend/app/login/page.tsx` - NEW route
- `frontend/components/LandingPage.tsx` - NEW component
- `frontend/components/LoginPage.tsx` - Enhanced styling
- `frontend/components/Dashboard.tsx` - Enhanced with animations
- `frontend/components/ForecastChart.tsx` - Prominent Gemini section

### Backend
- `backend/services/gemini_client.py` - Fixed model + response handling
- `backend/routes/explain.py` - Fixed response handling
- `backend/routes/forecast.py` - Fixed engine initialization

---

## ✅ Verification Checklist

After starting both servers:

- [ ] Landing page loads at http://localhost:3000
- [ ] Dark/light mode toggle works (🌙 button)
- [ ] Can sign in/create account
- [ ] Can upload CSV file
- [ ] Can generate forecast
- [ ] Sees chart with forecast
- [ ] Sees "AI Analysis" section
- [ ] Sees explanation with source badge
- [ ] Backend shows no errors in terminal

---

## 🚀 Performance Tips

- Use **Auto** model selection for best results
- Start with **30 days** forecast horizon
- Upload CSV with consistent date format (YYYY-MM-DD)
- In dark mode, colors adjust automatically for readability

---

## 📞 Support

If issues arise:

1. Check terminal output for error messages
2. Verify all dependencies installed: `npm list` (frontend), `pip list` (backend)
3. Ensure ports 3000 and 8000 are available
4. Restart servers if making changes to code
5. Clear browser cache if theme not updating

---

**Happy Forecasting! 📊✨**
