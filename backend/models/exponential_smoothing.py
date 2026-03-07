"""
Exponential Smoothing forecasting model.
Excellent for data with trends and seasonality.
Automatically selects between SES, Holt's, and Holt-Winters methods.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
import warnings
warnings.filterwarnings('ignore')


class ExponentialSmoothingModel:
    """Exponential Smoothing forecasting model with automatic method selection."""
    
    def __init__(self):
        """Initialize Exponential Smoothing model."""
        self.model = None
        self.fitted = False
        self.method = None
        self.data_length = None
        self.has_seasonality = False
        self.trend = None
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Exponential Smoothing model to historical data.
        Automatically selects method based on data characteristics.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        self.data_length = len(values)
        
        # Convert to pandas Series with datetime index
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'value': values
        })
        df.set_index('date', inplace=True)
        series = df['value']
        
        # Detect trend
        if len(series) > 2:
            first_half_mean = np.mean(series[:len(series)//2])
            second_half_mean = np.mean(series[len(series)//2:])
            if second_half_mean > first_half_mean * 1.05:
                self.trend = "upward"
            elif second_half_mean < first_half_mean * 0.95:
                self.trend = "downward"
            else:
                self.trend = "stable"
        
        try:
            # Choose method based on data characteristics
            if len(series) < 14:
                # For small datasets, use Simple Exponential Smoothing
                self.model = SimpleExpSmoothing(series).fit(optimized=True)
                self.method = "simple"
            elif len(series) < 30:
                # For medium datasets without seasonality, use Holt's
                self.model = Holt(series, trend='add').fit()
                self.method = "holt"
            else:
                # For larger datasets with potential seasonality
                seasonal_period = 7  # Weekly seasonality for sales data
                try:
                    # Try Holt-Winters with additive seasonality
                    self.model = ExponentialSmoothing(
                        series,
                        seasonal_periods=seasonal_period,
                        trend='add',
                        seasonal='add',
                        initialization_method='estimated'
                    ).fit(optimized=True)
                    self.method = "holt_winters"
                    self.has_seasonality = True
                except:
                    # Fallback to Holt's if Holt-Winters fails
                    self.model = Holt(series, trend='add').fit()
                    self.method = "holt"
            
            self.fitted = True
        except Exception as e:
            # Fallback to Simple Exponential Smoothing
            try:
                self.model = SimpleExpSmoothing(series).fit(optimized=True)
                self.method = "simple"
                self.fitted = True
            except Exception as e2:
                raise ValueError(f"Failed to fit Exponential Smoothing model: {str(e2)}")
    
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
        
        try:
            # Get forecast
            forecast = self.model.get_forecast(steps=horizon)
            forecast_values = forecast.predicted_mean.tolist()
            
            # Get confidence intervals
            try:
                ci = forecast.conf_int(alpha=0.05)
                lower_bounds = ci.iloc[:, 0].tolist()
                upper_bounds = ci.iloc[:, 1].tolist()
            except:
                # If confidence intervals not available, use std-based bounds
                std = np.std(forecast_values) if len(forecast_values) > 1 else np.mean(forecast_values) * 0.1
                lower_bounds = [max(0, v - 1.96 * std) for v in forecast_values]
                upper_bounds = [v + 1.96 * std for v in forecast_values]
            
            # Ensure values are positive (for sales forecasting)
            forecast_values = [max(0, v) for v in forecast_values]
            lower_bounds = [max(0, v) for v in lower_bounds]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "exponential_smoothing",
                "method": self.method,
                "trend": self.trend or "stable",
                "seasonality": "detected" if self.has_seasonality else "none"
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "exponential_smoothing",
            "method": self.method,
            "trend": self.trend or "stable",
            "seasonality": "detected" if self.has_seasonality else "none",
            "description": self._get_method_description()
        }
    
    def _get_method_description(self) -> str:
        """Get description of the selected method."""
        descriptions = {
            "simple": "Simple Exponential Smoothing - Good for non-trending data with minimal seasonal patterns",
            "holt": "Holt's Linear Trend Method - Excellent for data with clear trends",
            "holt_winters": "Holt-Winters Method - Best for data with both trends and seasonality"
        }
        return descriptions.get(self.method, "Exponential Smoothing Model")
