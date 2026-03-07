# 17-Model Ensemble - Frontend Implementation Guide

## Updated Features

### 1. **Expanded Model Dropdown**
The model selection dropdown now includes all 17 models organized by category:

#### Categories:
- **Recommended**: Auto (system selects best model)
- **Simple Models**: MA, Weighted MA, Seasonal Naive
- **Statistical**: Holt's, Polynomial, Exp Smoothing, Theta, ARIMA, BSTS, Prophet, SARIMA
- **Machine Learning**: Vector AR, XGBoost, Random Forest, Gradient Boosting
- **Deep Learning**: LSTM, NeuralProphet

### 2. **Enhanced Info Cards**
The forecast summary now displays 6 info cards:
- **Data Points**: Number of historical data points
- **Model Used**: Selected forecasting model
- **Models Tested**: Count of eligible models backtested
- **Confidence**: Prediction confidence level
- **MAPE**: Mean Absolute Percentage Error
- **Trend**: Detected trend direction

### 3. **Model Selection Reasoning**
A new section explains why the selected model was chosen:
- Displays `model_reason` from backend
- Color-coded with purple accent
- Shows data-driven selection rationale

### 4. **Model Performance Comparison**
When multiple models are tested, displays:
- All tested models with their MAPE scores
- Models ranked by performance
- Best model marked with 🏆
- Selected model marked with ✓
- Interactive hover effects

### 5. **Updated API Types**
`lib/api.ts` now includes:

```typescript
// New model type supporting all 17 models
model: 'auto' | 'moving_average' | 'weighted_moving_average' | ... | 'neural_prophet'

// New ModelInfo interface
interface ModelInfo {
  description: string;
  mape: number;
  data_points_used: number;
  model_type?: string;
  key_features?: string[];
}

// Enhanced ForecastResponse
interface ForecastResponse {
  model_info?: ModelInfo;
  tested_models?: number;
  model_performance?: Record<string, number>;
  // ... existing fields
}
```

## Model Selection Behavior

### Automatic Selection (Auto mode)
1. System analyzes data length and characteristics
2. Filters to eligible models (based on minimum data points)
3. Backtests all eligible models
4. Selects best performer by MAPE
5. Returns detailed reasoning and comparison

### Manual Selection
Users can select specific models from dropdown:
- Auto validates model eligibility with data
- Shows error if insufficient data
- Provides fallback recommendations

## UI Enhancements

### Color Scheme
- **Purple (#8b5cf6)**: Model selection reasoning
- **Cyan (#06b6d4)**: Model comparison & selected model
- **Green (#22c55e)**: Best performing model

### Performance Indicators
- 🏆 Best model (lowest MAPE)
- ✓ Selected/current model
- 🎯 Model recommendation focus

## Example Backend Response

```json
{
  "model_used": "prophet",
  "tested_models": 12,
  "model_reason": "Strong seasonality detected - Prophet excels here; Sufficient data for seasonal decomposition; Low prediction error in backtesting",
  "model_performance": {
    "moving_average": 8.5,
    "exponential_smoothing": 7.2,
    "prophet": 5.1,
    "xgboost": 5.8,
    "seasonal_naive": 6.3
  },
  "model_info": {
    "description": "Prophet - excellent for seasonal patterns",
    "mape": 5.1,
    "data_points_used": 90
  },
  "confidence_level": "92",
  "metrics": {
    "mape": 5.1
  }
}
```

## User Flow

1. **Upload CSV** → Frontend receives 60+ data points
2. **Select Horizon** → Choose 7, 30, or 90 days
3. **Choose Model** → 
   - Select "Auto" for automatic selection
   - Or pick specific model from organized dropdown
4. **Generate Forecast**
5. **View Results**:
   - Info cards show data summary
   - Model selection reasoning displays
   - Performance comparison shows all tested models
   - Chart visualizes historical and forecasted values
   - AI explanation provides business insights

## Backward Compatibility

All changes are backward compatible:
- Existing endpoints work without changes
- Old response format still supported
- New fields are optional
- Graceful degradation if fields missing

## Dependencies

Frontend requires NO new dependencies:
- Uses existing React, Recharts, TypeScript
- No additional npm packages needed
- Works with current build setup

## Testing Checklist

- [ ] Model dropdown renders all 17 models
- [ ] Auto selection works with sufficient data
- [ ] Manual model selection works
- [ ] Info cards display correctly
- [ ] Model reasoning section shows text
- [ ] Performance comparison displays with 5+ models tested
- [ ] Best model indicator (🏆) shows correctly
- [ ] Selected model indicator (✓) highlights properly
- [ ] Responsive design works on mobile
- [ ] Hover effects work on model comparison cards

## Future Enhancements

1. **Model Details Popup** - Click model to see full specs
2. **Performance Charts** - Visualize MAPE comparison
3. **Model History** - Track which models performed best over time
4. **Custom Ensembles** - Let users combine multiple models
5. **Model Explanations** - Feature importance for ML models
