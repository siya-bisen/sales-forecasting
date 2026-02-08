# Gemini API Integration & Enhanced Validation

## Summary of Changes

This enhancement integrates Gemini API for AI-powered forecast explanations while maintaining graceful fallback to rule-based explanations. The system also enforces strict data validation and model eligibility rules.

## Files Added

### Backend Services

1. **`backend/services/data_validation.py`**
   - Validates minimum data points (2+ required)
   - Provides data quality notes for API responses
   - Raises `DataValidationError` for invalid data

2. **`backend/services/model_eligibility.py`**
   - Enforces model-specific data requirements:
     - **Moving Average**: ≥ 2 data points
     - **Prophet**: ≥ 14 data points
     - **SARIMA**: ≥ 30 data points
   - Filters ineligible models during auto-selection
   - Provides validation for manual model selection
   - Returns `ModelIneligibilityError` with helpful suggestions

3. **`backend/services/gemini_client.py`**
   - Wraps Google Generative AI API
   - Handles initialization with API key from `GEMINI_API_KEY` environment variable
   - Graceful degradation if API key is missing or API fails
   - Builds structured prompts (no raw numbers, only metadata)
   - Never throws unhandled exceptions

4. **`backend/services/explanation_engine.py`**
   - Orchestrates Gemini and rule-based explanations
   - Returns `(explanation_text, source)` tuple
   - Falls back to deterministic rule-based explanations automatically
   - Generates explanations based on:
     - Model used (Prophet, SARIMA, Moving Average)
     - Trend (upward, downward, stable)
     - Seasonality patterns
     - Volatility levels
     - Confidence level
     - Data points available

## Files Modified

### Backend Routes

**`backend/routes/forecast.py`**
- Enhanced `ForecastResponse` schema:
  - Added `data_points`: Number of historical data points
  - Added `explanation`: AI or rule-based explanation text
  - Added `explanation_source`: "gemini" or "rule-based"
  - Added `notes`: List of data quality notes
  - Added `model_reason`: Why the model was selected
- Added data validation before forecasting
- Added model eligibility validation for manual selections
- Integrated explanation engine
- Clear error messages for validation failures

### Backend Services

**`backend/services/forecasting.py`**
- Added imports for new validation services
- Added global `_explanation_engine` instance
- Added `initialize_explanation_engine()` function for startup
- Updated `generate_forecast()` to work with new pipeline

**`backend/services/model_selector.py`**
- Integrated model eligibility filtering
- Filters models based on data length before backtesting
- Explains why ineligible models were excluded
- Returns "Only one model met the minimum data requirements" when appropriate

**`backend/main.py`**
- Added startup event handler
- Initializes explanation engine with Gemini API key
- Maintains backward compatibility with explain route

### Frontend

**`frontend/lib/api.ts`**
- Updated `ForecastResponse` interface:
  - Added `data_points`
  - Added `explanation`
  - Added `explanation_source`
  - Added `notes`

**`frontend/components/ForecastChart.tsx`**
- Displays explanation automatically after forecast generation
- Shows explanation source badge ("AI-generated (Gemini)" or "Rule-based")
- Displays data quality notes
- Shows data points count in forecast info cards
- Removed separate "Explain Forecast" button (explanation included in forecast)

## How Gemini Fallback Works

### Scenario 1: Gemini API Key Available and Valid
1. Forecast is generated
2. Structured metadata (no raw time series) is prepared
3. Gemini receives metadata including:
   - Model used
   - Model selection reason
   - Data points count
   - Confidence level
   - Trend, seasonality, volatility
4. Gemini returns natural language explanation
5. Response includes `"explanation_source": "gemini"`

### Scenario 2: Gemini API Key Missing
1. Environment variable `GEMINI_API_KEY` is not set
2. `GeminiClient` initializes without active API connection
3. Explanation engine detects unavailable Gemini
4. Falls back to deterministic rule-based explanation
5. Response includes `"explanation_source": "rule-based"`

### Scenario 3: Gemini API Call Fails
1. API key is present and configured
2. Gemini request fails (network error, quota exceeded, etc.)
3. `GeminiClient.generate_explanation()` catches exception and returns `None`
4. Explanation engine detects `None` and falls back to rules
5. Response includes `"explanation_source": "rule-based"`

### Scenario 4: Insufficient Data
1. Fewer than 2 data points provided
2. Request is rejected with 400 status code
3. Error message: "At least 2 data points are required to generate a forecast."

