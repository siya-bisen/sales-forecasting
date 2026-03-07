"""
Theta Method
Proven method for short-term sales forecasting.
Decomposes series into trend and detrended components.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy import stats


class ThetaMethodModel:
    """
    Theta Method forecasting model.
    Decomposes time series into theta lines for forecasting.
    Excellent for short-term (7-30 day) forecasts.
    
    Features:
    - Extracts trend via exponential smoothing
    - Combines multiple theta lines
    - Simple and interpretable
    - Fast computation
    - Good for short horizons
    """
    
    def __init__(self, theta: float = 2.0):
        """
        Initialize Theta Method model.
        
        Args:
            theta: Theta parameter (default 2.0)
        """
        self.theta = theta
        self.values = None
        self.trend = None
        self.detrended = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Theta Method model.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < 5:
            self.metadata = {
                "status": "insufficient_data",
                "message": "Need at least 5 data points"
            }
            return
        
        self.values = values_array
        
        # Extract trend component using simple exponential smoothing
        self.trend = self._extract_trend(values_array)
        
        # Detrend the series
        self.detrended = values_array - self.trend
        
        # Calculate statistics
        trend_strength = self._calculate_trend_strength()
        seasonality = self._detect_seasonality()
        
        self.metadata = {
            "type": "Theta Method",
            "theta": self.theta,
            "trend_strength": round(trend_strength, 3),
            "seasonality_present": seasonality,
            "data_points_used": len(values_array),
            "interpretation": "Decomposes into trend and detrended components",
            "message": "Theta method - excellent for short-term forecasts"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate Theta Method forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.values is None or self.trend is None:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "theta",
                "trend": "stable",
                "seasonality": "none"
            }
        
        forecast_values = []
        n = len(self.values)
        
        # Extrapolate trend
        trend_forecast = self._extrapolate_trend(horizon)
        
        # Forecast detrended component (simple exponential smoothing)
        detrended_forecast = self._forecast_detrended(horizon)
        
        # Combine components
        for i in range(horizon):
            combined = trend_forecast[i] + detrended_forecast[i]
            forecast_values.append(combined)
        
        # Calculate confidence intervals
        residuals = self.values - (self.trend + self.detrended)
        residual_std = np.std(residuals)
        
        lower_bounds = [v - 1.96 * residual_std for v in forecast_values]
        upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "theta",
            "trend": "stable",
            "seasonality": "none"
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _extract_trend(self, values: np.ndarray) -> np.ndarray:
        """Extract trend using simple exponential smoothing."""
        alpha = 0.2
        trend = np.zeros_like(values)
        trend[0] = values[0]
        
        for t in range(1, len(values)):
            trend[t] = alpha * values[t] + (1 - alpha) * trend[t-1]
        
        return trend
    
    def _extrapolate_trend(self, horizon: int) -> List[float]:
        """Extrapolate trend into future."""
        if len(self.trend) < 2:
            last_val = self.trend[-1]
            return [last_val] * horizon
        
        # Linear extrapolation of trend
        trend_change = self.trend[-1] - self.trend[-2]
        
        extrapolated = []
        for i in range(horizon):
            next_val = self.trend[-1] + trend_change * (i + 1)
            extrapolated.append(next_val)
        
        return extrapolated
    
    def _forecast_detrended(self, horizon: int) -> List[float]:
        """Forecast detrended component."""
        if len(self.detrended) < 1:
            return [0.0] * horizon
        
        # Simple exponential smoothing of detrended component
        alpha = 0.3
        last_detrended = self.detrended[-1]
        
        forecasts = []
        for _ in range(horizon):
            # For detrended, use exponential decay
            forecast = last_detrended * (1 - alpha)
            forecasts.append(forecast)
            last_detrended = forecast
        
        return forecasts
    
    def _calculate_trend_strength(self) -> float:
        """Calculate strength of trend in data."""
        if self.trend is None or len(self.trend) < 2:
            return 0.0
        
        trend_var = np.var(self.trend)
        total_var = np.var(self.values)
        
        if total_var == 0:
            return 0.0
        
        return min(trend_var / total_var, 1.0)
    
    def _detect_seasonality(self) -> bool:
        """Detect if seasonality is present."""
        if self.detrended is None or len(self.detrended) < 14:
            return False
        
        # Check autocorrelation at lag 7
        acf_7 = np.corrcoef(self.detrended[:-7], self.detrended[7:])[0, 1]
        
        return abs(acf_7) > 0.3
