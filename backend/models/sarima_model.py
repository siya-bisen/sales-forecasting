"""
SARIMA forecasting model.
Good for time series with trends and seasonality.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')


class SARIMAModel:
    """SARIMA (Seasonal ARIMA) forecasting model."""
    
    def __init__(self, order: tuple = (1, 1, 1), seasonal_order: tuple = (1, 1, 1, 7)):
        """
        Initialize SARIMA model.
        
        Args:
            order: (p, d, q) for ARIMA
            seasonal_order: (P, D, Q, s) for seasonal component
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted = False
        self.fitted_model = None
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit SARIMA model to historical data.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Convert to pandas Series with datetime index
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'value': values
        })
        df.set_index('date', inplace=True)
        series = df['value']
        
        # Auto-select parameters if data is limited
        if len(series) < 30:
            # Use simpler model for small datasets
            self.order = (1, 0, 1)
            self.seasonal_order = (0, 0, 0, 0)
        elif len(series) < 60:
            # No seasonality for medium datasets
            self.seasonal_order = (0, 0, 0, 0)
        
        try:
            # Fit SARIMA model
            self.fitted_model = SARIMAX(
                series,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.model = self.fitted_model.fit(disp=False, maxiter=50)
            self.fitted = True
        except Exception as e:
            # Fallback to simpler model on error
            try:
                self.order = (1, 0, 1)
                self.seasonal_order = (0, 0, 0, 0)
                self.fitted_model = SARIMAX(
                    series,
                    order=self.order,
                    seasonal_order=self.seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                self.model = self.fitted_model.fit(disp=False, maxiter=50)
                self.fitted = True
            except:
                raise ValueError(f"Failed to fit SARIMA model: {str(e)}")
    
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
        
        # Generate forecast with confidence intervals
        forecast_result = self.model.get_forecast(steps=horizon)
        forecast_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        
        return {
            "forecast": forecast_mean.tolist(),
            "lower": conf_int.iloc[:, 0].tolist(),
            "upper": conf_int.iloc[:, 1].tolist(),
            "model_name": "sarima",
            "order": self.order,
            "seasonal_order": self.seasonal_order
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "sarima",
            "fitted": self.fitted,
            "order": self.order,
            "seasonal_order": self.seasonal_order
        }
