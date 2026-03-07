"""
Seasonal Naive Forecasting Model
Simple yet effective baseline for seasonal data.
Repeats values from same season in previous period.
"""
import numpy as np
from typing import List, Dict, Any, Tuple


class SeasonalNaiveModel:
    """
    Seasonal Naive forecasting model.
    Repeats values from same season in previous year/period.
    Excellent baseline for seasonal data.
    
    Features:
    - Automatic seasonal period detection (7 for weekly, 365 for yearly)
    - Simple and interpretable
    - No parameters to tune
    - Fast computation
    - Good for highly seasonal data
    """
    
    def __init__(self, seasonal_period: int = 7):
        """
        Initialize Seasonal Naive model.
        
        Args:
            seasonal_period: Number of periods in a season (default 7 for weekly)
        """
        self.seasonal_period = seasonal_period
        self.values = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Seasonal Naive model (no actual fitting needed).
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < self.seasonal_period:
            self.metadata = {
                "status": "insufficient_data",
                "message": f"Need at least {self.seasonal_period} data points"
            }
            return
        
        self.values = values_array
        
        # Detect seasonality strength
        seasonality_score = self._calculate_seasonality_strength()
        
        # Auto-detect seasonal period if needed
        self._detect_seasonal_period()
        
        self.metadata = {
            "type": "Seasonal Naive",
            "seasonal_period": self.seasonal_period,
            "data_points_used": len(values_array),
            "seasonality_strength": round(seasonality_score, 3),
            "interpretation": f"Repeats pattern from {self.seasonal_period} periods ago",
            "message": "Simple seasonal baseline - excellent for highly seasonal data"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate seasonal naive forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.values is None or len(self.values) < self.seasonal_period:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "seasonal_naive",
                "trend": "stable",
                "seasonality": "detected"
            }
        
        forecast_values = []
        n = len(self.values)
        
        # Repeat values from same season
        for i in range(horizon):
            idx = (n - self.seasonal_period + (i % self.seasonal_period)) % n
            forecast_values.append(self.values[idx])
        
        # Calculate seasonal standard deviation for bounds
        seasonal_std = self._calculate_seasonal_std()
        
        lower_bounds = [v - 1.96 * seasonal_std for v in forecast_values]
        upper_bounds = [v + 1.96 * seasonal_std for v in forecast_values]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "seasonal_naive",
            "trend": "stable",
            "seasonality": "detected"
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _calculate_seasonality_strength(self) -> float:
        """Calculate strength of seasonality in data."""
        if self.values is None or len(self.values) < self.seasonal_period * 2:
            return 0.0
        
        seasonal_components = []
        for i in range(self.seasonal_period):
            seasonal_values = self.values[i::self.seasonal_period]
            if len(seasonal_values) > 1:
                seasonal_components.append(np.std(seasonal_values))
        
        if not seasonal_components:
            return 0.0
        
        avg_seasonal_std = np.mean(seasonal_components)
        overall_std = np.std(self.values)
        
        if overall_std == 0:
            return 0.0
        
        # Strength = 1 - (variance of remainder / variance of data)
        return min(avg_seasonal_std / overall_std, 1.0)
    
    def _detect_seasonal_period(self) -> None:
        """Auto-detect seasonal period if not provided."""
        if self.values is None or len(self.values) < 14:
            return
        
        # Try common periods
        for period in [7, 14, 30, 365]:
            if len(self.values) >= period * 2:
                strength = self._strength_for_period(period)
                if strength > 0.3:
                    self.seasonal_period = period
                    break
    
    def _strength_for_period(self, period: int) -> float:
        """Calculate seasonality strength for a specific period."""
        if len(self.values) < period * 2:
            return 0.0
        
        seasonal_values = []
        for i in range(period):
            vals = self.values[i::period]
            if len(vals) > 1:
                seasonal_values.append(np.std(vals))
        
        if not seasonal_values:
            return 0.0
        
        return np.mean(seasonal_values) / (np.std(self.values) + 1e-8)
    
    def _calculate_seasonal_std(self) -> float:
        """Calculate standard deviation within seasonal components."""
        if self.values is None or len(self.values) < self.seasonal_period:
            return np.std(self.values)
        
        seasonal_stds = []
        for i in range(self.seasonal_period):
            seasonal_values = self.values[i::self.seasonal_period]
            if len(seasonal_values) > 0:
                seasonal_stds.append(np.std(seasonal_values))
        
        return np.mean(seasonal_stds) if seasonal_stds else np.std(self.values)
