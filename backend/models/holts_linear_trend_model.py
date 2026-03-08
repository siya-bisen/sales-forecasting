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
        Fit Holt's Linear Trend model with robust validation.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 3:
            raise ValueError(f"Need at least 3 data points (have {len(values) if values else 0})")
        
        # Clean invalid values
        values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        if len(values_clean) < 3:
            raise ValueError("Not enough valid data points")
        
        values_array = np.array(values_clean, dtype=float)
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
                "fitted": True,
                "interpretation": f"Linear trend with {trend_direction} direction",
                "message": "Exponential smoothing with explicit trend component"
            }
        except Exception as e:
            raise ValueError(f"Failed to fit model: {str(e)}")
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast using Holt's Linear Trend with robust bounds.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.model is None or self.values is None:
            raise ValueError("Model must be fitted before forecasting")
        
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            # Get forecast
            forecast_result = self.model.get_forecast(steps=horizon)
            forecast_values = [max(0, float(v)) for v in forecast_result.predicted_mean.tolist()]
            
            # Get confidence intervals
            try:
                confidence_intervals = forecast_result.conf_int(alpha=0.05)
                lower_bounds = [max(0, float(v)) for v in confidence_intervals.iloc[:, 0].tolist()]
                upper_bounds = [max(0, float(v)) for v in confidence_intervals.iloc[:, 1].tolist()]
            except Exception:
                # Fallback: use standard error
                std_error = np.std(forecast_values) if np.std(forecast_values) > 0 else np.mean(forecast_values) * 0.1
                lower_bounds = [max(0, v - 1.96 * std_error) for v in forecast_values]
                upper_bounds = [v + 1.96 * std_error for v in forecast_values]
            
            # Ensure bounds are valid
            for i in range(len(forecast_values)):
                lower_bounds[i] = min(lower_bounds[i], forecast_values[i])
                upper_bounds[i] = max(upper_bounds[i], forecast_values[i])
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "holts_linear_trend",
                "trend": self._detect_trend(),
                "seasonality": "none",
                "alpha": float(self.alpha) if self.alpha else None,
                "beta": float(self.beta) if self.beta else None
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
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
