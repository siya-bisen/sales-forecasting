"""
Gradient Boosting forecasting model.
Powerful ensemble method combining weak learners.
Excellent for capturing nonlinear relationships.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class GradientBoostingModel:
    """Gradient Boosting forecasting model for time series."""
    
    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1, max_depth: int = 5):
        """
        Initialize Gradient Boosting model.
        
        Args:
            n_estimators: Number of boosting stages
            learning_rate: Learning rate (lower = more conservative)
            max_depth: Maximum depth of trees
        """
        self.model = None
        self.fitted = False
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.scaler = StandardScaler()
        self.last_values = None
        self.feature_importance = {}
    
    def _create_features(self, values: np.ndarray, lookback: int = 7) -> tuple:
        """
        Create features from time series using lagged values and statistics.
        
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
            past_values = values[i-lookback:i]
            features = list(past_values)
            
            # Add statistical features
            features.append(np.mean(past_values))  # Mean
            features.append(np.std(past_values) if len(past_values) > 1 else 0)  # Std
            features.append(np.min(past_values))  # Min
            features.append(np.max(past_values))  # Max
            
            # Add moving averages
            ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else np.mean(past_values)
            ma_7 = np.mean(past_values) if len(past_values) >= 7 else np.mean(past_values)
            features.extend([ma_3, ma_7])
            
            # Add trend features
            if len(past_values) > 1:
                trend = (past_values[-1] - past_values[0]) / len(past_values)
                momentum = past_values[-1] - past_values[-2] if len(past_values) > 1 else 0
                features.extend([trend, momentum])
            else:
                features.extend([0, 0])
            
            # Add cyclical feature (day of week encoded)
            features.append((i % 7) / 7.0)  # Normalized day of week
            
            X.append(features)
            y.append(values[i])
        
        return np.array(X), np.array(y)
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Gradient Boosting model to historical data.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        if len(values) < 5:
            raise ValueError("Gradient Boosting requires at least 5 data points")
        
        # Determine lookback period
        lookback = min(7, len(values) - 2)
        
        try:
            # Create features
            X, y = self._create_features(np.array(values), lookback)
            
            if len(X) < 2:
                raise ValueError("Not enough data points to create features")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Gradient Boosting
            self.model = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                min_samples_split=2,
                min_samples_leaf=1,
                loss='squared_error',
                random_state=42
            )
            self.model.fit(X_scaled, y)
            
            # Store feature importances
            feature_names = (
                [f"lag_{i+1}" for i in range(lookback)] +
                ["mean", "std", "min", "max", "ma_3", "ma_7", "trend", "momentum", "day_of_week"]
            )
            self.feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            
            # Store last values
            self.last_values = values[-lookback:] if len(values) >= lookback else values
            self.lookback = lookback
            self.fitted = True
        except Exception as e:
            raise ValueError(f"Failed to fit Gradient Boosting model: {str(e)}")
    
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
            current_values = list(self.last_values)
            
            for step in range(horizon):
                # Create feature vector
                past_values = np.array(current_values[-self.lookback:])
                
                # Statistical features
                mean_val = np.mean(past_values)
                std_val = np.std(past_values) if len(past_values) > 1 else 0
                min_val = np.min(past_values)
                max_val = np.max(past_values)
                
                # Moving averages
                ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else mean_val
                ma_7 = np.mean(past_values)
                
                # Trend and momentum
                trend = (past_values[-1] - past_values[0]) / len(past_values) if len(past_values) > 1 else 0
                momentum = past_values[-1] - past_values[-2] if len(past_values) > 1 else 0
                
                # Cyclical feature
                day_of_week = ((len(current_values) - self.lookback + step) % 7) / 7.0
                
                # Combine features
                features = np.array([
                    *past_values,
                    mean_val, std_val, min_val, max_val,
                    ma_3, ma_7, trend, momentum, day_of_week
                ]).reshape(1, -1)
                
                features_scaled = self.scaler.transform(features)
                
                # Predict
                pred = self.model.predict(features_scaled)[0]
                pred = max(0, pred)  # Ensure positive
                
                forecast_values.append(pred)
                current_values.append(pred)
            
            # Estimate confidence intervals using model performance
            residual_std = np.std(forecast_values) * 0.2 if len(forecast_values) > 1 else np.mean(forecast_values) * 0.15
            
            lower_bounds = [max(0, v - 1.96 * residual_std) for v in forecast_values]
            upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "gradient_boosting",
                "lookback": self.lookback,
                "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "gradient_boosting",
            "n_estimators": self.n_estimators,
            "learning_rate": self.learning_rate,
            "max_depth": self.max_depth,
            "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]),
            "description": "Gradient Boosting - Sequential ensemble method with strong predictive power"
        }
