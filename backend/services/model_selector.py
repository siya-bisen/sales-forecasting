"""
Auto model selection logic.
Analyzes data characteristics and selects best model.
Applies model eligibility rules based on data length.
Includes 17 forecasting models: MA, ExpSmoothing, ARIMA, Prophet, SARIMA, GB, RF, XGBoost, LSTM, 
Seasonal Naive, Holt's, BSTS, VAR, Polynomial, WMA, Theta, NeuralProphet.
"""
from typing import List, Dict, Any, Tuple
from models.moving_average import MovingAverageModel
from models.prophet_model import ProphetModel
from models.sarima_model import SARIMAModel
from models.exponential_smoothing import ExponentialSmoothingModel
from models.arima_model import ARIMAModel
from models.random_forest_model import RandomForestModel
from models.gradient_boosting_model import GradientBoostingModel
from models.xgboost_model import XGBoostModel
from models.lstm_model import LSTMModel
from models.seasonal_naive_model import SeasonalNaiveModel
from models.holts_linear_trend_model import HoltsLinearTrendModel
from models.bayesian_structural_model import BayesianStructuralTimeSeriesModel
from models.vector_ar_model import VectorARModel
from models.polynomial_regression_model import PolynomialRegressionModel
from models.weighted_moving_average_model import WeightedMovingAverageModel
from models.theta_method_model import ThetaMethodModel
from models.neural_prophet_model import NeuralProphetModel
from services.evaluation import backtest_model, calculate_confidence_level
from services.preprocessing import calculate_volatility, detect_seasonality
from services.model_eligibility import filter_eligible_models, get_single_eligible_model_reason


