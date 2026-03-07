# Sales Context - Visual Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SALES FORECAST SYSTEM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ FRONTEND (React/Next.js)                                     │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ CSVUpload Component                                  │  │   │
│  │  │ ├─ Parse CSV file                                   │  │   │
│  │  │ ├─ Extract: date, sales (REQUIRED)                 │  │   │
│  │  │ └─ Extract: ProductCategory, Region, etc. (OPTIONAL) │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          ↓                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ ForecastDataPoint[] sent to backend                 │  │   │
│  │  │ {                                                   │  │   │
│  │  │   date: "2024-01-01",                              │  │   │
│  │  │   sales: 1200,                                     │  │   │
│  │  │   ProductCategory: "Electronics",     /* OPTIONAL */│  │   │
│  │  │   Region: "North America",            /* OPTIONAL */│  │   │
│  │  │   Quantity: 150,                      /* OPTIONAL */│  │   │
│  │  │   ...                                               │  │   │
│  │  │ }                                                   │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
├─────────────────────────────────────────────────────────────────────┤
│                        NETWORK CALL                                  │
│                    POST /api/forecast                                │
├─────────────────────────────────────────────────────────────────────┤
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ BACKEND (FastAPI/Python)                                     │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Forecast Route Handler                               │  │   │
│  │  │ ├─ Validate data                                    │  │   │
│  │  │ ├─ Call: generate_forecast()                        │  │   │
│  │  │ └─ Call: _generate_explanation()                    │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          ↓                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ generate_forecast() in forecasting.py               │  │   │
│  │  │ ├─ Normalize data                                   │  │   │
│  │  │ ├─ Call: _extract_sales_context(data)              │  │   │
│  │  │ ├─ Select forecasting model                         │  │   │
│  │  │ ├─ Generate forecast                                │  │   │
│  │  │ └─ Return result with sales_context                │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          ↓                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ _extract_sales_context(data)                         │  │   │
│  │  │                                                      │  │   │
│  │  │ For each optional column:                           │  │   │
│  │  │ ├─ ProductCategory → Extract unique & join         │  │   │
│  │  │ ├─ Region → Extract unique & join                  │  │   │
│  │  │ ├─ CustomerSegment → Extract unique & join         │  │   │
│  │  │ ├─ MarketingSpend → Calculate average              │  │   │
│  │  │ ├─ IsPromotion → Analyze impact percentage         │  │   │
│  │  │ ├─ Quantity → Calculate average with units         │  │   │
│  │  │ └─ UnitPrice → Calculate average with $            │  │   │
│  │  │                                                      │  │   │
│  │  │ Return: {                                           │  │   │
│  │  │   product_category: "Electronics, Software",       │  │   │
│  │  │   regions: "Asia, Europe, North America",          │  │   │
│  │  │   ...                                              │  │   │
│  │  │ }                                                   │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ForecastResponse returned                                    │   │
│  │ {                                                            │   │
│  │   data_points: 30,                                           │   │
│  │   model_used: "prophet",                                     │   │
│  │   forecast: [...],                                           │   │
│  │   sales_context: {                                           │   │
│  │     product_category: "Electronics, Software",               │   │
│  │     regions: "Asia, Europe, North America",                  │   │
│  │     customer_segments: "Enterprise, SMB",                    │   │
│  │     avg_marketing_spend: "$4,500",                           │   │
│  │     promotion_impact: "Promotions +15%",                     │   │
│  │     avg_quantity: "175 units",                               │   │
│  │     avg_unit_price: "$8.50"                                  │   │
│  │   },                                                         │   │
│  │   explanation: {...}                                         │   │
│  │ }                                                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
├─────────────────────────────────────────────────────────────────────┤
│                        NETWORK RESPONSE                              │
├─────────────────────────────────────────────────────────────────────┤
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ FRONTEND - ForecastChart Component                           │   │
│  │                                                              │   │
│  │  Check: Do we have meaningful sales_context?               │   │
│  │                                                              │   │
│  │  ┌─ YES (values exist & not default) ──────┐               │   │
│  │  │                                           │               │   │
│  │  │  Display Context Cards Section:          │               │   │
│  │  │  ┌──────────────────────────────────┐   │               │   │
│  │  │  │ 📊 Sales Business Context        │   │               │   │
│  │  │  ├──────────────────────────────────┤   │               │   │
│  │  │  │ ┌──────────────────────────────┐ │   │               │   │
│  │  │  │ │ Product Categories           │ │   │               │   │
│  │  │  │ │ Electronics, Software        │ │   │               │   │
│  │  │  │ └──────────────────────────────┘ │   │               │   │
│  │  │  │ ┌──────────────────────────────┐ │   │               │   │
│  │  │  │ │ Geographic Regions           │ │   │               │   │
│  │  │  │ │ Asia, Europe, N. America     │ │   │               │   │
│  │  │  │ └──────────────────────────────┘ │   │               │   │
│  │  │  │ ┌──────────────────────────────┐ │   │               │   │
│  │  │  │ │ Avg Marketing Spend          │ │   │               │   │
│  │  │  │ │ $4,500                       │ │   │               │   │
│  │  │  │ └──────────────────────────────┘ │   │               │   │
│  │  │  │ ... more cards ...               │   │               │   │
│  │  │  └──────────────────────────────────┘   │               │   │
│  │  │                                           │               │   │
│  │  └─ NO (all values are default) ──┐        │               │   │
│  │  │                                │        │               │   │
│  │  │  Display Onboarding Guide:     │        │               │   │
│  │  │  ┌──────────────────────────────────┐   │               │   │
│  │  │  │ ✨ Enhance Your Forecast       │   │               │   │
│  │  │  │                                 │   │               │   │
│  │  │  │ Your CSV only has date & sales  │   │               │   │
│  │  │  │                                 │   │               │   │
│  │  │  │ 📋 Suggested columns to add:   │   │               │   │
│  │  │  │ • ProductCategory               │   │               │   │
│  │  │  │ • Region                        │   │               │   │
│  │  │  │ • CustomerSegment               │   │               │   │
│  │  │  │ • MarketingSpend                │   │               │   │
│  │  │  │ • IsPromotion                   │   │               │   │
│  │  │  │ • Quantity                      │   │               │   │
│  │  │  │ • UnitPrice                     │   │               │   │
│  │  │  │                                 │   │               │   │
│  │  │  │ Get deeper AI insights!         │   │               │   │
│  │  │  └──────────────────────────────────┘   │               │   │
│  │  │                                           │               │   │
│  │  └───────────────────────────────────────────┘               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  🎉 USER SEES:                                                       │
│  ├─ Beautiful context cards with extracted data                      │
│  ├─ OR helpful guide on how to enhance CSV                          │
│  ├─ AI analysis informed by business context                        │
│  └─ Better, more accurate forecasts!                                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Transformation Pipeline

