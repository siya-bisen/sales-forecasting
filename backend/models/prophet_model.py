"""
Prophet forecasting model.
Handles seasonality, trends, and changepoints well.
Improved with automatic seasonality detection and parameter tuning.
"""
from typing import List, Dict, Any
import pandas as pd
from prophet import Prophet
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class ProphetModel:
    """Facebook Prophet forecasting model with enhanced configuration."""
    
    def __init__(self):
        """Initialize Prophet model."""
        self.model = None
        self.fitted = False
        self.has_weekly_seasonality = False
        self.has_yearly_seasonality = False
        self.trend_type = "linear"
        self.n_changepoints = 0
    
    def _detect_seasonality(self, dates: List[str], values: List[float]) -> tuple:
        """
        Detect seasonality patterns in the data.
        
        Args:
            dates: List of date strings
            values: List of sales values
            
        Returns:
            Tuple of (has_weekly, has_yearly, n_changepoints)
        """
        n = len(values)
        
        # Need at least 14 days for weekly and 365 for yearly
        has_weekly = n >= 14
        has_yearly = n >= 365
        
        # Estimate number of changepoints (5-25% of data length)
        n_changepoints = max(0, min(25, int(n * 0.15)))
        
        if n < 14:
            n_changepoints = 0
        elif n < 30:
            n_changepoints = min(3, n_changepoints)
        
        return has_weekly, has_yearly, n_changepoints
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Prophet model to historical data with robust settings.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 2:
            raise ValueError("Need at least 2 data points for Prophet")
        
        # Remove any NaN or infinite values
        valid_indices = [i for i, v in enumerate(values) 
                        if isinstance(v, (int, float)) and np.isfinite(v)]
        
        if len(valid_indices) < 2:
            raise ValueError("Not enough valid data points for Prophet")
        
        values_clean = [values[i] for i in valid_indices]
        dates_clean = [dates[i] for i in valid_indices]
        
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        df = pd.DataFrame({
            'ds': pd.to_datetime(dates_clean),
            'y': values_clean
        })
        
        try:
            # Detect seasonality patterns
            has_weekly, has_yearly, n_changepoints = self._detect_seasonality(dates_clean, values_clean)
            self.has_weekly_seasonality = has_weekly
            self.has_yearly_seasonality = has_yearly
            self.n_changepoints = n_changepoints
            
            # Initialize Prophet with optimized parameters
            self.model = Prophet(
                yearly_seasonality=has_yearly,
                weekly_seasonality=has_weekly,
                daily_seasonality=False,
                interval_width=0.95,  # 95% confidence intervals
                changepoint_prior_scale=0.05,  # Smoother changepoints
                seasonality_prior_scale=10,  # Stronger seasonality detection
                seasonality_mode='additive',  # Better for sales data
                n_changepoints=n_changepoints
            )
            
            self.model.fit(df, verbose=False)
            self.fitted = True
        except Exception as e:
            raise ValueError(f"Failed to fit Prophet model: {str(e)}")
    
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
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=horizon)
            
            # Generate forecast
            forecast_df = self.model.predict(future)
            
            # Extract only the forecasted period (last horizon rows)
            forecast_period = forecast_df.tail(horizon)
            
            # Get forecast values and bounds
            forecast_values = forecast_period['yhat'].tolist()
            lower_bounds = forecast_period['yhat_lower'].tolist()
            upper_bounds = forecast_period['yhat_upper'].tolist()
            
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
                "model_name": "prophet",
                "trend": self._detect_trend(forecast_period),
                "seasonality": self._detect_seasonality_type(),
                "has_weekly": self.has_weekly_seasonality,
                "has_yearly": self.has_yearly_seasonality
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
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
    
    def _detect_seasonality_type(self) -> str:
        """Detect seasonality type."""
        if self.has_yearly_seasonality:
            return "yearly"
        elif self.has_weekly_seasonality:
            return "weekly"
        return "none"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "prophet",
            "fitted": self.fitted,
            "seasonality": self._detect_seasonality_type() if self.fitted else None,
            "has_weekly": self.has_weekly_seasonality,
            "has_yearly": self.has_yearly_seasonality,
            "n_changepoints": self.n_changepoints
        }