def select_best_model(
    dates: List[str],
    values: List[float],
    metadata: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """
    Automatically select the best forecasting model based on data characteristics.
    Eligibility rules (min data points):
    - Moving Average: 2+
    - Weighted MA: 3+
    - Holt's Linear: 3+
    - Polynomial: 5+
    - Exponential Smoothing: 5+
    - Seasonal Naive: 7+
    - Theta: 8+
    - ARIMA: 10+
    - BSTS: 15+
    - Prophet: 14+
    - VAR: 20+
    - XGBoost: 20+
    - Random Forest: 20+
    - Gradient Boosting: 25+
    - LSTM: 30+
    - SARIMA: 30+
    - NeuralProphet: 30+
    
    Args:
        dates: List of date strings
        values: List of sales values
        metadata: Data metadata from preprocessing
        
    Returns:
        Tuple of (model_name, reason_dict)
    """
    data_length = len(values)
    volatility = metadata.get("volatility", "moderate")
    has_seasonality = metadata.get("has_seasonality", False)
    
    # Define eligibility rules
    model_eligibility = {
        "moving_average": 2,
        "weighted_moving_average": 3,
        "holts_linear_trend": 3,
        "polynomial_regression": 5,
        "exponential_smoothing": 5,
        "seasonal_naive": 7,
        "theta": 8,
        "arima": 10,
        "bayesian_structural": 15,
        "prophet": 14,
        "vector_ar": 20,
        "xgboost": 20,
        "random_forest": 20,
        "gradient_boosting": 25,
        "lstm": 30,
        "sarima": 30,
        "neural_prophet": 30
    }
    
    # Filter eligible models
    eligible_models = [
        name for name, min_points in model_eligibility.items()
        if data_length >= min_points
    ]
    
    excluded = {
        name: f"Requires {min_points}+ data points (have {data_length})"
        for name, min_points in model_eligibility.items()
        if data_length < min_points
    }
    
    # Fallback if no eligible models
    if not eligible_models:
        return "moving_average", {
            "reason": "Fallback to baseline model",
            "data_length": data_length
        }
    
    # If only one eligible model, use it
    if len(eligible_models) == 1:
        model_name = eligible_models[0]
        return model_name, {
            "reason": f"Only eligible model for dataset size ({data_length} points)",
            "mape": 10.0,
            "data_length": data_length,
            "model_info": _get_model_description(model_name)
        }
    
    # Prepare models to test
    models_to_test = []
    
    if "moving_average" in eligible_models:
        models_to_test.append(("moving_average", MovingAverageModel, {"window": 7}))
    
    if "weighted_moving_average" in eligible_models:
        models_to_test.append(("weighted_moving_average", WeightedMovingAverageModel, {}))
    
    if "holts_linear_trend" in eligible_models:
        models_to_test.append(("holts_linear_trend", HoltsLinearTrendModel, {}))
    
    if "polynomial_regression" in eligible_models:
        models_to_test.append(("polynomial_regression", PolynomialRegressionModel, {}))
    
    if "exponential_smoothing" in eligible_models:
        models_to_test.append(("exponential_smoothing", ExponentialSmoothingModel, {}))
    
    if "seasonal_naive" in eligible_models:
        models_to_test.append(("seasonal_naive", SeasonalNaiveModel, {}))
    
    if "theta" in eligible_models:
        models_to_test.append(("theta", ThetaMethodModel, {}))
    
    if "arima" in eligible_models:
        models_to_test.append(("arima", ARIMAModel, {}))
    
    if "bayesian_structural" in eligible_models:
        models_to_test.append(("bayesian_structural", BayesianStructuralTimeSeriesModel, {}))
    
    if "prophet" in eligible_models:
        models_to_test.append(("prophet", ProphetModel, {}))
    
    if "vector_ar" in eligible_models:
        models_to_test.append(("vector_ar", VectorARModel, {}))
    
    if "xgboost" in eligible_models:
        models_to_test.append(("xgboost", XGBoostModel, {}))
    
    if "random_forest" in eligible_models:
        models_to_test.append(("random_forest", RandomForestModel, {}))
    
    if "gradient_boosting" in eligible_models:
        models_to_test.append(("gradient_boosting", GradientBoostingModel, {}))
    
    if "lstm" in eligible_models:
        models_to_test.append(("lstm", LSTMModel, {}))
    
    if "sarima" in eligible_models:
        models_to_test.append(("sarima", SARIMAModel, {}))
    
    if "neural_prophet" in eligible_models:
        models_to_test.append(("neural_prophet", NeuralProphetModel, {}))
    
    # Backtest models
    results = {}
    test_size = min(7, max(2, data_length // 4))
    
    for model_name, model_class, kwargs in models_to_test:
        try:
            metrics = backtest_model(model_class, dates, values, test_size, **kwargs)
            results[model_name] = metrics
        except Exception as e:
            results[model_name] = {"mape": float('inf'), "rmse": float('inf')}
    
    # Select best model
    if not results or all(r["mape"] == float('inf') for r in results.values()):
        return "moving_average", {"reason": "Fallback to baseline model"}
    
    best_model = min(results.items(), key=lambda x: x[1]["mape"])
    best_model_name = best_model[0]
    best_mape = best_model[1]["mape"]
    
    # Generate reason
    reason = generate_selection_reason(
        best_model_name,
        best_mape,
        data_length,
        volatility,
        has_seasonality,
        results,
        excluded
    )
    
    return best_model_name, reason


def generate_selection_reason(
    model_name: str,
    mape: float,
    data_length: int,
    volatility: str,
    has_seasonality: bool,
    all_results: Dict[str, Dict[str, float]],
    excluded: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Generate detailed reason for model selection with performance analysis.
    Considers data characteristics, model strengths, and backtest results.
    """
    model_descriptions = {
        "moving_average": "Simple Moving Average - Baseline for trend identification",
        "exponential_smoothing": "Exponential Smoothing - Adapts to recent patterns",
        "arima": "ARIMA - Handles non-stationary and trending data",
        "prophet": "Prophet - Excellent for seasonal patterns and trends",
        "random_forest": "Random Forest - ML ensemble capturing complex patterns",
        "gradient_boosting": "Gradient Boosting - Advanced ensemble with rich features",
        "sarima": "SARIMA - Combines seasonal and non-seasonal patterns"
    }
    
    reasons = []
    
    # Model-specific selection logic
    if model_name == "gradient_boosting":
        reasons.append("Advanced ensemble with sophisticated feature engineering")
        if data_length >= 50:
            reasons.append("Sufficient data for gradient boosting")
        if volatility == "high":
            reasons.append("Handles high volatility through non-linear patterns")
    elif model_name == "random_forest":
        reasons.append("ML ensemble capturing non-linear relationships")
        if data_length >= 25:
            reasons.append("Adequate data for ML model training")
    elif model_name == "arima":
        reasons.append("Auto-detected ARIMA parameters for trend handling")
        if data_length >= 15:
            reasons.append("Sufficient historical data for ARIMA")
    elif model_name == "exponential_smoothing":
        reasons.append("Exponential smoothing with trend/seasonality detection")
        if has_seasonality:
            reasons.append("Captures seasonality effectively")
    elif model_name == "prophet":
        reasons.append("Handles trends and seasonal patterns")
        if has_seasonality:
            reasons.append("Strong seasonality detected - Prophet excels here")
        if data_length >= 30:
            reasons.append("Sufficient data for seasonal decomposition")
        if mape < 10:
            reasons.append("Low prediction error in backtesting")
    elif model_name == "sarima":
        reasons.append("Seasonal ARIMA for complex patterns")
        if has_seasonality:
            reasons.append("Seasonal patterns identified")
        if mape < 10:
            reasons.append("Best overall backtest performance")
    else:  # moving_average
        reasons.append("Stable baseline for trend identification")
        if data_length < 30:
            reasons.append("Limited historical data - simple model preferred")
    
    # Performance comparison
    if all_results and len(all_results) > 1:
        other_mapes = [r["mape"] for n, r in all_results.items() if n != model_name and r["mape"] != float('inf')]
        if other_mapes:
            best_other = min(other_mapes)
            if mape < best_other * 0.9:
                reasons.append("Significantly outperformed alternatives")
            elif mape < best_other * 1.1:
                reasons.append("Comparable performance to best alternative")
    
    reason_text = "; ".join(reasons) if reasons else "Lowest MAPE among eligible models"
    
    return {
        "model": model_name,
        "description": model_descriptions.get(model_name, "Forecasting Model"),
        "reason": reason_text,
        "mape": round(mape, 2),
        "data_length": data_length,
        "volatility": volatility,
        "has_seasonality": has_seasonality,
        "tested_models": len(all_results) if all_results else 0,
        "model_performance": {k: round(v["mape"], 2) for k, v in (all_results or {}).items()},
        "excluded_models": excluded if excluded else {}
    }


def _get_model_description(model_name: str) -> str:
    """Get description of forecasting model."""
    descriptions = {
        "moving_average": "Simple moving average - good baseline",
        "weighted_moving_average": "Weighted MA with recent bias",
        "holts_linear_trend": "Holt's trend-following method",
        "polynomial_regression": "Polynomial trend fitting",
        "exponential_smoothing": "Exponential smoothing - adapts to trends and seasonality",
        "seasonal_naive": "Naive seasonal baseline",
        "theta": "Theta method - excellent short-term",
        "arima": "ARIMA - auto-detects parameters for trend handling",
        "bayesian_structural": "BSTS - probabilistic with uncertainty",
        "prophet": "Prophet - excellent for seasonal patterns",
        "vector_ar": "VAR - multivariate model",
        "xgboost": "XGBoost - advanced gradient boosting",
        "random_forest": "Random Forest - ML ensemble for complex patterns",
        "gradient_boosting": "Gradient Boosting - advanced ensemble with feature engineering",
        "lstm": "LSTM - deep learning neural network",
        "sarima": "SARIMA - combines seasonal and non-seasonal patterns",
        "neural_prophet": "NeuralProphet - neural network variant of Prophet"
    }
    return descriptions.get(model_name, "Forecasting Model")


def _get_selection_explanation(
    model_name: str,
    mape: float,
    volatility: str,
    has_seasonality: bool,
    data_length: int
) -> str:
    """Generate explanation for why this model was selected."""
    explanations = []
    
    if model_name == "gradient_boosting":
        explanations.append("Advanced ML ensemble with 9 engineered features")
        if data_length > 50:
            explanations.append("Large dataset enables complex pattern learning")
    elif model_name == "random_forest":
        explanations.append("ML ensemble with feature importance analysis")
        if data_length > 30:
            explanations.append("Adequate training data for ensemble")
    elif model_name == "arima":
        explanations.append("Auto-detects trend through ADF test")
        if volatility in ["high", "moderate"]:
            explanations.append("Effective for volatile data")
    elif model_name == "exponential_smoothing":
        if has_seasonality:
            explanations.append("Holt-Winters method handles seasonality")
        else:
            explanations.append("Simple exponential smoothing for trend following")
    elif model_name == "prophet":
        if has_seasonality:
            explanations.append("Prophet decomposition captures seasonal components")
        explanations.append("Handles trend changes and growth")
    elif model_name == "sarima":
        explanations.append("Seasonal ARIMA for complex seasonal patterns")
        if has_seasonality:
            explanations.append("Strong seasonality detected - SARIMA optimal")
    else:  # moving_average
        explanations.append("Simple stable baseline")
        if data_length < 30:
            explanations.append("Limited data - complex models risky")
    
    return "; ".join(explanations) if explanations else "Best MAPE performance"
