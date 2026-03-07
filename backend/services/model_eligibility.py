"""
Model eligibility service for data-specific model requirements.
Enforces model-specific data requirements and filtering.
"""
from typing import List, Dict, Tuple, Any


class ModelIneligibilityError(Exception):
    """Raised when a model is ineligible for the given data."""
    pass


# Model eligibility requirements
MODEL_REQUIREMENTS = {
    "moving_average": {"min_data_points": 2},
    "weighted_moving_average": {"min_data_points": 3},
    "holts_linear_trend": {"min_data_points": 3},
    "polynomial_regression": {"min_data_points": 5},
    "exponential_smoothing": {"min_data_points": 5},
    "seasonal_naive": {"min_data_points": 7},
    "theta": {"min_data_points": 8},
    "arima": {"min_data_points": 10},
    "bayesian_structural": {"min_data_points": 15},
    "prophet": {"min_data_points": 14},
    "vector_ar": {"min_data_points": 20},
    "xgboost": {"min_data_points": 20},
    "random_forest": {"min_data_points": 20},
    "gradient_boosting": {"min_data_points": 25},
    "lstm": {"min_data_points": 30},
    "sarima": {"min_data_points": 30},
    "neural_prophet": {"min_data_points": 30},
}


def check_model_eligibility(model_name: str, data_point_count: int) -> bool:
    """
    Check if a model is eligible for the given amount of data.
    
    Args:
        model_name: Name of the model ("moving_average", "prophet", "sarima")
        data_point_count: Number of data points available
        
    Returns:
        True if model is eligible, False otherwise
    """
    if model_name not in MODEL_REQUIREMENTS:
        return False
    
    min_required = MODEL_REQUIREMENTS[model_name]["min_data_points"]
    return data_point_count >= min_required


def validate_model_selection(
    model_name: str,
    data_point_count: int
) -> None:
    """
    Validate that a manually selected model is eligible for the data.
    
    Args:
        model_name: Name of the model
        data_point_count: Number of data points
        
    Raises:
        ModelIneligibilityError: If model is not eligible
    """
    if not check_model_eligibility(model_name, data_point_count):
        min_required = MODEL_REQUIREMENTS.get(model_name, {}).get("min_data_points", 2)
        
        # Provide helpful suggestions based on model and data
        suggestions = {
            "exponential_smoothing": "Use Moving Average (2+ points) or Exponential Smoothing (5+)",
            "arima": "Use Moving Average (2+), Exponential Smoothing (5+), or ARIMA (10+)",
            "prophet": "Use Moving Average (2+) or Exponential Smoothing (5+) for less data",
            "random_forest": "Use ARIMA (10+), Prophet (14+), or Random Forest (20+)",
            "gradient_boosting": "Use Prophet (14+) or Gradient Boosting (25+)",
            "sarima": "Use Prophet (14+) or SARIMA (30+) for seasonal data"
        }
        
        suggestion = suggestions.get(model_name, "Consider using Moving Average (2+ points)")
        
        error_msg = (
            f"{model_name} requires at least {min_required} data points, "
            f"but only {data_point_count} were provided. {suggestion}"
        ).strip()
        raise ModelIneligibilityError(error_msg)


def filter_eligible_models(
    candidate_models: List[str],
    data_point_count: int
) -> Tuple[List[str], Dict[str, str]]:
    """
    Filter models to only those eligible for the given data.
    
    Args:
        candidate_models: List of model names to consider
        data_point_count: Number of data points
        
    Returns:
        Tuple of (eligible_models, exclusion_reasons)
    """
    eligible = []
    excluded = {}
    
    for model in candidate_models:
        if check_model_eligibility(model, data_point_count):
            eligible.append(model)
        else:
            min_required = MODEL_REQUIREMENTS.get(model, {}).get("min_data_points", 0)
            excluded[model] = (
                f"{model} requires {min_required} data points "
                f"(only {data_point_count} available)"
            )
    
    return eligible, excluded


def get_single_eligible_model_reason(
    data_point_count: int,
    data_length: int
) -> str:
    """
    Generate reason when only one model is eligible.
    
    Args:
        data_point_count: Number of data points
        data_length: Not used, for compatibility
        
    Returns:
        Reason string
    """
    return "Only one model met the minimum data requirements."
