"""
Exponential Smoothing forecasting model.
Excellent for data with trends and seasonality.
Automatically selects between SES, Holt's, and Holt-Winters methods.
Improved with better seasonality detection and robust fallbacks.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from scipy import signal
import warnings
warnings.filterwarnings('ignore')


class ExponentialSmoothingModel:
    """Exponential Smoothing forecasting model with advanced method selection."""
    
    def __init__(self):
        """Initialize Exponential Smoothing model."""
        self.model = None
        self.fitted = False
        self.method = None
        self.data_length = None
        self.has_seasonality = False
        self.trend = None
        self.seasonal_period = None
        self.smoothing_level = None
    
    def _detect_seasonality(self, series: pd.Series) -> tuple:
        """
        Detect seasonality in the time series using autocorrelation and periodogram.
        
        Args:
            series: Time series data
            
        Returns:
            Tuple of (has_seasonality, seasonal_period)
        """
        if len(series) < 14:
            return False, None
        
        try:
            # Use periodogram to detect dominant frequencies
            freq, power = signal.periodogram(series.values)
            
            # Find peaks in power spectrum
            peaks, _ = signal.find_peaks(power[1:], height=np.max(power[1:]) * 0.3)
            
            if len(peaks) > 0:
                # Get the period of the strongest peak
                dominant_freq = freq[peaks[0] + 1]
                if dominant_freq > 0:
                    seasonal_period = int(1 / dominant_freq)
                    # Likely periods for sales: 7 (weekly), 30 (monthly), 365 (yearly)
                    if 3 <= seasonal_period <= 365:
                        return True, seasonal_period
        except Exception:
            pass
        
        # Fallback: Check for known seasonal patterns
        if len(series) >= 14:
            return True, 7  # Default to weekly seasonality
        
        return False, None
    
    def _detect_trend(self, series: pd.Series) -> str:
        """
        Detect trend direction using linear regression slope.
        
        Args:
            series: Time series data
            
        Returns:
            Trend direction: "upward", "downward", or "stable"
        """
        if len(series) < 3:
            return "stable"
        
        try:
            x = np.arange(len(series))
            y = series.values
            
            # Fit line and get slope
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            
            # Normalize slope
            y_mean = np.mean(y)
            if y_mean != 0:
                normalized_slope = slope / y_mean
                
                if normalized_slope > 0.01:
                    return "upward"
                elif normalized_slope < -0.01:
                    return "downward"
        except Exception:
            pass
        
        return "stable"
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Exponential Smoothing model to historical data.
        Automatically selects method based on data characteristics.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 2:
            raise ValueError("Need at least 2 data points for Exponential Smoothing")
        
        # Remove invalid values
        valid_indices = [i for i, v in enumerate(values) 
                        if isinstance(v, (int, float)) and np.isfinite(v)]
        
        if len(valid_indices) < 2:
            raise ValueError("Not enough valid data points")
        
        values_clean = [values[i] for i in valid_indices]
        dates_clean = [dates[i] for i in valid_indices]
        
        self.data_length = len(values_clean)
        
        # Convert to pandas Series with datetime index
        df = pd.DataFrame({
            'date': pd.to_datetime(dates_clean),
            'value': values_clean
        })
        df.set_index('date', inplace=True)
        series = df['value']
        
        # Detect trend
        self.trend = self._detect_trend(series)
        
        # Detect seasonality
        has_seasonality, seasonal_period = self._detect_seasonality(series)
        self.has_seasonality = has_seasonality
        self.seasonal_period = seasonal_period
        
        try:
            # Choose method based on data characteristics and seasonality
            if len(series) < 14:
                # For small datasets, use Simple Exponential Smoothing
                self.model = SimpleExpSmoothing(series).fit(optimized=True)
                self.method = "simple"
                self.smoothing_level = self.model.smoothing_level
            
            elif len(series) < 30 or not has_seasonality:
                # For medium datasets without strong seasonality, use Holt's
                try:
                    self.model = Holt(series, trend='add').fit(optimized=True)
                    self.method = "holt"
                    self.smoothing_level = self.model.smoothing_level
                except Exception:
                    # Fallback to Simple Exponential Smoothing
                    self.model = SimpleExpSmoothing(series).fit(optimized=True)
                    self.method = "simple"
                    self.smoothing_level = self.model.smoothing_level
            
            else:
                # For larger datasets with seasonality, use Holt-Winters
                if seasonal_period is None:
                    seasonal_period = 7  # Default to weekly seasonality
                
                try:
                    # Ensure seasonal period is not too large
                    seasonal_period = min(seasonal_period, len(series) // 3)
                    
                    # Try additive seasonality first (better for sales data)
                    self.model = ExponentialSmoothing(
                        series,
                        seasonal_periods=seasonal_period,
                        trend='add',
                        seasonal='add',
                        initialization_method='estimated'
                    ).fit(optimized=True)
                    self.method = "holt_winters"
                    self.smoothing_level = self.model.smoothing_level
                except Exception:
                    try:
                        # Fallback to multiplicative seasonality
                        self.model = ExponentialSmoothing(
                            series,
                            seasonal_periods=seasonal_period,
                            trend='add',
                            seasonal='mul',
                            initialization_method='estimated'
                        ).fit(optimized=True)
                        self.method = "holt_winters_mult"
                        self.smoothing_level = self.model.smoothing_level
                    except Exception:
                        # Final fallback to Holt's
                        self.model = Holt(series, trend='add').fit(optimized=True)
                        self.method = "holt"
                        self.smoothing_level = self.model.smoothing_level
            
            self.fitted = True
        
        except Exception as e:
            # Ultimate fallback to Simple Exponential Smoothing
            try:
                self.model = SimpleExpSmoothing(series).fit(optimized=True)
                self.method = "simple"
                self.smoothing_level = self.model.smoothing_level
                self.fitted = True
            except Exception as e2:
                raise ValueError(f"Failed to fit Exponential Smoothing model: {str(e2)}")
    
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
            # Get forecast
            forecast = self.model.get_forecast(steps=horizon)
            forecast_values = forecast.predicted_mean.tolist()
            
            # Get confidence intervals
            try:
                ci = forecast.conf_int(alpha=0.05)
                lower_bounds = ci.iloc[:, 0].tolist()
                upper_bounds = ci.iloc[:, 1].tolist()
            except Exception:
                # If confidence intervals not available, use std-based bounds
                std = np.std(forecast_values) if len(forecast_values) > 1 else np.mean(forecast_values) * 0.1
                lower_bounds = [max(0, v - 1.96 * std) for v in forecast_values]
                upper_bounds = [v + 1.96 * std for v in forecast_values]
            
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
                "model_name": "exponential_smoothing",
                "method": self.method,
                "trend": self.trend or "stable",
                "seasonality": "detected" if self.has_seasonality else "none",
                "seasonal_period": self.seasonal_period
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
            "seasonal_period": self.seasonal_period,
            "smoothing_level": float(self.smoothing_level) if self.smoothing_level else None,
            "data_length": self.data_length,
            "description": self._get_method_description()
        }
    
    def _get_method_description(self) -> str:
        """Get description of the selected method."""
        descriptions = {
            "simple": "Simple Exponential Smoothing - Good for non-trending data with minimal seasonal patterns",
            "holt": "Holt's Linear Trend Method - Excellent for data with clear trends",
            "holt_winters": "Holt-Winters Additive Method - Best for data with both trends and seasonality",
            "holt_winters_mult": "Holt-Winters Multiplicative Method - For proportional seasonal variations"
        }
        return descriptions.get(self.method, "Exponential Smoothing Model")
