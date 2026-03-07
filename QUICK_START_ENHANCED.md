# Quick Start Guide - Enhanced Sales Forecasting

## 🚀 Getting Started with the New Features

### Prerequisites
- Backend running on `localhost:8000`
- Frontend running on `localhost:3000`
- Gemini API key configured (optional, uses fallback if not set)

### Step 1: Use Enhanced Dataset

The simplest way to test is using the new `sales_data_enhanced.csv`:

```bash
# Navigate to project root
cd c:\Projects\sales-forecast

# View the enhanced dataset
cat sales_data_enhanced.csv | head -20
```

**File Contents:**
- 40 rows of sample data (Jan-Feb 2010)
- 11 columns including Date, Sales, Product Category, Region, etc.
- Realistic business metrics

### Step 2: Upload & Forecast

#### Frontend:
1. Open http://localhost:3000
2. Click "Upload CSV"
3. Select `sales_data_enhanced.csv`
4. Select forecast horizon (7, 30, or 90 days)
5. Choose model (auto recommended)
6. Click "Generate Forecast"

#### What You'll See:

**Chart Section:**
- Historical sales line (cyan)
- Forecast line (purple)
- Confidence intervals (dashed lines)

**AI Analysis Section:**
```
🤖 AI Analysis with Gemini
[AI-generated explanation mentioning specific product categories,
 regions, seasonal patterns, and business insights]

✓ Powered by Google Gemini AI
```

**NEW - Sales Business Context Panel:**
```
📊 Sales Business Context
- Product Categories: Electronics, Apparel, Home
- Geographic Regions: North America, Europe, APAC  
- Customer Segments: Enterprise, SMB, Consumer
- Avg Marketing Spend: $2,140.50
- Promotion Impact: Promotions increase sales by ~18.3%
- Avg Quantity: 20.5 units
- Avg Unit Price: $2.92
```

### Step 3: Create Your Own Dataset

To use your own sales data with enhanced features:

```csv
Date,Sales,ProductCategory,Region,Quantity,UnitPrice,CustomerSegment,MarketingSpend,IsPromotion,WebsiteTraffic,ConversionRate
2024-01-01,5000,Electronics,North America,25,200,Enterprise,1500,0,8500,2.1
2024-01-02,5200,Electronics,North America,26,200,Enterprise,1500,1,8700,2.3
2024-01-03,4800,Apparel,Europe,20,240,SMB,1200,0,7200,1.9
...
```

**Required Columns:**
- `Date` (YYYY-MM-DD format)
- `Sales` (numeric)

**Optional Columns (for enhanced analysis):**
- `ProductCategory` - Product type/line
- `Region` - Geographic region
- `Quantity` - Units sold
- `UnitPrice` - Price per unit
- `CustomerSegment` - Customer type
- `MarketingSpend` - Advertising budget
- `IsPromotion` - 0 or 1 flag
- `WebsiteTraffic` - Site visitors
- `ConversionRate` - Conversion percentage
- Any other business metrics!

### Step 4: Interpret the Sales Context

The new Sales Context Panel shows:

| Field | Meaning | Business Use |
|-------|---------|--------------|
| **Product Categories** | Which product lines were sold | Understand product mix impact on forecast |
| **Regions** | Geographic breakdown | Plan regional inventory and distribution |
| **Customer Segments** | Type of customers | Adjust strategy by segment (B2B vs B2C) |
| **Avg Marketing Spend** | Average ad budget | Correlate spend with forecast trends |
| **Promotion Impact** | Effect of promotions | Plan future promotion strategies |
| **Avg Quantity** | Units per transaction | Manage inventory levels |
| **Avg Unit Price** | Average product price | Understand revenue per transaction |

### Step 5: Interpret the AI Explanation

The Gemini-powered explanation now includes:

**What It Explains:**
- ✅ Which model was selected and WHY
- ✅ Trend direction (upward/downward/stable)
- ✅ Seasonality patterns (weekly/monthly/yearly)
- ✅ Confidence level and what affects it
- ✅ **NEW:** Specific product category insights
- ✅ **NEW:** Regional variation patterns
- ✅ **NEW:** Promotion effectiveness
- ✅ **NEW:** Inventory and resource planning advice
- ✅ **NEW:** Marketing ROI implications

