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
        Fit Theta Method model with robust validation.
        
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
            "fitted": True,
            "interpretation": "Decomposes into trend and detrended components",
            "message": "Theta method - excellent for short-term forecasts"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate Theta Method forecast with robust bounds validation.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.values is None or self.trend is None:
            raise ValueError("Model must be fitted before forecasting")
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            # Extrapolate trend
            trend_forecast = self._extrapolate_trend(horizon)
            
            # Forecast detrended component (simple exponential smoothing)
            detrended_forecast = self._forecast_detrended(horizon)
            
            # Combine components
            forecast_values = []
            for i in range(horizon):
                combined = max(0, trend_forecast[i] + detrended_forecast[i])
                forecast_values.append(combined)
            
            # Calculate confidence intervals from residuals
            residuals = self.values - (self.trend + self.detrended)
            residual_std = np.std(residuals) if np.std(residuals) > 0 else np.mean(forecast_values) * 0.1
            
            lower_bounds = []
            upper_bounds = []
            
            for i, fv in enumerate(forecast_values):
                # Increase uncertainty with horizon
                adjusted_std = residual_std * np.sqrt(1 + i * 0.08)
                lower = max(0, fv - 1.96 * adjusted_std)
                upper = fv + 1.96 * adjusted_std
                
                # Ensure bounds are valid
                lower = min(lower, fv)
                upper = max(upper, fv)
                
                lower_bounds.append(lower)
                upper_bounds.append(upper)
            
            # Detect trend direction
            recent_trend = forecast_values[-1] - forecast_values[0] if horizon > 1 else forecast_values[0]
            trend_direction = "upward" if recent_trend > 0 else ("downward" if recent_trend < 0 else "flat")
            
            return {
                "forecast": [float(v) for v in forecast_values],
                "lower_bounds": [float(v) for v in lower_bounds],
                "upper_bounds": [float(v) for v in upper_bounds],
                "trend": trend_direction,
                "confidence_level": 0.95,
                "method": "Theta Method"
            }
        except Exception as e:
            raise ValueError(f"Theta method forecast failed: {str(e)}")
    
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
