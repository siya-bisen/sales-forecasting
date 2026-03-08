"""
NeuralProphet Forecasting Model
Neural network variant of Facebook's Prophet.
Combines neural networks with time series domain knowledge.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
try:
    from neuralprophet import NeuralProphet
    NEURALPROPHET_AVAILABLE = True
except ImportError:
    NEURALPROPHET_AVAILABLE = False


class NeuralProphetModel:
    """
    NeuralProphet forecasting model.
    Neural network approach inspired by Prophet.
    Captures trend, seasonality, and special events.
    
    Features:
    - Neural network backbone
    - Automatic seasonality detection
    - Handles trend changes
    - Fast training
    - Good interpretability
    """
    
    def __init__(self):
        """Initialize NeuralProphet model."""
        self.model = None
        self.values = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit NeuralProphet model with robust validation.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 10:
            raise ValueError(f"Need at least 10 data points (have {len(values) if values else 0})")
        
        # Clean invalid values
        values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        if len(values_clean) < 10:
            raise ValueError("Not enough valid data points for NeuralProphet")
        
        values_array = np.array(values_clean, dtype=float)
        self.values = values_array
        
        if not NEURALPROPHET_AVAILABLE:
            # Fallback to manual implementation
            self._fit_fallback(values_array)
            return
        
        try:
            # Create NeuralProphet model
            self.model = NeuralProphet(
                n_lags=min(7, len(values_array) // 3),
                n_forecasts=1,
                yearly_seasonality=False,
                weekly_seasonality=len(values_array) >= 14
            )
            
            # Prepare data as DataFrame
            import pandas as pd
            df = pd.DataFrame({
                'ds': pd.date_range(start='2024-01-01', periods=len(values_array)),
                'y': values_array
            })
            
            # Fit model with adaptive epochs
            epochs = min(100, max(20, len(values_array) // 2))
            self.model.fit(df, epochs=epochs, batch_size=8, verbose=0)
            
            self.metadata = {
                "type": "NeuralProphet",
                "architecture": "Neural Network with AR-Net",
                "data_points_used": len(values_array),
                "seasonality_enabled": len(values_array) >= 14,
                "fitted": True,
                "n_lags": min(7, len(values_array) // 3),
                "message": "Neural network version of Prophet"
            }
        except Exception as e:
            # Fallback if NeuralProphet fitting fails
            self._fit_fallback(values_array)
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate NeuralProphet forecast with bounds validation.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast values and confidence intervals
        """
        if self.model is None or self.values is None:
            raise ValueError("Model must be fitted before forecasting")
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            import pandas as pd
            
            # Create historical dataframe
            df = pd.DataFrame({
                'ds': pd.date_range(start='2024-01-01', periods=len(self.values)),
                'y': self.values
            })
            
            future = self.model.make_future_dataframe(df, periods=horizon)
            forecast = self.model.predict(future)
            
            # Extract predictions and apply non-negative constraint
            forecast_values = [max(0, float(v)) for v in forecast['yhat'].tail(horizon).values.tolist()]
            
            # Calculate confidence intervals from residuals
            residuals = self.values - forecast['yhat'].head(len(self.values)).values
            std_error = np.std(residuals) if np.std(residuals) > 0 else np.mean(forecast_values) * 0.1
            
            lower_bounds = []
            upper_bounds = []
            
            for i, fv in enumerate(forecast_values):
                # Increase uncertainty with horizon
                adjusted_std = std_error * np.sqrt(1 + i * 0.08)
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
                "method": "NeuralProphet"
            }
        except Exception as e:
            raise ValueError(f"NeuralProphet forecast failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _fit_fallback(self, values_array: np.ndarray) -> None:
        """Fallback implementation if NeuralProphet unavailable."""
        if len(values_array) < 5:
            raise ValueError("Need at least 5 data points")
        
        self.values = values_array
        
        # Simple fallback: store values for naive forecast
        self.metadata = {
            "type": "NeuralProphet (Fallback)",
            "message": "NeuralProphet not installed or failed, using fallback",
            "data_points_used": len(values_array),
            "fitted": True,
            "fallback_mode": True
        }
    
    def _forecast_fallback(self, horizon: int) -> Tuple[List[float], List[float], List[float]]:
        """Fallback forecasting using exponential smoothing concept."""
        if self.values is None:
            return [np.nan] * horizon, [np.nan] * horizon, [np.nan] * horizon
        
        # Use weighted average of recent values
        recent = self.values[-7:] if len(self.values) >= 7 else self.values
        weights = np.linspace(1, len(recent), len(recent))
        weights = weights / np.sum(weights)
        
        base_forecast = np.sum(recent * weights)
        
        forecast_values = [base_forecast] * horizon
        std = np.std(self.values)
        
        lower_bounds = [v - 1.96 * std for v in forecast_values]
        upper_bounds = [v + 1.96 * std for v in forecast_values]
        
        return forecast_values, lower_bounds, upper_bounds
