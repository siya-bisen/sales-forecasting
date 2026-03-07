#!/usr/bin/env python
"""
Quick test to verify all 7 models can be imported and instantiated.
"""
import sys
from datetime import datetime, timedelta

# Test imports
try:
    from backend.models.moving_average import MovingAverageModel
    from backend.models.prophet_model import ProphetModel
    from backend.models.sarima_model import SARIMAModel
    from backend.models.exponential_smoothing import ExponentialSmoothingModel
    from backend.models.arima_model import ARIMAModel
    from backend.models.random_forest_model import RandomForestModel
    from backend.models.gradient_boosting_model import GradientBoostingModel
    from backend.services.model_selector import select_best_model
    print("✓ All model imports successful!")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Create sample data
dates = []
values = []
base_date = datetime(2024, 1, 1)

for i in range(60):
    dates.append((base_date + timedelta(days=i)).strftime("%Y-%m-%d"))
    # Generate some sample data with trend
    values.append(100 + i * 0.5 + (i % 7) * 10)

metadata = {
    "volatility": "moderate",
    "has_seasonality": True,
    "trend": "upward"
}

print("\n📊 Test Data:")
print(f"  - Data points: {len(values)}")
print(f"  - Date range: {dates[0]} to {dates[-1]}")
print(f"  - Value range: {min(values):.1f} to {max(values):.1f}")

# Test model instantiation
print("\n🤖 Model Instantiation:")
models = [
    ("Moving Average", MovingAverageModel),
    ("Exponential Smoothing", ExponentialSmoothingModel),
    ("ARIMA", ARIMAModel),
    ("Prophet", ProphetModel),
    ("Random Forest", RandomForestModel),
    ("Gradient Boosting", GradientBoostingModel),
    ("SARIMA", SARIMAModel)
]

for name, model_class in models:
    try:
        model = model_class()
        print(f"  ✓ {name}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

# Test model selection
print("\n🎯 Model Selection:")
try:
    selected_model, reason = select_best_model(dates, values, metadata)
    print(f"  ✓ Selected: {selected_model}")
    print(f"    Reason: {reason.get('reason', 'N/A')}")
    print(f"    MAPE: {reason.get('mape', 'N/A')}")
except Exception as e:
    print(f"  ✗ Selection error: {e}")

# Test model fitting and forecasting
print("\n🔮 Model Fitting & Forecasting:")
try:
    model = RandomForestModel()
    model.fit(dates, values)
    forecast = model.forecast(7)
    metadata_output = model.get_metadata()
    
    print(f"  ✓ Random Forest fitted and forecasted")
    print(f"    7-day forecast: {[f'{v:.1f}' for v in forecast[:3]]}...")
    print(f"    Metadata keys: {list(metadata_output.keys())}")
except Exception as e:
    print(f"  ✗ Fitting error: {e}")

print("\n✅ All tests completed!")