### Scenario 5: Ineligible Model Selected
1. User selects Prophet with 10 data points (requires 14+)
2. Request is rejected with 400 status code
3. Error message: Includes minimum requirement and suggestion

## Validation Rules

### Global Rules
- **Minimum 2 data points** required for any forecast
- Always include "More historical data generally leads to more accurate forecasts" in notes

### Moving Average
- ✅ Works with ≥ 2 data points
- Always eligible (baseline option)

### Prophet
- ✅ Works with ≥ 14 data points
- ❌ Rejected with < 14 points
- Suggestion offered: "Consider using Moving Average"

### SARIMA
- ✅ Works with ≥ 30 data points
- ❌ Rejected with < 30 points
- Suggestion offered: "Consider using Prophet (14+ points) or Moving Average (2+ points)"

## API Response Example (with Gemini)

```json
{
  "data_points": 28,
  "model_used": "prophet",
  "model_reason": "Strong seasonality detected; Sufficient historical data",
  "confidence_level": "medium",
  "metrics": {"mape": 8.5},
  "forecast": [...],
  "summary": {"trend": "upward", "seasonality": "weekly", "volatility": "moderate"},
  "explanation": "Prophet was selected because it excels at handling seasonal patterns and trends. The forecast indicates an upward trend in sales. Weekly seasonality patterns were detected in your historical data. Confidence is moderate - the forecast should be used as guidance alongside other business factors.",
  "explanation_source": "gemini",
  "notes": [
    "More historical data generally leads to more accurate forecasts."
  ]
}
```

## API Response Example (Rule-based Fallback)

```json
{
  "data_points": 8,
  "model_used": "moving_average",
  "model_reason": "Only one model met the minimum data requirements.",
  "confidence_level": "medium",
  "metrics": {"mape": 12.0},
  "forecast": [...],
  "summary": {"trend": "stable", "seasonality": "none", "volatility": "moderate"},
  "explanation": "Moving Average was selected, providing a stable and straightforward baseline forecast. The forecast suggests relatively stable sales with minimal trend. Confidence is moderate - the forecast should be used as guidance alongside other business factors. With 8 data points, more historical data would improve accuracy.",
  "explanation_source": "rule-based",
  "notes": [
    "More historical data generally leads to more accurate forecasts."
  ]
}
```

## Environment Configuration

### Required
- No new required environment variables (backward compatible)

### Optional
- `GEMINI_API_KEY`: Google Generative AI API key for Gemini explanations
  - If not set: automatically uses rule-based explanations
  - If invalid: automatically falls back to rule-based explanations

### Frontend Environment (if needed)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Installation

No additional setup needed. Dependencies are already in `requirements.txt`:
- `google-generativeai==0.7.0` (updated from 0.3.1 for better API support)

## Testing the Enhancement

### Test 1: Forecast with Gemini (if key available)
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"date": "2024-01-01", "sales": 100},
      {"date": "2024-01-02", "sales": 110},
      {"date": "2024-01-03", "sales": 105}
    ],
    "horizon": 7,
    "model": "auto"
  }'
# Should return explanation_source: "gemini" (if API key set)
```

### Test 2: Forecast without sufficient data
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"date": "2024-01-01", "sales": 100}],
    "horizon": 7,
    "model": "auto"
  }'
# Should return 400 error: "At least 2 data points are required..."
```

### Test 3: Try SARIMA with insufficient data
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"date": "2024-01-01", "sales": 100},
      ...15 more points...
    ],
    "horizon": 7,
    "model": "sarima"
  }'
# Should return 400 error with minimum requirement and suggestion
```

## Key Design Decisions

1. **Explanation included in forecast response**: No separate API call needed for explanations. This reduces latency and ensures consistency.

2. **Structured metadata only to Gemini**: Never sends raw time-series data to Gemini. This is safer and follows data minimization principles.

3. **Deterministic rule-based fallback**: Rules are consistent and don't depend on external APIs, ensuring reliability.

4. **Graceful degradation**: Missing or failing Gemini never breaks the API - it automatically falls back.

5. **Clear source attribution**: Frontend can distinguish between AI and rule-based explanations for user transparency.

6. **Model eligibility enforcement at service level**: Prevents ineligible models from even being backtested, saving resources.

## Future Enhancements

- Add caching for Gemini responses (same metadata = same explanation)
- Add user preference for explanation style (concise vs. detailed)
- Track explanation source usage metrics
- Allow custom rule-based explanation templates
