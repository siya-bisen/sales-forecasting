# Sales Context Integration Guide

## Overview

The Sales Forecast System now supports **rich business context** from your CSV data. By including optional columns beyond the basic date and sales, you enable the AI engine to provide deeper insights into your sales patterns.

## How It Works

### Frontend (CSVUpload Component)
1. Parses your CSV file
2. Extracts all available columns (not just date and sales)
3. Sends complete data to the backend as `ForecastDataPoint` objects

### Backend (Forecasting Service)
1. Receives the full data payload
2. Calls `_extract_sales_context()` to analyze optional columns
3. Populates `sales_context` dictionary with:
   - Product categories
   - Regions
   - Customer segments
   - Average marketing spend
   - Promotion impact analysis
   - Average quantity and unit price

### Frontend Display (ForecastChart Component)
1. **If context data exists**: Displays as attractive cards with key metrics
2. **If context is missing**: Shows a helpful guide suggesting which columns to add

## Supported Optional Columns

| Column | Type | Purpose | Example |
|--------|------|---------|---------|
| ProductCategory | text | Product type categorization | "Electronics", "Software", "Hardware" |
| Region | text | Geographic location | "North America", "Europe", "Asia" |
| CustomerSegment | text | Customer classification | "Enterprise", "SMB", "Startup" |
| MarketingSpend | number | Marketing budget allocation | 5000, 3000 |
| IsPromotion | 0/1 | Promotion flag | 1 (active), 0 (inactive) |
| Quantity | number | Units sold | 150, 200, 250 |
| UnitPrice | number | Price per unit | 8.00, 9.50 |

## Example CSV Format

### Minimal (Basic Forecasting)
```csv
date,sales
2024-01-01,1200
2024-01-02,1350
2024-01-03,1100
```

### Enhanced (AI-Powered Insights)
```csv
date,sales,ProductCategory,Region,CustomerSegment,MarketingSpend,IsPromotion,Quantity,UnitPrice
2024-01-01,1200,Electronics,North America,Enterprise,5000,0,150,8.00
2024-01-02,1350,Electronics,North America,SMB,3000,1,180,7.50
2024-01-03,1100,Software,Europe,Enterprise,4000,0,120,9.00
2024-01-04,1500,Software,Asia,SMB,2500,1,200,7.50
```

## Benefits of Adding Context Columns

When you include optional columns, the AI engine automatically:

### 📊 Product Mix Analysis
- Identifies which product categories drive sales
- Detects performance differences between product types
- Helps forecast category-specific trends

### 🌍 Regional Insights
- Discovers regional sales variations
- Identifies geographic growth opportunities
- Enables region-specific recommendations

### 👥 Customer Segmentation
- Analyzes behavior differences across customer types
- Identifies high-value segments
- Provides segment-specific forecasts

### 💰 Marketing Analytics
- Calculates marketing ROI
- Measures spend effectiveness
- Suggests optimal budget allocation

### 🎉 Promotion Impact
- Quantifies promotion effectiveness
- Measures lift in sales from promotions
- Guides future promotion strategy

### 📦 Volume & Pricing
- Analyzes quantity trends
- Evaluates pricing strategy
- Identifies volume-price relationships

## Implementation Details

### Frontend Changes
The `CSVUpload` component now:
```typescript
// Extracts all columns from CSV
contextFields.forEach(field => {
  const value = row[field];
  if (value !== undefined && value !== null && value !== '') {
    dataPoint[field] = isNaN(parseFloat(value)) ? value : parseFloat(value);
  }
});
```

### Backend Changes
The `_extract_sales_context()` function:
1. Checks for presence of each optional column
2. Parses values (numeric or text)
3. Calculates aggregations (averages, sums)
4. Analyzes relationships (promotion impact = promo_sales vs non_promo_sales)
5. Returns formatted context dictionary

### Display Enhancement
The `ForecastChart` component:
- Shows context cards when data is present
- Displays helpful onboarding message when context is missing
- Suggests specific columns to add for better insights

## Testing the Feature

### Test Case 1: Minimal Data
1. Upload CSV with only date and sales
2. Observe: "No business context available" message
3. See suggested columns to add

### Test Case 2: Partial Context
1. Upload CSV with date, sales, and ProductCategory
2. Observe: Context card shows product categories
3. Other fields show "Not specified" or "Not analyzed"

### Test Case 3: Full Context
1. Upload the example CSV with all columns
2. Observe: Multiple context cards with detailed insights
3. See Gemini AI analyze all context dimensions

## File Structure

- **Frontend**: `frontend/components/CSVUpload.tsx` - CSV parsing with context extraction
- **Frontend**: `frontend/components/ForecastChart.tsx` - Context display and onboarding
- **Backend**: `backend/services/forecasting.py` - `_extract_sales_context()` function
- **Backend**: `backend/routes/forecast.py` - Response building with sales_context
- **Example**: `example_data_with_context.csv` - Sample CSV with all optional columns
- **Guide**: `DATA_FORMAT_GUIDE.md` - User-facing documentation

## Next Steps

1. **User Communication**: Share the `DATA_FORMAT_GUIDE.md` with users
2. **CSV Templates**: Provide `example_data_with_context.csv` as a download
3. **Onboarding**: Use the in-UI messages to guide first-time users
4. **Analytics**: Track which columns users include to optimize recommendations

## Troubleshooting

### Context Cards Show "Not specified"
- The column exists in your CSV but contains empty or null values
- Fill in the values for that column in all rows

### Context Cards Not Appearing at All
- Your CSV only has date and sales columns
- Add at least one optional column from the supported list
- Ensure column names match exactly (case-sensitive)

### Promotion Impact Not Calculated
- Your CSV must have an `IsPromotion` column with values of 0 or 1
- Also ensure you have a `sales` column for comparison
- Need at least some rows with IsPromotion=1 and some with IsPromotion=0

### Marketing Spend Showing Incorrectly
- Ensure `MarketingSpend` contains numeric values
- Remove currency symbols ($) - use plain numbers
- Decimal values are supported (e.g., 5000.50)
