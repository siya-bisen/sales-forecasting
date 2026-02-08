"""
Prophet forecasting model.
Handles seasonality and trends well.
"""
from typing import List, Dict, Any
import pandas as pd
from prophet import Prophet
import numpy as np


class ProphetModel:
    """Facebook Prophet forecasting model."""
    
    def __init__(self):
        """Initialize Prophet model."""
        self.model = None
        self.fitted = False
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Prophet model to historical data.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        df = pd.DataFrame({
            'ds': pd.to_datetime(dates),
            'y': values
        })
        
        # Initialize and fit Prophet
        # Enable weekly and yearly seasonality if enough data
        self.model = Prophet(
            yearly_seasonality=len(df) > 365,
            weekly_seasonality=len(df) > 14,
            daily_seasonality=False,
            interval_width=0.95  # 95% confidence intervals
        )
        
        self.model.fit(df)
        self.fitted = True
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast for specified horizon.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if not self.fitted or self.model is None:
            raise ValueError("Model must be fitted before forecasting")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=horizon)
        
        # Generate forecast
        forecast_df = self.model.predict(future)
        
        # Extract only the forecasted period (last horizon rows)
        forecast_period = forecast_df.tail(horizon)
        
        return {
            "forecast": forecast_period['yhat'].tolist(),
            "lower": forecast_period['yhat_lower'].tolist(),
            "upper": forecast_period['yhat_upper'].tolist(),
            "model_name": "prophet",
            "trend": self._detect_trend(forecast_period),
            "seasonality": self._detect_seasonality()
        }
    
    def _detect_trend(self, forecast_df: pd.DataFrame) -> str:
        """Detect trend direction from forecast."""
        if len(forecast_df) < 2:
            return "stable"
        
        first_half = forecast_df['yhat'].iloc[:len(forecast_df)//2].mean()
        second_half = forecast_df['yhat'].iloc[len(forecast_df)//2:].mean()
        
        change_pct = (second_half - first_half) / first_half if first_half > 0 else 0
        
        if change_pct > 0.05:
            return "upward"
        elif change_pct < -0.05:
            return "downward"
        else:
            return "stable"
    
    def _detect_seasonality(self) -> str:
        """Detect seasonality type."""
        if self.model is None:
            return "none"
        
        # Check model components for seasonality
        try:
            seasonalities = self.model.seasonalities
            if 'weekly' in seasonalities:
                return "weekly"
            elif 'yearly' in seasonalities:
                return "yearly"
        except AttributeError:
            # Fallback for different Prophet versions
            if hasattr(self.model, 'weekly_seasonality') and self.model.weekly_seasonality:
                return "weekly"
            elif hasattr(self.model, 'yearly_seasonality') and self.model.yearly_seasonality:
                return "yearly"
        
        return "none"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "prophet",
            "fitted": self.fitted,
            "seasonality": self._detect_seasonality() if self.fitted else None
        }
