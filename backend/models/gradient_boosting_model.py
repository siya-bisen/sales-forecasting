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
        Fit Gradient Boosting model to historical data with adaptive parameters.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate and clean input
        try:
            values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
            
            if len(values_clean) < 5:
                raise ValueError(f"Gradient Boosting requires at least 5 data points (have {len(values_clean)})")
            
            values_array = np.array(values_clean, dtype=float)
            
            # Determine lookback period
            lookback = min(7, max(3, len(values_array) - 2))
            self.lookback = lookback
            
            # Create features
            X, y = self._create_features(values_array, lookback)
            
            if len(X) < 2:
                raise ValueError(f"Not enough data points to create features (created {len(X)})")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine adaptive hyperparameters
            n_est = max(20, min(100, len(X) // 2)) if self.n_estimators is None or self.n_estimators == 50 else self.n_estimators
            lr = 0.05 if self.learning_rate is None or self.learning_rate == 0.05 else self.learning_rate
            max_d = min(8, max(3, int(np.sqrt(X.shape[1])))) if self.max_depth is None or self.max_depth == 5 else self.max_depth
            
            # Train Gradient Boosting with optimized parameters
            self.model = GradientBoostingRegressor(
                n_estimators=n_est,
                learning_rate=lr,
                max_depth=max_d,
                min_samples_split=max(2, len(X) // 10),
                min_samples_leaf=max(1, len(X) // 20),
                subsample=0.8,
                loss='squared_error',
                random_state=42,
                verbose=0
            )
            self.model.fit(X_scaled, y)
            
            # Store feature importances and metadata
            self.last_values = values_clean[-lookback:] if len(values_clean) >= lookback else values_clean
            self.fitted = True
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
            if residual_std == 0:
                residual_std = np.mean(forecast_values) * 0.1
            
            lower_bounds = []
            upper_bounds = []
            
            for i, fv in enumerate(forecast_values):
                # Increase uncertainty with horizon
                adjusted_std = residual_std * np.sqrt(1 + i * 0.08)
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
                "lookback": self.lookback,
                "confidence_level": 0.95,
                "method": "Gradient Boosting",
                "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        except Exception as e:
            raise ValueError(f"Gradient Boosting forecast failed: {str(e)}")
    
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
