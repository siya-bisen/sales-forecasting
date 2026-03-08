"""
Moving Average forecasting model (baseline).
Simple but interpretable baseline model.
Enhanced with robust input validation and adaptive parameters.
"""
from typing import List, Dict, Any
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class MovingAverageModel:
    """Simple moving average forecasting model with enhanced robustness."""
    
    def __init__(self, window: int = None):
        """
        Initialize moving average model with adaptive window.
        
        Args:
            window: Number of periods to average (auto-selected if None)
        """
        self.window = window
        self.last_value = None
        self.mean = None
        self.std = None
        self.fitted = False
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit the model to historical data with robust validation.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 2:
            raise ValueError(f"Need at least 2 data points (have {len(values) if values else 0})")
        
        # Clean invalid values
        values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        if len(values_clean) < 2:
            raise ValueError("Not enough valid data points")
        
        values_array = np.array(values_clean, dtype=float)
        
        # Auto-select window if not provided
        if self.window is None:
            self.window = min(7, max(2, len(values_array) // 3))
        else:
            self.window = min(max(2, self.window), len(values_array))
        
        if len(values_array) < self.window:
            # If not enough data, use all available
            self.mean = np.mean(values_array)
            self.std = np.std(values_array) if len(values_array) > 1 else max(values_array) * 0.1
        else:
            # Use last window values
            recent_values = values_array[-self.window:]
            self.mean = np.mean(recent_values)
            self.std = np.std(recent_values) if len(recent_values) > 1 else self.mean * 0.1
        
        # Ensure std is not zero
        if self.std == 0 or np.isnan(self.std):
            self.std = self.mean * 0.1 if self.mean > 0 else 1
        
        self.last_value = float(values_array[-1])
        self.fitted = True
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast for specified horizon.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if not self.fitted or self.mean is None:
            raise ValueError("Model must be fitted before forecasting")
        
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        # Simple forecast: use mean value for all future periods
        forecast_values = [max(0, self.mean) for _ in range(horizon)]
        
        # Confidence intervals (assuming normal distribution)
        # Use 1.96 * std for 95% confidence interval
        confidence_multiplier = 1.96
        margin = confidence_multiplier * self.std
        
        lower_bounds = [max(0, self.mean - margin) for _ in range(horizon)]
        upper_bounds = [self.mean + margin for _ in range(horizon)]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "moving_average",
            "window": self.window,
            "trend": self._detect_trend(),
            "mean": float(self.mean),
            "std": float(self.std)
        }
    
    def _detect_trend(self) -> str:
        """Detect trend direction (always stable for MA)."""
        return "stable"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "moving_average",
            "window": self.window,
            "mean": float(self.mean) if self.mean is not None else None,
            "std": float(self.std) if self.std is not None else None,
            "fitted": self.fitted,
            "description": f"Moving Average with window size {self.window} - Simple baseline model"
        }
