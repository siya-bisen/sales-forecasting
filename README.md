# Sales Forecasting Copilot MVP

A clean, explainable, multi-model forecasting MVP that predicts future sales and explains why using AI.

## Features

- 🔐 **Firebase Authentication** - Email/password authentication
- 📊 **Multiple Forecasting Models** - Moving Average, Prophet, SARIMA
- 🤖 **Auto Model Selection** - Automatically selects the best model based on data characteristics
- 💡 **AI Explanations** - Gemini-powered explanations of forecasts
- 📈 **Interactive Charts** - Visualize historical data and forecasts with confidence intervals
- 📁 **CSV Upload** - Easy data import with validation

## Tech Stack

### Backend
- FastAPI (Python)
- Prophet, SARIMA, Moving Average models
- Google Gemini API for explanations

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Firebase Authentication & Firestore
- Recharts for visualization

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase project
- (Optional) Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional)
```

5. Run the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp env.example .env.local
# Edit .env.local with your Firebase configuration
```

4. Configure Firebase:
   - Create a Firebase project at https://console.firebase.google.com
   - Enable Email/Password authentication
   - Create a Firestore database
   - Copy your Firebase config to `.env.local`

5. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage

1. **Sign Up/Login**: Create an account or sign in with existing credentials
2. **Upload Data**: Upload a CSV file with `date,sales` format (see `example_data.csv`)
3. **Generate Forecast**: 
   - Select forecast horizon (7, 30, or 90 days)
   - Choose a model (Auto recommended)
   - Click "Generate Forecast"
4. **View Results**: 
   - See forecast chart with confidence intervals
   - View model metrics and confidence level
   - Click "Explain Forecast" for AI-powered explanation

## CSV Format

The CSV file should have the following format:

```csv
date,sales
2024-01-01,120
2024-01-02,135
...
```

- `date`: Date in YYYY-MM-DD format
- `sales`: Numeric sales value (must be >= 0)

## API Endpoints

### POST `/api/forecast`

Generate a sales forecast.

**Request:**
```json
{
  "data": [
    {"date": "2024-01-01", "sales": 120},
    {"date": "2024-01-02", "sales": 135}
  ],
  "horizon": 30,
  "model": "auto"
}
```

**Response:**
```json
{
  "model_used": "prophet",
  "model_reason": "Strong weekly seasonality detected",
  "confidence_level": "medium",
  "metrics": {
    "mape": 8.2
  },
  "forecast": [
    {
      "date": "2025-03-01",
      "value": 145,
      "lower": 130,
      "upper": 160
    }
  ],
  "summary": {
    "trend": "upward",
    "seasonality": "weekly",
    "volatility": "moderate"
  }
}
```

### POST `/api/explain`

Get AI explanation of a forecast.

**Request:**
```json
{
  "forecast_result": { /* forecast response */ },
  "user_question": "Why was this model chosen?"
}
```

**Response:**
```json
{
  "explanation": "The forecast shows an upward trend with weekly seasonality..."
}
```

## Project Structure

```
.
├── backend/
│   ├── models/          # Forecasting models
│   ├── services/        # Business logic
│   ├── routes/          # API endpoints
│   └── main.py         # FastAPI app
├── frontend/
│   ├── app/            # Next.js pages
│   ├── components/     # React components
│   └── lib/            # Utilities
├── example_data.csv    # Sample data
└── README.md
```

## Model Selection Logic

When "auto" is selected, the system:

1. Analyzes data characteristics (length, volatility, seasonality)
2. Backtests available models on recent historical data
3. Selects the model with lowest MAPE (Mean Absolute Percentage Error)
4. Provides reasoning for the selection

## Notes

- The app works without Gemini API key, but explanations will be rule-based
- Minimum 2 data points required for forecasting
- More data points generally lead to better forecasts
- Prophet requires at least 14 data points
- SARIMA requires at least 30 data points

## License

MIT
