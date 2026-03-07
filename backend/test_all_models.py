#!/usr/bin/env python3
"""
Test script to validate all 17 models return correct format (dict with forecast, lower, upper keys).
"""
import sys
from datetime import datetime, timedelta
import numpy as np

# Sample data for testing
dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(60, 0, -1)]
values = [100 + np.sin(i/10) * 20 + np.random.normal(0, 5) for i in range(60)]

models_to_test = [
    ("moving_average", "MovingAverageModel"),
    ("prophet_model", "ProphetModel"),
    ("sarima_model", "SARIMAModel"),
    ("exponential_smoothing", "ExponentialSmoothingModel"),
    ("arima_model", "ARIMAModel"),
    ("random_forest_model", "RandomForestModel"),
    ("gradient_boosting_model", "GradientBoostingModel"),
    ("xgboost_model", "XGBoostModel"),
    ("lstm_model", "LSTMModel"),
    ("seasonal_naive_model", "SeasonalNaiveModel"),
    ("holts_linear_trend_model", "HoltsLinearTrendModel"),
    ("bayesian_structural_model", "BayesianStructuralTimeSeriesModel"),
    ("polynomial_regression_model", "PolynomialRegressionModel"),
    ("weighted_moving_average_model", "WeightedMovingAverageModel"),
    ("theta_method_model", "ThetaMethodModel"),
    ("neural_prophet_model", "NeuralProphetModel"),
    ("vector_ar_model", "VectorARModel"),
]

print("Testing all 17 models for correct return format...")
print("=" * 60)

passed = 0
failed = 0
errors = []

for module_name, class_name in models_to_test:
    try:
        # Import model
        module = __import__(f"models.{module_name}", fromlist=[class_name])
        ModelClass = getattr(module, class_name)
        
        # Create and fit model
        model = ModelClass()
        model.fit(dates, values)
        
        # Generate forecast
        result = model.forecast(horizon=7)
        
        # Validate return format
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "forecast" in result, "Missing 'forecast' key"
        assert "lower" in result, "Missing 'lower' key"
        assert "upper" in result, "Missing 'upper' key"
        assert isinstance(result["forecast"], list), "forecast must be a list"
        assert isinstance(result["lower"], list), "lower must be a list"
        assert isinstance(result["upper"], list), "upper must be a list"
        assert len(result["forecast"]) == 7, "forecast length mismatch"
        assert len(result["lower"]) == 7, "lower length mismatch"
        assert len(result["upper"]) == 7, "upper length mismatch"
        
        print(f"✓ {class_name:40} PASS")
        passed += 1
        
    except Exception as e:
        print(f"✗ {class_name:40} FAIL: {str(e)[:50]}")
        failed += 1
        errors.append((class_name, str(e)))

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed out of {len(models_to_test)} models")

if failed > 0:
    print("\nFailures:")
    for model_name, error in errors:
        print(f"  {model_name}: {error}")
    sys.exit(1)
else:
    print("\n✓ All models return correct format!")
    sys.exit(0)
