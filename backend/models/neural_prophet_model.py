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
        Fit NeuralProphet model.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        if not NEURALPROPHET_AVAILABLE:
            # Fallback to manual implementation
            self._fit_fallback(dates, values)
            return
        
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < 10:
            self.metadata = {
                "status": "insufficient_data",
                "message": "Need at least 10 data points"
            }
            return
        
        self.values = values_array
        
        try:
            # Create NeuralProphet model
            self.model = NeuralProphet(
                n_lags=7,
                n_forecasts=1,
                yearly_seasonality=False,
                weekly_seasonality=True if len(values_array) >= 14 else False
            )
            
            # Prepare data as DataFrame
            import pandas as pd
            df = pd.DataFrame({
                'ds': pd.date_range(start='2024-01-01', periods=len(values_array)),
                'y': values_array
            })
            
            # Fit model
            self.model.fit(df, epochs=100, batch_size=8, verbose=0)
            
            self.metadata = {
                "type": "NeuralProphet",
                "architecture": "Neural Network with AR-Net",
                "data_points_used": len(values_array),
                "seasonality_enabled": len(values_array) >= 14,
                "message": "Neural network version of Prophet"
            }
        except Exception as e:
            self._fit_fallback(dates, values)
    
    def forecast(self, horizon: int) -> Tuple[List[float], List[float], List[float]]:
        """
        Generate NeuralProphet forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Tuple of (forecast, lower_bound, upper_bound)
        """
        if self.model is None or self.values is None:
            return [np.nan] * horizon, [np.nan] * horizon, [np.nan] * horizon
        
        try:
            import pandas as pd
            
            # Create future dataframe
            df = pd.DataFrame({
                'ds': pd.date_range(start='2024-01-01', periods=len(self.values)),
                'y': self.values
            })
            
            future = self.model.make_future_dataframe(df, periods=horizon)
            forecast = self.model.predict(future)
            
            # Extract predictions
            forecast_values = forecast['yhat'].tail(horizon).values.tolist()
            
            # Estimate confidence intervals
            std = np.std(self.values)
            lower_bounds = [v - 1.96 * std for v in forecast_values]
            upper_bounds = [v + 1.96 * std for v in forecast_values]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "neural_prophet",
                "trend": "stable",
                "seasonality": "none"
            }
        except Exception:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "neural_prophet",
                "trend": "stable",
                "seasonality": "none"
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _fit_fallback(self, dates: List[str], values: List[float]) -> None:
        """Fallback implementation if NeuralProphet unavailable."""
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < 5:
            self.metadata = {
                "status": "insufficient_data",
                "message": "Need at least 5 data points"
            }
            return
        
        self.values = values_array
        
        # Simple fallback: store values for naive forecast
        self.metadata = {
            "type": "NeuralProphet (Fallback)",
            "message": "NeuralProphet not installed, using fallback",
            "data_points_used": len(values_array),
            "status": "fallback_mode"
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
