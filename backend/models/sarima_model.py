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
        Fit SARIMA model to historical data with robust error handling.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 3:
            raise ValueError(f"Need at least 3 data points for SARIMA (have {len(values) if values else 0})")
        
        # Clean invalid values
        values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        if len(values_clean) < 3:
            raise ValueError("Not enough valid data points for SARIMA")
        
        # Convert to pandas Series with datetime index
        df = pd.DataFrame({
            'date': pd.to_datetime(dates[-len(values_clean):]),
            'value': values_clean
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
        Generate forecast for specified horizon with robust bounds validation.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if not self.fitted or self.model is None:
            raise ValueError("Model must be fitted before forecasting")
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            # Generate forecast with confidence intervals
            forecast_result = self.model.get_forecast(steps=horizon)
            forecast_mean = forecast_result.predicted_mean
            
            # Apply non-negative constraint
            forecast_values = [max(0, float(v)) for v in forecast_mean.tolist()]
            
            # Get confidence intervals
            try:
                conf_int = forecast_result.conf_int(alpha=0.05)
                lower_bounds = [max(0, float(v)) for v in conf_int.iloc[:, 0].tolist()]
                upper_bounds = [float(v) for v in conf_int.iloc[:, 1].tolist()]
            except Exception:
                # Fallback: use residual-based confidence intervals
                residuals = self.model.resid
                std_error = np.std(residuals) if np.std(residuals) > 0 else np.mean(forecast_values) * 0.1
                
                lower_bounds = [max(0, v - 1.96 * std_error) for v in forecast_values]
                upper_bounds = [v + 1.96 * std_error for v in forecast_values]
            
            # Validate bounds
            for i in range(len(forecast_values)):
                lower_bounds[i] = min(lower_bounds[i], forecast_values[i])
                upper_bounds[i] = max(upper_bounds[i], forecast_values[i])
            
            # Detect trend direction
            recent_trend = forecast_values[-1] - forecast_values[0] if horizon > 1 else forecast_values[0]
            trend_direction = "upward" if recent_trend > 0 else ("downward" if recent_trend < 0 else "flat")
            
            return {
                "forecast": [float(v) for v in forecast_values],
                "lower_bounds": [float(v) for v in lower_bounds],
                "upper_bounds": [float(v) for v in upper_bounds],
                "trend": trend_direction,
                "order": self.order,
                "seasonal_order": self.seasonal_order,
                "confidence_level": 0.95,
                "method": "SARIMA"
            }
        except Exception as e:
            raise ValueError(f"SARIMA forecast failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "sarima",
            "fitted": self.fitted,
            "order": self.order,
            "seasonal_order": self.seasonal_order
        }
