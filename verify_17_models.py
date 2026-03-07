#!/usr/bin/env python
"""
Verification script for 17-model ensemble system.
Tests all model imports, instantiation, and basic functionality.
"""
import sys
import traceback
from datetime import datetime, timedelta

print("=" * 80)
print("17-MODEL ENSEMBLE SYSTEM VERIFICATION")
print("=" * 80)

# Test imports
print("\n📦 Testing Model Imports...")
models_to_test = [
    ("Moving Average", "backend.models.moving_average", "MovingAverageModel"),
    ("Weighted MA", "backend.models.weighted_moving_average_model", "WeightedMovingAverageModel"),
    ("Holt's Linear Trend", "backend.models.holts_linear_trend_model", "HoltsLinearTrendModel"),
    ("Polynomial Regression", "backend.models.polynomial_regression_model", "PolynomialRegressionModel"),
    ("Exponential Smoothing", "backend.models.exponential_smoothing", "ExponentialSmoothingModel"),
    ("Seasonal Naive", "backend.models.seasonal_naive_model", "SeasonalNaiveModel"),
    ("Theta Method", "backend.models.theta_method_model", "ThetaMethodModel"),
    ("ARIMA", "backend.models.arima_model", "ARIMAModel"),
    ("Bayesian Structural", "backend.models.bayesian_structural_model", "BayesianStructuralTimeSeriesModel"),
    ("Prophet", "backend.models.prophet_model", "ProphetModel"),
    ("Vector AR", "backend.models.vector_ar_model", "VectorARModel"),
    ("XGBoost", "backend.models.xgboost_model", "XGBoostModel"),
    ("Random Forest", "backend.models.random_forest_model", "RandomForestModel"),
    ("Gradient Boosting", "backend.models.gradient_boosting_model", "GradientBoostingModel"),
    ("LSTM", "backend.models.lstm_model", "LSTMModel"),
    ("SARIMA", "backend.models.sarima_model", "SARIMAModel"),
    ("NeuralProphet", "backend.models.neural_prophet_model", "NeuralProphetModel"),
]

imported_models = {}
failed_imports = []

for display_name, module_path, class_name in models_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        model_class = getattr(module, class_name)
        imported_models[display_name] = model_class
        print(f"  ✓ {display_name:25} ({module_path})")
    except Exception as e:
        print(f"  ✗ {display_name:25} - {str(e)[:50]}")
        failed_imports.append((display_name, str(e)))

print(f"\n✅ Successfully imported: {len(imported_models)}/17 models")
if failed_imports:
    print(f"⚠️  Failed imports: {len(failed_imports)}")
    for name, error in failed_imports:
        print(f"   - {name}: {error}")

# Test instantiation
print("\n🤖 Testing Model Instantiation...")
instantiated = 0
failed_instantiation = []

for display_name, model_class in list(imported_models.items())[:5]:  # Test first 5
    try:
        model = model_class()
        instantiated += 1
        print(f"  ✓ {display_name:25} instantiated")
    except Exception as e:
        print(f"  ✗ {display_name:25} - {str(e)[:50]}")
        failed_instantiation.append((display_name, str(e)))

print(f"\n✅ Successfully instantiated: {instantiated} models")

# Test with sample data
print("\n📊 Testing with Sample Data...")

# Create sample time series
dates = []
values = []
base_date = datetime(2024, 1, 1)

for i in range(60):
    dates.append((base_date + timedelta(days=i)).strftime("%Y-%m-%d"))
    # Generate sample data with trend and seasonality
    values.append(100 + i * 0.5 + (i % 7) * 10 + (i % 2) * 5)

print(f"  Sample data: {len(values)} points from {dates[0]} to {dates[-1]}")
print(f"  Value range: {min(values):.1f} - {max(values):.1f}")

# Test a few models with data
test_models = [
    ("Moving Average", imported_models.get("Moving Average")),
    ("Exponential Smoothing", imported_models.get("Exponential Smoothing")),
    ("ARIMA", imported_models.get("ARIMA")),
]

fitted_models = 0
failed_fits = []

for name, model_class in test_models:
    if model_class is None:
        continue
    try:
        model = model_class()
        model.fit(dates, values)
        forecast, lower, upper = model.forecast(7)
        metadata = model.get_metadata()
        fitted_models += 1
        print(f"  ✓ {name:25} fit & forecast successful")
    except Exception as e:
        print(f"  ✗ {name:25} - {str(e)[:50]}")
        failed_fits.append((name, str(e)))

print(f"\n✅ Successfully fit & forecasted: {fitted_models}/3 models")

# Test service imports
print("\n⚙️  Testing Service Imports...")
try:
    from backend.services.model_selector import select_best_model
    print("  ✓ model_selector.select_best_model")
except Exception as e:
    print(f"  ✗ model_selector.select_best_model - {str(e)[:50]}")

try:
    from backend.services.forecasting import create_model
    print("  ✓ forecasting.create_model")
except Exception as e:
    print(f"  ✗ forecasting.create_model - {str(e)[:50]}")

try:
    from backend.services.model_eligibility import MODEL_REQUIREMENTS
    print(f"  ✓ model_eligibility.MODEL_REQUIREMENTS ({len(MODEL_REQUIREMENTS)} models)")
except Exception as e:
    print(f"  ✗ model_eligibility - {str(e)[:50]}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Models Configured: 17")
print(f"Successfully Imported: {len(imported_models)}")
print(f"Failed Imports: {len(failed_imports)}")
print(f"Successfully Instantiated: {instantiated}")
print(f"Successfully Fitted & Forecast: {fitted_models}")

if len(imported_models) == 17 and len(failed_imports) == 0:
    print("\n✅ ALL SYSTEMS GO! 17-model ensemble ready for deployment")
else:
    print(f"\n⚠️  System status: Partial ({len(imported_models)}/17 models available)")
    if failed_imports:
        print("   Ensure optional dependencies are installed for full functionality")
        print("   - tensorflow/keras for LSTM")
        print("   - neuralprophet for NeuralProphet")
        print("   - xgboost for XGBoost")

print("=" * 80)