```
INPUT: CSV File
┌──────────────────────┐
│ date  │ sales │ Prod │
├───────┼───────┼──────┤
│ 01-01 │ 1200  │ Elec │
│ 01-02 │ 1350  │ Soft │
│ 01-03 │ 1100  │ Elec │
└──────────────────────┘
           ↓ CSVUpload Parsing
┌──────────────────────────────────────┐
│ ForecastDataPoint[] {                │
│   date: "2024-01-01",                │
│   sales: 1200,                       │
│   ProductCategory: "Electronics"     │
│ }                                    │
└──────────────────────────────────────┘
           ↓ Backend Processing
┌──────────────────────────────────────┐
│ sales_context: {                     │
│   product_category: "Electronics,    │
│                     Software",        │
│   regions: "...",                    │
│   avg_quantity: "150 units",         │
│   ...                                │
│ }                                    │
└──────────────────────────────────────┘
           ↓ Frontend Display
┌──────────────────────────────────────┐
│ ✨ BEAUTIFUL CONTEXT CARDS            │
│                                       │
│ [Product: Electronics, Software]     │
│ [Avg Quantity: 150 units]            │
│ [Avg Spend: $5,000]                  │
│ ...                                  │
└──────────────────────────────────────┘
```

---

## Extraction Logic Detail

