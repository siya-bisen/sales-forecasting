"""
Holt's Linear Trend Model
Simple trend-following forecasting method.
Extends exponential smoothing with explicit trend component.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class HoltsLinearTrendModel:
    """
    Holt's Linear Trend (Exponential Smoothing with Trend).
    Simple method that explicitly models trend in data.
    
    Features:
    - Automatic alpha (level) and beta (trend) selection
    - Simple and interpretable
    - Fast computation
    - Good for trending but non-seasonal data
    - Additive/multiplicative variant selection
    """
    
    def __init__(self):
        """Initialize Holt's Linear Trend model."""
        self.model = None
        self.alpha = None
        self.beta = None
        self.values = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Holt's Linear Trend model.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < 3:
            self.metadata = {
                "status": "insufficient_data",
                "message": "Need at least 3 data points"
            }
            return
        
        self.values = values_array
        
        try:
            # Fit Holt's Linear Trend (trend='add' for additive)
            self.model = ExponentialSmoothing(
                values_array,
                trend='add',
                seasonal=None,
                initialization_method='estimated'
            ).fit(optimized=True)
            
            # Extract smoothing parameters
            self.alpha = self.model.params.get('smoothing_level', 0.3)
            self.beta = self.model.params.get('smoothing_trend', 0.1)
            
            # Detect trend direction
            trend_direction = self._detect_trend()
            
            self.metadata = {
                "type": "Holt's Linear Trend",
                "alpha": round(float(self.alpha), 4),
                "beta": round(float(self.beta), 4),
                "trend_direction": trend_direction,
                "data_points_used": len(values_array),
                "interpretation": f"Linear trend with {trend_direction} direction",
                "message": "Exponential smoothing with explicit trend component"
            }
        except Exception as e:
            self.metadata = {
                "status": "fitting_error",
                "message": f"Failed to fit model: {str(e)}"
            }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast using Holt's Linear Trend.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.model is None or self.values is None:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "holts_linear_trend",
                "trend": self.trend,
                "seasonality": "none"
            }
        
        try:
            # Get forecast
            forecast_result = self.model.get_forecast(steps=horizon)
            forecast_values = forecast_result.predicted_mean.tolist()
            
            # Get confidence intervals
            confidence_intervals = forecast_result.conf_int(alpha=0.05)
            lower_bounds = confidence_intervals.iloc[:, 0].tolist()
            upper_bounds = confidence_intervals.iloc[:, 1].tolist()
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "holts_linear_trend",
                "trend": self.trend,
                "seasonality": "none"
            }
        except Exception:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "holts_linear_trend",
                "trend": self.trend,
                "seasonality": "none"
            }
            confidence_intervals = forecast_result.conf_int(alpha=0.05)
            lower_bounds = confidence_intervals.iloc[:, 0].tolist()
            upper_bounds = confidence_intervals.iloc[:, 1].tolist()
            
            return forecast_values, lower_bounds, upper_bounds
        except Exception:
            return [np.nan] * horizon, [np.nan] * horizon, [np.nan] * horizon
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _detect_trend(self) -> str:
        """Detect trend direction from data."""
        if self.values is None or len(self.values) < 2:
            return "stable"
        
        first_half = np.mean(self.values[:len(self.values)//2])
        second_half = np.mean(self.values[len(self.values)//2:])
        
        change_pct = (second_half - first_half) / (first_half + 1e-8) * 100
        
        if change_pct > 5:
            return "upward"
        elif change_pct < -5:
            return "downward"
        else:
            return "stable"
