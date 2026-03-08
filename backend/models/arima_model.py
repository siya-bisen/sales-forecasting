"""
ARIMA forecasting model.
Good for stationary and trend-based time series.
Auto-detects p, d, q parameters using grid search.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
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
        self.aic_score = None
    
    def _find_d(self, series: pd.Series) -> int:
        """
        Find differencing order (d) using ADF test.
        Tests up to d=2 for robustness.
        
        Args:
            series: Time series data
            
        Returns:
            Differencing order (0, 1, or 2)
        """
        try:
            # Test original series
            result = adfuller(series, autolag='AIC', maxlag=5)
            if result[1] < 0.05:
                self.is_stationary = True
                return 0
            
            # Test first difference
            diff1 = series.diff().dropna()
            if len(diff1) < 2:
                return 1
            
            result = adfuller(diff1, autolag='AIC', maxlag=5)
            if result[1] < 0.05:
                return 1
            
            # Test second difference
            diff2 = diff1.diff().dropna()
            if len(diff2) < 2:
                return 1
            
            return 2
        except Exception:
            return 1
    
    def _find_order(self, series: pd.Series) -> tuple:
        """
        Auto-find ARIMA order (p, d, q) using grid search with AIC.
        
        Args:
            series: Time series data
            
        Returns:
            ARIMA order tuple (p, d, q)
        """
        n = len(series)
        
        # Find d (differencing)
        d = self._find_d(series)
        
        # Determine p and q ranges based on data length
        if n < 20:
            p_range = range(0, 3)
            q_range = range(0, 3)
        elif n < 50:
            p_range = range(0, 4)
            q_range = range(0, 4)
        else:
            p_range = range(0, 6)
            q_range = range(0, 6)
        
        best_order = (1, d, 1)
        best_aic = float('inf')
        
        try:
            for p in p_range:
                for q in q_range:
                    try:
                        model = ARIMA(
                            series,
                            order=(p, d, q),
                            enforce_stationarity=False,
                            enforce_invertibility=False
                        )
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except Exception:
                        continue
        except Exception:
            pass
        
        self.aic_score = best_aic
        return best_order
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit ARIMA model to historical data with robust error handling.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 2:
            raise ValueError("Need at least 2 data points for ARIMA")
        
        # Remove any NaN or infinite values
        values = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        
        if len(values) < 2:
            raise ValueError("Not enough valid data points for ARIMA")
        
        # Convert to pandas Series with datetime index
        df = pd.DataFrame({
            'date': pd.to_datetime(dates[-len(values):]),
            'value': values
        })
        df.set_index('date', inplace=True)
        series = df['value']
        
        try:
            # Auto-find order with grid search
            self.order = self._find_order(series)
            
            # Fit ARIMA model with robust settings
            self.model = ARIMA(
                series,
                order=self.order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.model = self.model.fit(disp=False)
            self.fitted = True
        except Exception as e:
            # Fallback sequence: try progressively simpler orders
            fallback_orders = [(1, 0, 1), (1, 1, 0), (0, 1, 1), (1, 1, 1), (0, 0, 1)]
            
            for fallback_order in fallback_orders:
                try:
                    self.order = fallback_order
                    self.model = ARIMA(
                        series,
                        order=self.order,
                        enforce_stationarity=False,
                        enforce_invertibility=False
                    )
                    self.model = self.model.fit(disp=False)
                    self.fitted = True
                    return
                except Exception:
                    continue
            
            raise ValueError(f"Failed to fit ARIMA model with all fallback options: {str(e)}")
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast for specified horizon with robust bounds.
        
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
            # Get forecast with confidence intervals
            forecast_result = self.model.get_forecast(steps=horizon)
            forecast_values = forecast_result.predicted_mean.tolist()
            
            # Get confidence intervals
            try:
                ci = forecast_result.conf_int(alpha=0.05)
                lower_bounds = ci.iloc[:, 0].tolist()
                upper_bounds = ci.iloc[:, 1].tolist()
            except Exception:
                # Fallback: use standard error for bounds
                std_error = np.std([forecast_values[0] if forecast_values else 1])
                lower_bounds = [max(0, v - 1.96 * std_error) for v in forecast_values]
                upper_bounds = [v + 1.96 * std_error for v in forecast_values]
            
            # Ensure values are non-negative (for sales forecasting)
            forecast_values = [max(0, v) for v in forecast_values]
            lower_bounds = [max(0, v) for v in lower_bounds]
            upper_bounds = [max(0, v) for v in upper_bounds]
            
            # Ensure lower <= forecast <= upper
            for i in range(len(forecast_values)):
                lower_bounds[i] = min(lower_bounds[i], forecast_values[i])
                upper_bounds[i] = max(upper_bounds[i], forecast_values[i])
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "arima",
                "order": str(self.order),
                "is_stationary": self.is_stationary,
                "aic_score": float(self.aic_score) if self.aic_score else None
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "arima",
            "order": str(self.order) if self.order else "unknown",
            "is_stationary": self.is_stationary,
            "description": f"ARIMA{self.order if self.order else '(p,d,q)'} - Autoregressive Integrated Moving Average model"
        }
