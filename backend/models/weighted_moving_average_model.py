"""
Weighted Moving Average Model
Enhanced moving average with custom weights.
Recent values have higher influence on forecast.
"""
import numpy as np
from typing import List, Dict, Any, Tuple


class WeightedMovingAverageModel:
    """
    Weighted Moving Average forecasting model.
    Moving average with linearly increasing weights.
    Recent observations have more influence.
    
    Features:
    - Auto-detects optimal window size
    - Weights decline linearly into past
    - Simple and fast
    - Interpretable results
    - Good for trending data
    """
    
    def __init__(self, window: int = None):
        """
        Initialize Weighted Moving Average model.
        
        Args:
            window: Window size (auto-selected if None)
        """
        self.window = window
        self.values = None
        self.weights = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Weighted Moving Average model.
        
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
        
        # Auto-detect window size if not provided
        if self.window is None:
            self.window = self._auto_select_window(values_array)
        else:
            self.window = min(max(3, self.window), len(values_array))
        
        # Create linearly increasing weights
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
            "message": "Recent values have higher influence on forecast"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate weighted moving average forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.values is None or self.weights is None:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "weighted_moving_average",
                "trend": "stable",
                "seasonality": "none"
            }
        
        forecast_values = []
        current_window = self.values[-self.window:].copy()
        
        for _ in range(horizon):
            # Calculate weighted average
            wma = np.sum(current_window * self.weights)
            forecast_values.append(wma)
            
            # Update window: remove oldest, add newest
            current_window = np.concatenate([current_window[1:], [wma]])
        
        # Calculate uncertainty based on historical volatility
        residuals = self._calculate_residuals()
        residual_std = np.std(residuals) if len(residuals) > 0 else 1.0
        
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
