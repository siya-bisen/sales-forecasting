# Data Display Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Forecast Data Not Displaying in Chart
**Symptoms**: Chart is empty or shows no forecast line
**Root Cause**: Invalid forecast response or data format mismatch

**Solution Steps**:
1. Open browser DevTools → Network tab
2. Check the `/api/forecast` response
3. Verify forecast array has data:
```json
{
  "forecast": [
    {"date": "2024-03-15", "value": 1200, "lower": 1100, "upper": 1300},
    // ... more points
  ]
}
```
4. If empty, check:
   - Backend model is fitting correctly
   - Input data has valid sales values
   - Horizon > 0

**Quick Fix**: The ForecastChart now validates data automatically with:
```typescript
if (!result.forecast || result.forecast.length === 0) {
  throw new Error('Invalid forecast data received from server');
}
```

---

### Issue 2: Confidence Level Showing as "NaN%"
**Symptoms**: Confidence displays as "NaN%" in info card
**Root Cause**: Confidence value is undefined or in unexpected format

**Solution Steps**:
1. Check backend response includes `confidence_level`
2. Verify it's either a number (95) or string ("95%")
3. The frontend now handles both with:
```typescript
if (typeof result.confidence_level === 'string') {
  result.confidence_level = parseInt(result.confidence_level.replace('%', ''), 10);
}
```

**Debug Output**: Add to ForecastChart.tsx:
```typescript
console.log('Confidence Level:', forecastResult.confidence_level);
console.log('Confidence Parsed:', getConfidenceLevel(forecastResult.confidence_level));
```

---

### Issue 3: AI Explanation Section Shows Error or Blank
**Symptoms**: Explanation area is empty or shows parsing error
**Root Cause**: Explanation is malformed JSON or missing

**Solution Steps**:
1. Check network response for `explanation` field
2. It can be either:
   - String: `"{\\"analysis\\": \\"text\\"}"`
   - Object: `{"analysis": "text"}`
3. The parser now handles both:
```typescript
if (typeof forecastResult.explanation === 'string') {
  try {
    explanation = JSON.parse(forecastResult.explanation);
  } catch (e) {
    explanation = { analysis: forecastResult.explanation };
  }
}
```

**Fallback Behavior**: If parsing fails, displays the raw text as analysis

---

### Issue 4: Sales Context Not Showing
**Symptoms**: Business Context section is empty or shows "Enhance Your Forecast"
**Root Cause**: CSV data missing optional business columns

**Solution Steps**:
1. Upload CSV with only "Date" and "Sales" columns → Shows enhancement prompt
2. Add optional columns for more context:
   - ProductCategory
   - Region
   - CustomerSegment
   - MarketingSpend
   - IsPromotion
   - Quantity
   - UnitPrice

**Data Processing**:
```python
# Backend extracts context
context["product_category"] = ", ".join(sorted(categories))
context["regions"] = ", ".join(sorted(regions))
context["avg_marketing_spend"] = f"${avg_spend:.2f}"
# etc.
```

**Frontend Display**:
```typescript
const contextItems = extractSalesContext(forecastResult.sales_context);
// Only shows non-default values
```

---

### Issue 5: Volatility Not Displaying with Color/Icon
**Symptoms**: Volatility shows as plain text without visual indicator
**Root Cause**: Missing volatility classification utility call

**Solution Steps**:
1. Verify ForecastChart imports dataUtils:
```typescript
import { getVolatilityClassification } from '@/lib/dataUtils';
```

2. Check volatility is being classified:
```typescript
const volatility = getVolatilityClassification(forecastResult.summary.volatility);
// Returns: { text: 'Moderate', color: '#06b6d4', icon: '📊' }
```

3. Verify display uses the classification:
```tsx
<div style={{ color: volatility.color, fontSize: '1rem' }}>
  {volatility.icon} {volatility.text}
</div>
```

---

### Issue 6: Data Quality Notes Missing or Poorly Formatted
**Symptoms**: Notes section is empty or all notes are same color
**Root Cause**: Utility function not properly organizing notes by type

**Solution Steps**:
1. Verify notes are in response:
```json
{
  "notes": [
    "✓ Data has clear trend",
    "⚠️ High volatility detected",
    "✓ No missing values"
  ]
}
```

2. Check utility organizes by type:
```typescript
const { warnings, positives, neutral } = getDataQualitySummary(forecastResult.notes);
```

3. Verify different colors for each type:
   - ✓ Green (`#22c55e`)
   - ⚠️ Orange (`#f59e0b`)
   - Other Blue (`#06b6d4`)

---

### Issue 7: Model Comparison Panel Not Showing
**Symptoms**: Model Performance comparison section is missing
**Root Cause**: Backend not returning `model_performance` field

**Solution Steps**:
1. Check if `auto` model was selected
2. Only `auto` model returns `model_performance` with comparison
3. Manual model selection returns only the selected model

