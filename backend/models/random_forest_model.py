"""
Random Forest forecasting model.
Non-parametric ML model excellent for capturing complex patterns.
Uses lagged features and recent trends.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class RandomForestModel:
    """Random Forest forecasting model for time series."""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
        """
        self.model = None
        self.fitted = False
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.scaler = StandardScaler()
        self.last_values = None
        self.feature_importance = {}
    
    def _create_features(self, values: np.ndarray, lookback: int = 7) -> tuple:
        """
        Create features from time series using lagged values.
        
        Args:
            values: Time series values
            lookback: Number of past periods to use as features
            
        Returns:
            Tuple of (X, y) features and targets
        """
        X, y = [], []
        
        # Ensure we have enough data
        if len(values) <= lookback:
            lookback = max(1, len(values) - 2)
        
        for i in range(lookback, len(values)):
            # Features: past values, moving average, trend
            past_values = values[i-lookback:i]
            features = list(past_values)
            
            # Add moving averages
            ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else np.mean(past_values)
            ma_7 = np.mean(past_values) if len(past_values) >= 7 else np.mean(past_values)
            
            features.extend([ma_3, ma_7])
            
            # Add trend (slope)
            if len(past_values) > 1:
                trend = (past_values[-1] - past_values[0]) / len(past_values)
                features.append(trend)
            else:
                features.append(0)
            
            X.append(features)
            y.append(values[i])
        
        return np.array(X), np.array(y)
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Random Forest model to historical data.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        if len(values) < 5:
            raise ValueError("Random Forest requires at least 5 data points")
        
        # Determine lookback period based on data length
        lookback = min(7, len(values) - 2)
        
        try:
            # Create features
            X, y = self._create_features(np.array(values), lookback)
            
            if len(X) < 2:
                raise ValueError("Not enough data points to create features")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_scaled, y)
            
            # Store feature importances
            feature_names = [f"lag_{i+1}" for i in range(lookback)] + ["ma_3", "ma_7", "trend"]
            self.feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            
            # Store last values for prediction
            self.last_values = values[-lookback:] if len(values) >= lookback else values
            self.lookback = lookback
            self.fitted = True
        except Exception as e:
            raise ValueError(f"Failed to fit Random Forest model: {str(e)}")
    
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
            forecast_values = []
            forecast_errors = []
            current_values = list(self.last_values)
            
            for _ in range(horizon):
                # Create feature vector
                past_values = np.array(current_values[-self.lookback:])
                
                ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else np.mean(past_values)
                ma_7 = np.mean(past_values)
                trend = (past_values[-1] - past_values[0]) / len(past_values) if len(past_values) > 1 else 0
                
                features = np.concatenate([past_values, [ma_3, ma_7, trend]]).reshape(1, -1)
                features_scaled = self.scaler.transform(features)
                
                # Predict
                pred = self.model.predict(features_scaled)[0]
                pred = max(0, pred)  # Ensure positive values
                
                forecast_values.append(pred)
                current_values.append(pred)
            
            # Estimate uncertainty using ensemble predictions
            # Simple approach: use model's training residual std
            train_pred = self.model.predict(self.scaler.transform(
                self._create_features(np.array(self.last_values + forecast_values), self.lookback)[0]
            )) if len(self.last_values) > 1 else np.array(forecast_values)
            
            residual_std = np.std(forecast_values) * 0.15 if len(forecast_values) > 1 else np.mean(forecast_values) * 0.1
            
            lower_bounds = [max(0, v - 1.96 * residual_std) for v in forecast_values]
            upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "random_forest",
                "lookback": self.lookback,
                "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3])
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "random_forest",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]),
            "description": "Random Forest - Ensemble machine learning model capturing complex patterns"
        }
