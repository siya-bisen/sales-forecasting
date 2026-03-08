"""
Weighted Moving Average Model
Enhanced moving average with custom weights.
Recent values have higher influence on forecast.
Improved with robust validation and adaptive parameters.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class WeightedMovingAverageModel:
    """Weighted Moving Average forecasting model with enhanced robustness."""
    
    def __init__(self, window: int = None):
        """
        Initialize Weighted Moving Average model with adaptive window.
        
        Args:
            window: Window size (auto-selected if None)
        """
        self.window = window
        self.values = None
        self.weights = None
        self.metadata = {}
        self.fitted = False
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Weighted Moving Average model with validation.
        
        Args:
            dates: List of date strings
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
        self.values = values_array
        
        # Auto-detect window size if not provided
        if self.window is None:
            self.window = self._auto_select_window(values_array)
        else:
            self.window = min(max(2, self.window), len(values_array))
        
        # Create linearly increasing weights (recent values have more weight)
        self.weights = np.linspace(1, self.window, self.window)
        self.weights = self.weights / np.sum(self.weights)  # Normalize
        
        # Calculate trend
        trend_direction = self._detect_trend()
        
        # Calculate autocorrelation
        autocorr = self._calculate_autocorrelation()
        
        self.metadata = {
            "type": "Weighted Moving Average",
            "window": self.window,
            "trend_direction": trend_direction,
            "autocorrelation": round(autocorr, 3),
            "data_points_used": len(values_array),
            "interpretation": f"WMA({self.window}) with linearly increasing weights",
            "fitted": True,
            "message": "Recent values have higher influence on forecast"
        }
        self.fitted = True
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate weighted moving average forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if not self.fitted or self.values is None or self.weights is None:
            raise ValueError("Model must be fitted before forecasting")
        
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            forecast_values = []
            current_window = self.values[-self.window:].copy()
            
            for _ in range(horizon):
                # Calculate weighted average
                wma = float(np.sum(current_window * self.weights))
                forecast_values.append(max(0, wma))
                
                # Update window: remove oldest, add newest
                current_window = np.concatenate([current_window[1:], [wma]])
            
            # Calculate uncertainty based on historical volatility
            residuals = self._calculate_residuals()
            residual_std = np.std(residuals) if len(residuals) > 0 else np.mean(forecast_values) * 0.1
            if residual_std == 0:
                residual_std = np.mean(forecast_values) * 0.1 if np.mean(forecast_values) > 0 else 1
            
            lower_bounds = [max(0, v - 1.96 * residual_std) for v in forecast_values]
            upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "weighted_moving_average",
                "window": self.window,
                "trend": self._detect_trend(),
                "seasonality": "none"
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
        
        lower_bounds = [v - 1.96 * residual_std for v in forecast_values]
        upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "weighted_moving_average",
            "trend": "stable",
            "seasonality": "none"
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _auto_select_window(self, values: np.ndarray) -> int:
        """Auto-select optimal window size."""
        n = len(values)
        
        if n < 7:
            return 3
        elif n < 30:
            return 5
        elif n < 90:
            return 7
        else:
            return 14
    
    def _detect_trend(self) -> str:
        """Detect trend direction."""
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
    
    def _calculate_autocorrelation(self) -> float:
        """Calculate lag-1 autocorrelation."""
        if self.values is None or len(self.values) < 2:
            return 0.0
        
        mean = np.mean(self.values)
        c0 = np.sum((self.values - mean) ** 2) / len(self.values)
        c1 = np.sum((self.values[:-1] - mean) * (self.values[1:] - mean)) / len(self.values)
        
        if c0 == 0:
            return 0.0
        
        return c1 / c0
    
    def _calculate_residuals(self) -> np.ndarray:
        """Calculate residuals for uncertainty estimation."""
        if self.values is None or len(self.values) < self.window:
            return np.array([])
        
        residuals = []
        
        for i in range(self.window, len(self.values)):
            window_vals = self.values[i-self.window:i]
            wma = np.sum(window_vals * self.weights)
            residual = self.values[i] - wma
            residuals.append(residual)
        
        return np.array(residuals)
