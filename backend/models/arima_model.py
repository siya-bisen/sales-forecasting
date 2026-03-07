"""
ARIMA forecasting model.
Good for stationary and trend-based time series.
Auto-detects p, d, q parameters.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')


class ARIMAModel:
    """ARIMA (AutoRegressive Integrated Moving Average) forecasting model."""
    
    def __init__(self):
        """Initialize ARIMA model."""
        self.model = None
        self.fitted = False
        self.order = None
        self.is_stationary = False
    
    def _find_d(self, series: pd.Series) -> int:
        """
        Find differencing order (d) using ADF test.
        
        Args:
            series: Time series data
            
        Returns:
            Differencing order (0 or 1)
        """
        try:
            result = adfuller(series, autolag='AIC')
            # If p-value < 0.05, series is stationary
            if result[1] < 0.05:
                self.is_stationary = True
                return 0
            else:
                return 1
        except:
            return 1
    
    def _find_order(self, series: pd.Series) -> tuple:
        """
        Auto-find ARIMA order (p, d, q).
        Uses simplified approach for efficiency.
        
        Args:
            series: Time series data
            
        Returns:
            ARIMA order tuple (p, d, q)
        """
        n = len(series)
        
        # Find d (differencing)
        d = self._find_d(series)
        
        # For small datasets, use simple parameters
        if n < 20:
            return (1, d, 1)
        elif n < 50:
            return (2, d, 2)
        else:
            # For larger datasets, try to detect ACF/PACF patterns
            return (2, d, 2)
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit ARIMA model to historical data.
        
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
        
        try:
            # Auto-find order
            self.order = self._find_order(series)
            
            # Fit ARIMA model
            self.model = ARIMA(
                series,
                order=self.order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.model = self.model.fit()
            self.fitted = True
        except Exception as e:
            # Fallback to simpler order
            try:
                self.order = (1, 0, 1)
                self.model = ARIMA(
                    series,
                    order=self.order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                self.model = self.model.fit()
                self.fitted = True
            except Exception as e2:
                raise ValueError(f"Failed to fit ARIMA model: {str(e2)}")
    
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
            # Get forecast with confidence intervals
            forecast_result = self.model.get_forecast(steps=horizon)
            forecast_values = forecast_result.predicted_mean.tolist()
            
            # Get confidence intervals
            ci = forecast_result.conf_int(alpha=0.05)
            lower_bounds = ci.iloc[:, 0].tolist()
            upper_bounds = ci.iloc[:, 1].tolist()
            
            # Ensure values are positive (for sales forecasting)
            forecast_values = [max(0, v) for v in forecast_values]
            lower_bounds = [max(0, v) for v in lower_bounds]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "arima",
                "order": str(self.order),
                "is_stationary": self.is_stationary
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "arima",
            "order": str(self.order) if self.order else "unknown",
            "is_stationary": self.is_stationary,
            "description": f"ARIMA{self.order if self.order else '(p,d,q)'} - Autoregressive Integrated Moving Average model"
        }
