"""
Moving Average forecasting model (baseline).
Simple but interpretable baseline model.
"""
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta


class MovingAverageModel:
    """Simple moving average forecasting model."""
    
    def __init__(self, window: int = 7):
        """
        Initialize moving average model.
        
        Args:
            window: Number of periods to average (default: 7 days)
        """
        self.window = window
        self.last_value = None
        self.mean = None
        self.std = None
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit the model to historical data.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        if len(values) < self.window:
            # If not enough data, use all available
            self.mean = np.mean(values)
            self.std = np.std(values) if len(values) > 1 else values[0] * 0.1
        else:
            # Use last window values
            recent_values = values[-self.window:]
            self.mean = np.mean(recent_values)
            self.std = np.std(recent_values) if len(recent_values) > 1 else self.mean * 0.1
        
        self.last_value = values[-1] if values else None
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast for specified horizon.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.mean is None:
            raise ValueError("Model must be fitted before forecasting")
        
        # Simple forecast: use mean value for all future periods
        forecast_values = [self.mean] * horizon
        
        # Confidence intervals (assuming normal distribution)
        # Use 1.96 * std for 95% confidence interval
        confidence_multiplier = 1.96
        lower_bounds = [max(0, self.mean - confidence_multiplier * self.std)] * horizon
        upper_bounds = [self.mean + confidence_multiplier * self.std] * horizon
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "moving_average",
            "window": self.window
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "moving_average",
            "window": self.window,
            "mean": float(self.mean) if self.mean is not None else None,
            "std": float(self.std) if self.std is not None else None
        }