**Example Explanation:**
```
Prophet was selected because it excels at handling seasonal patterns
and trends in sales data. Specifically: Strong weekly seasonality 
detected with product category variation. Forecast indicates an upward
trend in sales, suggesting revenue growth. Weekly seasonality patterns
are present - prepare for cyclical demand fluctuations. Business Context:
Product categories in analysis: Electronics, Apparel, Home; Geographic
regions: North America, Europe, APAC; Customer segments: Enterprise,
SMB, Consumer. Promotion impact noted: Promotions increase sales by 18.3%.
Confidence is high - enabling reliable sales planning and resource
allocation.
```

### Step 6: Use the API Directly

#### Generate Forecast:
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"date": "2024-01-01", "sales": 5000, "ProductCategory": "Electronics", "Region": "North America"},
      {"date": "2024-01-02", "sales": 5200, "ProductCategory": "Electronics", "Region": "North America"}
    ],
    "horizon": 30,
    "model": "auto"
  }'
```

#### Response Includes:
```json
{
  "data_points": 2,
  "model_used": "prophet",
  "confidence_level": "high",
  "explanation": "...",
  "sales_context": {
    "product_category": "Electronics",
    "regions": "North America",
    "customer_segments": "All",
    "avg_marketing_spend": "Not specified",
    "promotion_impact": "Not analyzed",
    "avg_quantity": "N/A",
    "avg_unit_price": "N/A"
  }
}
```

### Troubleshooting

**Issue: Sales Context Panel not showing**
- ✓ Make sure all columns in CSV match exact field names
- ✓ Fields are case-sensitive: `ProductCategory`, `Region`, etc.
- ✓ At least 2 rows of data needed for extraction

**Issue: Gemini explanation not appearing**
- ✓ Check GEMINI_API_KEY environment variable is set
- ✓ Verify API key is valid in Google Cloud Console
- ✓ System will use rule-based fallback if API unavailable

**Issue: Forecast doesn't generate**
- ✓ Ensure at least 2 data points in CSV
- ✓ Check Date format is YYYY-MM-DD
- ✓ Sales values must be numeric
- ✓ Check backend logs for specific errors

### Performance Tips

1. **For Better Forecasts:**
   - Use at least 30 data points (2+ months)
   - Ensure consistent date spacing
   - Include all relevant sales dimensions

2. **For Better AI Explanations:**
   - Provide complete sales data (categories, regions, etc.)
   - Include promotion flags for impact analysis
   - Add marketing spend data for ROI correlation

3. **For Faster Response:**
   - Shorter forecast horizon (7 days faster than 90)
   - Fewer data points (but minimum 2)
   - Model selection: auto > prophet > sarima > moving_average

### Examples

#### Retail Forecast
```csv
Date,Sales,ProductCategory,Region,Quantity,IsPromotion,MarketingSpend
2024-01-01,10000,Electronics,North America,50,0,2000
2024-01-02,12000,Electronics,North America,60,1,3000
2024-01-03,8500,Apparel,Europe,35,0,1500
```

#### E-commerce Forecast
```csv
Date,Sales,ProductCategory,Region,WebsiteTraffic,ConversionRate,UnitPrice
2024-01-01,5000,Home,APAC,8500,2.1,150
2024-01-02,5500,Electronics,North America,9500,2.4,250
2024-01-03,4200,Apparel,Europe,7200,1.9,180
```

#### Multi-Segment B2B Forecast
```csv
Date,Sales,CustomerSegment,Region,Quantity,UnitPrice,MarketingSpend
2024-01-01,50000,Enterprise,North America,200,250,5000
2024-01-02,45000,SMB,Europe,150,300,3000
2024-01-03,25000,Consumer,APAC,100,250,2000
```

### Next Steps

1. ✅ Upload your own CSV with enhanced features
2. ✅ Generate forecasts with multiple dimensions
3. ✅ Review AI explanations for business insights
4. ✅ Track sales context metrics over time
5. ✅ Compare forecasts across product categories/regions

### Support

For detailed documentation, see:
- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - Complete feature guide
- [IMPLEMENTATION_ENHANCEMENTS.md](IMPLEMENTATION_ENHANCEMENTS.md) - Technical details
- [README.md](README.md) - Original setup guide

### Key Takeaways

✨ **The system is now sales-focused:**
- Understands product categories, regions, customer segments
- Analyzes promotion effectiveness and marketing ROI
- Provides business-aware AI explanations
- Displays actionable sales metrics
- Supports flexible CSV formats with any columns
