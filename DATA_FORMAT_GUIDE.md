# Sales Forecast System - Data Format Guide

## Basic Format (Minimum Required)

Your CSV file must contain at least these two columns:
- **date**: The date in YYYY-MM-DD format (e.g., 2024-01-01)
- **sales**: The sales amount as a number (e.g., 1200)

Example:
```
date,sales
2024-01-01,1200
2024-01-02,1350
2024-01-03,1100
```

## Enhanced Format (Recommended for Richer Context)

For deeper business insights, add these optional columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| ProductCategory | text | Type of product sold | "Electronics", "Software", "Hardware" |
| Region | text | Geographic region | "North America", "Europe", "Asia" |
| CustomerSegment | text | Customer type | "Enterprise", "SMB", "Startup" |
| MarketingSpend | number | Marketing investment (in dollars) | 5000, 3000 |
| IsPromotion | 0 or 1 | Whether a promotion was active | 1 (yes), 0 (no) |
| Quantity | number | Units sold | 150, 200 |
| UnitPrice | number | Price per unit (in dollars) | 8.00, 9.50 |

## Example with Full Context

```
date,sales,ProductCategory,Region,CustomerSegment,MarketingSpend,IsPromotion,Quantity,UnitPrice
2024-01-01,1200,Electronics,North America,Enterprise,5000,0,150,8.00
2024-01-02,1350,Electronics,North America,SMB,3000,1,180,7.50
2024-01-03,1100,Software,Europe,Enterprise,4000,0,120,9.00
2024-01-04,1500,Software,Asia,SMB,2500,1,200,7.50
```

## How Richer Context Enhances Forecasting

When you provide optional columns, the AI engine automatically:
- **Analyzes Product Mix**: Identifies top-performing product categories
- **Regional Insights**: Detects regional sales patterns
- **Customer Segmentation**: Understands different customer behavior patterns
- **Marketing Impact**: Calculates ROI and effectiveness of marketing spend
- **Promotion Effects**: Measures how promotions impact sales
- **Pricing Analysis**: Evaluates pricing strategy effectiveness

## Notes

- All dates must be unique (no duplicate dates)
- Sales values must be non-negative numbers
- Use consistent column naming (case-sensitive matching for optional fields)
- At least 2 data points required for forecasting
- More historical data (30+ points) leads to more accurate forecasts
