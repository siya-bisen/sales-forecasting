"""
Auto model selection logic.
Analyzes data characteristics and selects best model.
Applies model eligibility rules based on data length.
"""
from typing import List, Dict, Any, Tuple
from models.moving_average import MovingAverageModel
from models.prophet_model import ProphetModel
from models.sarima_model import SARIMAModel
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
    Applies model eligibility rules: Moving Average (2+), Prophet (14+), SARIMA (30+).
    
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
    
    # Filter to only eligible models based on data length
    all_candidate_models = ["moving_average", "prophet", "sarima"]
    eligible_models, excluded = filter_eligible_models(all_candidate_models, data_length)
    
    # If no eligible models (shouldn't happen with moving_average always eligible), fallback
    if not eligible_models:
        return "moving_average", {
            "reason": "Fallback to baseline model",
            "data_length": data_length
        }
    
    # If only one eligible model, use it
    if len(eligible_models) == 1:
        model_name = eligible_models[0]
        return model_name, {
            "reason": get_single_eligible_model_reason(data_length, data_length),
            "mape": 10.0,  # Estimate
            "data_length": data_length
        }
    
    # Backtest eligible models
    models_to_test = []
    
    # Moving Average (always eligible)
    models_to_test.append(("moving_average", MovingAverageModel, {"window": 7}))
    
    # Prophet (if eligible)
    if "prophet" in eligible_models:
        models_to_test.append(("prophet", ProphetModel, {}))
    
    # SARIMA (if eligible)
    if "sarima" in eligible_models:
        models_to_test.append(("sarima", SARIMAModel, {}))
    
    # Backtest each model
    results = {}
    test_size = min(7, data_length // 4)  # Use 25% of data for testing, max 7 days
    
    for model_name, model_class, kwargs in models_to_test:
        try:
            metrics = backtest_model(model_class, dates, values, test_size, **kwargs)
            results[model_name] = metrics
        except Exception as e:
            # If model fails, assign high error
            results[model_name] = {"mape": float('inf'), "rmse": float('inf')}
    
    # Select model with lowest MAPE
    if not results:
        return "moving_average", {"reason": "Fallback to baseline model"}
    
    best_model = min(results.items(), key=lambda x: x[1]["mape"])
    best_model_name = best_model[0]
    best_mape = best_model[1]["mape"]
    
    # Generate reason for selection
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
    Generate human-readable reason for model selection.
    
    Args:
        model_name: Selected model name
        mape: MAPE of selected model
        data_length: Number of data points
        volatility: Volatility level
        has_seasonality: Whether seasonality was detected
        all_results: Results from all tested models
        excluded: Models excluded due to eligibility rules
        
    Returns:
        Dictionary with reason details
    """
    reasons = []
    
    if excluded:
        if "prophet" in excluded:
            reasons.append("Prophet ineligible (requires 14+ data points)")
        if "sarima" in excluded:
            reasons.append("SARIMA ineligible (requires 30+ data points)")
    
    if model_name == "prophet":
        if has_seasonality:
            reasons.append("Strong seasonality detected")
        if data_length >= 30:
            reasons.append("Sufficient historical data")
        if mape < 10:
            reasons.append("Low prediction error in backtesting")
    elif model_name == "sarima":
        if has_seasonality:
            reasons.append("Seasonal patterns identified")
        if volatility == "moderate":
            reasons.append("Moderate volatility suitable for SARIMA")
        if mape < 10:
            reasons.append("Best backtest performance")
    else:  # moving_average
        if data_length < 30:
            reasons.append("Limited historical data")
        if volatility == "high":
            reasons.append("High volatility favors simple model")
        reasons.append("Stable baseline performance")
    
    # Add performance comparison
    if len(all_results) > 1:
        other_mape = min(
            [r["mape"] for name, r in all_results.items() if name != model_name],
            default=float('inf')
        )
        if mape < other_mape * 0.9:  # At least 10% better
            reasons.append("Significantly outperformed alternatives")
    
    reason_text = "; ".join(reasons) if reasons else "Lowest MAPE among eligible models"
    
    return {
        "reason": reason_text,
        "mape": mape,
        "data_length": data_length,
        "volatility": volatility,
        "has_seasonality": has_seasonality,
        "all_results": {k: v["mape"] for k, v in all_results.items()}
    }
