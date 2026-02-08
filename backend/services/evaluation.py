"""
Model evaluation utilities for backtesting and model selection.
"""
from typing import List, Dict, Any, Tuple
import numpy as np


def calculate_mape(actual: List[float], predicted: List[float]) -> float:
    """
    Calculate Mean Absolute Percentage Error (MAPE).
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        MAPE value (lower is better)
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have same length")
    
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    # Avoid division by zero
    mask = actual != 0
    if not mask.any():
        return float('inf')
    
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    return float(mape)


def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
    """
    Calculate Root Mean Squared Error (RMSE).
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        RMSE value (lower is better)
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have same length")
    
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    return float(rmse)


def backtest_model(
    model_class,
    dates: List[str],
    values: List[float],
    test_size: int = 7,
    **model_kwargs
) -> Dict[str, float]:
    """
    Backtest a model by training on historical data and testing on recent data.
    
    Args:
        model_class: Model class to instantiate
        dates: Full list of dates
        values: Full list of values
        test_size: Number of recent points to use for testing
        **model_kwargs: Additional arguments to pass to model constructor
        
    Returns:
        Dictionary with evaluation metrics
    """
    if len(values) < test_size + 5:
        # Not enough data for backtesting
        return {"mape": float('inf'), "rmse": float('inf')}
    
    # Split data
    train_dates = dates[:-test_size]
    train_values = values[:-test_size]
    test_dates = dates[-test_size:]
    test_values = values[-test_size:]
    
    try:
        # Train model
        model = model_class(**model_kwargs)
        model.fit(train_dates, train_values)
        
        # Forecast
        forecast_result = model.forecast(test_size)
        predicted = forecast_result["forecast"]
        
        # Calculate metrics
        mape = calculate_mape(test_values, predicted)
        rmse = calculate_rmse(test_values, predicted)
        
        return {
            "mape": mape,
            "rmse": rmse
        }
    except Exception as e:
        # If model fails, return high error
        return {"mape": float('inf'), "rmse": float('inf')}


def calculate_confidence_level(
    mape: float,
    volatility: str,
    data_length: int
) -> str:
    """
    Calculate confidence level based on model performance and data quality.
    
    Args:
        mape: Mean Absolute Percentage Error
        volatility: Volatility level ("low", "moderate", "high")
        data_length: Number of data points
        
    Returns:
        Confidence level: "high", "medium", or "low"
    """
    # Base confidence on MAPE
    if mape < 5:
        base_confidence = "high"
    elif mape < 15:
        base_confidence = "medium"
    else:
        base_confidence = "low"
    
    # Adjust based on volatility
    if volatility == "high" and base_confidence == "high":
        base_confidence = "medium"
    elif volatility == "high":
        base_confidence = "low"
    
    # Adjust based on data length
    if data_length < 30 and base_confidence == "high":
        base_confidence = "medium"
    elif data_length < 14:
        base_confidence = "low"
    
    return base_confidence