```
_extract_sales_context(data):
  
  For ProductCategory:
    • Find all unique values in ProductCategory column
    • Join them: "Electronics, Software"
    • Return: "Electronics, Software"
  
  For Region:
    • Find all unique values in Region column
    • Sort them alphabetically
    • Join them: "Asia, Europe, North America"
    • Return: "Asia, Europe, North America"
  
  For MarketingSpend:
    • Find all numeric values in MarketingSpend column
    • Calculate average
    • Format with $ sign and 2 decimals
    • Return: "$5,000.00"
  
  For IsPromotion:
    • Filter data where IsPromotion == 1 (promotions)
    • Get average sales for promotions: avg_promo
    • Get average sales for non-promotions: avg_non_promo
    • Calculate: (avg_promo - avg_non_promo) / avg_non_promo * 100
    • Return: "Promotions increase sales by ~{impact}%"
  
  For Quantity:
    • Find all numeric values in Quantity column
    • Calculate average
    • Format with unit label
    • Return: "{avg} units"
  
  For UnitPrice:
    • Find all numeric values in UnitPrice column
    • Calculate average
    • Format with $ sign and 2 decimals
    • Return: "${avg}"
```

---

## UI Decision Tree

```
                    ForecastChart Renders
                            │
                    ┌────────┴────────┐
                    │                 │
            Has sales_context?        
                    │                 │
             YES ───┼─── NO
                    │      │
        ┌───────────┘      └──────────┐
        │                             │
   Check Values:                Check Values:
   Are ANY meaningful?          Are ALL defaults?
        │                             │
    ┌───┴───┐                     ┌───┴───┐
   YES      NO                   YES      NO
    │       │                     │       │
    │       │              ┌─────┘       └──────────┐
    │       │              │                        │
    │    Show           Show            Show Cards
    │  Default          Onboarding       (partial)
    │  Message          Guide
    │                   
┌──────┐
│CARDS │
│SECT. │  Product: Electronics, Software
│      │  Region: North America
│      │  Avg Spend: $5,000
│      │  Avg Quantity: 150
│      │  ...
└──────┘
```

---

## Example: User Journey

### Step 1: User Creates/Uploads CSV
```csv
date,sales,ProductCategory,Region,Quantity,UnitPrice
2024-01-01,1200,Electronics,North America,150,8.00
2024-01-02,1350,Software,Asia,180,7.50
2024-01-03,1100,Electronics,Europe,120,9.00
```

### Step 2: Frontend Parses CSV
```
✓ Extracted date, sales (required)
✓ Extracted ProductCategory, Region (optional)
✓ Extracted Quantity, UnitPrice (optional)
→ Send to backend
```

### Step 3: Backend Processes
```
✓ Validates data
✓ _extract_sales_context() analyzes:
  - product_category: "Electronics, Software"
  - regions: "Asia, Europe, North America"
  - avg_quantity: "150 units"
  - avg_unit_price: "$8.17"
✓ Builds forecast
✓ Returns response with sales_context
```

### Step 4: Frontend Displays
```
Sales Business Context

┌─────────────────────────┐
│ Product Categories      │
│ Electronics, Software   │
└─────────────────────────┘

┌─────────────────────────┐
│ Geographic Regions      │
│ Asia, Europe, N.America │
└─────────────────────────┘

┌─────────────────────────┐
│ Avg Quantity            │
│ 150 units               │
└─────────────────────────┘

┌─────────────────────────┐
│ Avg Unit Price          │
│ $8.17                   │
└─────────────────────────┘
```

### Step 5: User Sees AI Analysis
- Gemini AI has context about products, regions, volumes, pricing
- Provides deeper, more relevant insights
- Better forecast recommendations

---

## Success Indicators

✅ **Functionality**
- CSV with optional columns uploads successfully
- All columns extracted and sent to backend
- Backend processes and returns sales_context
- Frontend displays context beautifully

✅ **User Experience**
- See context cards when data provided
- See helpful guidance when missing
- Know exactly what to add for better insights
- Clear benefits explained

✅ **Business Value**
- Richer business context
- AI understands company dimensions
- Better, more personalized forecasts
- Data-driven decision making

✅ **Technical Quality**
- No breaking changes
- Backward compatible
- Clean code
- Well documented
