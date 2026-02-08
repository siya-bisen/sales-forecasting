"""
Main forecasting service that orchestrates model selection and forecasting.
Integrates data validation, model eligibility, and explanation generation.
"""
from typing import List, Dict, Any, Optional
from models.moving_average import MovingAverageModel
from models.prophet_model import ProphetModel
from models.sarima_model import SARIMAModel
from services.model_selector import select_best_model
from services.evaluation import calculate_confidence_level
from services.preprocessing import validate_and_normalize_data
from services.data_validation import validate_minimum_data_points, get_data_quality_notes
from services.model_eligibility import validate_model_selection, filter_eligible_models, check_model_eligibility
from services.explanation_engine import ExplanationEngine
from services.gemini_client import GeminiClient


# Global explanation engine instance (initialized from main.py)
_explanation_engine = None


def initialize_explanation_engine(gemini_api_key: Optional[str] = None) -> None:
    """
    Initialize the global explanation engine.
    Called during app startup in main.py.
    
    Args:
        gemini_api_key: Optional Gemini API key
    """
    global _explanation_engine
    gemini_client = GeminiClient(gemini_api_key)
    _explanation_engine = ExplanationEngine(gemini_client)


def create_model(model_name: str):
    """
    Factory function to create model instance.
    
    Args:
        model_name: Name of the model to create
        
    Returns:
        Model instance
    """
    if model_name == "moving_average":
        return MovingAverageModel(window=7)
    elif model_name == "prophet":
        return ProphetModel()
    elif model_name == "sarima":
        return SARIMAModel()
    else:
        raise ValueError(f"Unknown model: {model_name}")


def generate_forecast(
    data: List[Dict[str, Any]],
    horizon: int,
    model_choice: str = "auto"
) -> Dict[str, Any]:
    """
    Generate sales forecast using specified or auto-selected model.
    
    Args:
        data: List of dictionaries with 'date' and 'sales' keys
        horizon: Number of days to forecast (7, 30, or 90)
        model_choice: Model to use ("auto", "moving_average", "prophet", "sarima")
        
    Returns:
        Dictionary with forecast results
    """
    # Validate and normalize data
    dates, values, metadata = validate_and_normalize_data(data)
    
    # Select model
    if model_choice == "auto":
        model_name, model_reason = select_best_model(dates, values, metadata)
    else:
        model_name = model_choice
        model_reason = {"reason": f"User selected {model_choice}"}
    
    # Create and fit model
    model = create_model(model_name)
    model.fit(dates, values)
    
    # Generate forecast
    forecast_result = model.forecast(horizon)
    
    # Calculate confidence level
    # Use backtest MAPE if available, otherwise estimate
    mape = model_reason.get("mape", 10.0)  # Default to 10% if not available
    confidence = calculate_confidence_level(
        mape,
        metadata["volatility"],
        len(values)
    )
    
    # Generate forecast dates
    from datetime import datetime, timedelta
    last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
    forecast_dates = [
        (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(horizon)
    ]
    
    # Format forecast output
    forecast_output = [
        {
            "date": date,
            "value": round(value, 2),
            "lower": round(lower, 2),
            "upper": round(upper, 2)
        }
        for date, value, lower, upper in zip(
            forecast_dates,
            forecast_result["forecast"],
            forecast_result["lower"],
            forecast_result["upper"]
        )
    ]
    
    # Get model metadata for explanation
    model_metadata = model.get_metadata()
    
    # Determine trend and seasonality from forecast
    trend = forecast_result.get("trend", "stable")
    seasonality = forecast_result.get("seasonality", "none")
    if not seasonality and metadata.get("has_seasonality"):
        seasonality = "weekly"  # Default if detected but not in result
    
    return {
        "model_used": model_name,
        "model_reason": model_reason.get("reason", "Model selected"),
        "confidence_level": confidence,
        "metrics": {
            "mape": round(mape, 2)
        },
        "forecast": forecast_output,
        "summary": {
            "trend": trend,
            "seasonality": seasonality,
            "volatility": metadata["volatility"]
        },
        "metadata": {
            "data_points": len(values),
            "forecast_horizon": horizon,
            "model_metadata": model_metadata
        }
    }