**Enable Comparison**:
- Use "⚡ Auto (Recommended)" model selection
- Backend will test multiple models and return their MAPE scores

**Example Response**:
```json
{
  "model_performance": {
    "arima": 8.5,
    "prophet": 7.2,
    "xgboost": 6.9
  }
}
```

---

### Issue 8: Forecast Values Showing Negative Numbers
**Symptoms**: Upper/lower bounds or forecast values are negative
**Root Cause**: Model returning invalid confidence intervals

**Solution Steps**:
1. Check backend models enforce non-negative values:
```python
forecast_values = [max(0, float(v)) for v in forecast_result["forecast"]]
lower_bounds = [max(0, float(v)) for v in lower_bounds]
```

2. Verify bounds are valid:
```python
lower = min(lower, forecast_values[i])
upper = max(upper, forecast_values[i])
```

3. If still negative, check:
   - Input data has no negative sales values
   - Model metadata is valid
   - Data normalization is correct

---

### Issue 9: Chart Not Rendering/Showing Blank
**Symptoms**: Chart area is empty, no line plot visible
**Root Cause**: Chart data format issue or data point mismatch

**Solution Steps**:
1. Open DevTools Console and add debugging:
```typescript
console.log('Chart Data:', chartData);
console.log('Forecast Result:', forecastResult);
```

2. Verify chart data structure:
```typescript
chartData = [
  { date: "2024-01-01", historical: 1000, forecast: null, lower: null, upper: null },
  { date: "2024-03-15", historical: null, forecast: 1200, lower: 1100, upper: 1300 },
  // ... more points
]
```

3. Check date format consistency:
```typescript
// Both historical and forecast dates must be "YYYY-MM-DD" format
```

4. Verify ResponsiveContainer height:
```tsx
<div style={{ height: '400px', width: '100%' }}>
  <ResponsiveContainer width="100%" height="100%">
    {/* Chart components */}
  </ResponsiveContainer>
</div>
```

---

### Issue 10: API Errors Not Displaying Properly
**Symptoms**: Generic error message or no error shown at all
**Root Cause**: Error message not propagating from backend

**Solution Steps**:
1. Check backend route error response:
```python
raise HTTPException(status_code=400, detail="Detailed error message")
```

2. Verify frontend error handling:
```typescript
const error = await response.json();
throw new Error(error.detail || error.message || 'Forecast generation failed');
```

3. Check ForecastChart error display:
```tsx
{error && (
  <div style={{ ... }}>
    ❌ {error}
  </div>
)}
```

4. View errors in DevTools Console for debugging

---

## Debugging Checklist

### Before Submitting Bug Report:
- [ ] Check browser console for JavaScript errors
- [ ] Check network tab for failed API requests
- [ ] Verify API response status is 200
- [ ] Check response body for data completeness
- [ ] Verify backend logs for model fitting errors
- [ ] Test with different model selection
- [ ] Try with different forecast horizons (7, 30, 90)
- [ ] Upload fresh test data CSV
- [ ] Clear browser cache and reload
- [ ] Test in incognito/private mode

### Useful Debug Commands (DevTools Console):

```javascript
// Check API response
fetch('http://localhost:8000/api/forecast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    data: [{date: '2024-01-01', sales: 1000}],
    horizon: 7,
    model: 'auto'
  })
}).then(r => r.json()).then(console.log);

// Check confidence parsing
const conf = parseInt('95%'.replace('%', ''), 10);
console.log('Parsed confidence:', conf); // Should be 95

// Check explanation parsing
const exp = JSON.parse('{"analysis":"text"}');
console.log('Parsed explanation:', exp);

// Check data utils
import { getConfidenceLevel } from '@/lib/dataUtils';
getConfidenceLevel('95%'); // Should return 95
```

---

## Performance Tips

1. **Large Datasets**: Backend automatically detects data size and uses appropriate models
2. **Long Horizons**: 90-day forecasts take slightly longer than 7-day
3. **Auto Model**: Tests multiple models, takes 2-3x longer than single model
4. **Caching**: Consider caching forecast results for same input data

---

## Getting Help

If issues persist:

1. **Check logs**:
   - Backend: `python -m uvicorn backend.main:app --reload`
   - Frontend: Browser DevTools (F12)

2. **Common Fixes**:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install` then restart dev server
   - Clear cache: Ctrl+Shift+Delete (Chrome) or Cmd+Shift+Delete (Mac)

3. **Test Endpoints Directly**:
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"data":[{"date":"2024-01-01","sales":1000}],"horizon":7,"model":"auto"}'
```

4. **Review Integration Documentation**:
   - See FRONTEND_BACKEND_INTEGRATION_COMPLETE.md
   - Check MODELS_IMPROVEMENTS_COMPLETE.md for model details
