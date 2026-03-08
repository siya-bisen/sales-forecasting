"""
Random Forest forecasting model.
Non-parametric ML model excellent for capturing complex patterns.
Uses lagged features, rolling statistics, and trend indicators.
Improved with better feature engineering and adaptive parameters.
"""
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class RandomForestModel:
    """Random Forest forecasting model for time series with enhanced features."""
    
    def __init__(self, n_estimators: int = None, max_depth: int = None):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees (auto-selected if None)
            max_depth: Maximum depth of trees (auto-selected if None)
        """
        self.model = None
        self.fitted = False
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.scaler = StandardScaler()
        self.last_values = None
        self.feature_importance = {}
        self.feature_names = []
        self.lookback = 7
    
    def _create_features(self, values: np.ndarray, lookback: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create enhanced features from time series using lagged values and statistics.
        
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
            # Features: past values, moving averages, trend, momentum
            past_values = values[i-lookback:i]
            features = list(past_values)
            
            # Add rolling statistics
            ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else np.mean(past_values)
            ma_7 = np.mean(past_values) if len(past_values) >= 7 else np.mean(past_values)
            std = np.std(past_values)
            min_val = np.min(past_values)
            max_val = np.max(past_values)
            
            features.extend([ma_3, ma_7, std, min_val, max_val])
            
            # Add trend (slope)
            trend = 0
            if len(past_values) > 1:
                trend = (past_values[-1] - past_values[0]) / len(past_values)
            features.append(trend)
            
            # Add momentum (recent acceleration)
            momentum = 0
            if len(past_values) >= 3:
                momentum = (past_values[-1] - past_values[-2]) - (past_values[-2] - past_values[-3])
            features.append(momentum)
            
            # Add velocity (rate of change)
            velocity = 0
            if len(past_values) > 1:
                velocity = (past_values[-1] - past_values[-2]) / (past_values[-2] + 1e-8)
            features.append(velocity)
            
            X.append(features)
            y.append(values[i])
        
        return np.array(X), np.array(y)
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit Random Forest model to historical data with robust error handling.
        
        Args:
            dates: List of date strings (YYYY-MM-DD)
            values: List of sales values
        """
        # Validate and clean input
        try:
            values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
            
            if len(values_clean) < 5:
                raise ValueError(f"Random Forest requires at least 5 data points (have {len(values_clean)})")
            
            values_array = np.array(values_clean, dtype=float)
            
            # Determine lookback period based on data length
            lookback = min(7, max(3, len(values_array) - 2))
            self.lookback = lookback
            
            # Create features
            X, y = self._create_features(values_array, lookback)
            
            if len(X) < 2:
                raise ValueError(f"Not enough data points to create features (created {len(X)})")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine adaptive parameters
            if self.n_estimators is None:
                self.n_estimators = min(100, max(10, len(X) * 2))
            
            if self.max_depth is None:
                self.max_depth = min(15, max(5, int(np.sqrt(len(X)))))
            
            # Train Random Forest with optimized parameters
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=max(2, len(X) // 10),
                min_samples_leaf=max(1, len(X) // 20),
                random_state=42,
                n_jobs=-1,
                verbose=0
            )
            self.model.fit(X_scaled, y)
            
            # Store feature importances
            self.feature_names = (
                [f"lag_{i+1}" for i in range(lookback)] + 
                ["ma_3", "ma_7", "std", "min", "max", "trend", "momentum", "velocity"]
            )
            self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            
            # Store last values for prediction
            self.last_values = values_clean[-lookback:] if len(values_clean) >= lookback else values_clean
            self.fitted = True
        except Exception as e:
            raise ValueError(f"Failed to fit Random Forest model: {str(e)}")
    
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
            forecast_values = []
            current_values = list(self.last_values)
            
            for _ in range(horizon):
                # Create feature vector
                past_values = np.array(current_values[-self.lookback:])
                
                # Calculate features
                ma_3 = np.mean(past_values[-3:]) if len(past_values) >= 3 else np.mean(past_values)
                ma_7 = np.mean(past_values)
                std = np.std(past_values)
                min_val = np.min(past_values)
                max_val = np.max(past_values)
                
                trend = 0
                if len(past_values) > 1:
                    trend = (past_values[-1] - past_values[0]) / len(past_values)
                
                momentum = 0
                if len(past_values) >= 3:
                    momentum = (past_values[-1] - past_values[-2]) - (past_values[-2] - past_values[-3])
                
                velocity = 0
                if len(past_values) > 1:
                    velocity = (past_values[-1] - past_values[-2]) / (past_values[-2] + 1e-8)
                
                features = np.concatenate([
                    past_values, [ma_3, ma_7, std, min_val, max_val, trend, momentum, velocity]
                ]).reshape(1, -1)
                
                features_scaled = self.scaler.transform(features)
                
                # Predict
                pred = float(self.model.predict(features_scaled)[0])
                pred = max(0, pred)  # Ensure positive values
                
                forecast_values.append(pred)
                current_values.append(pred)
            
            # Estimate uncertainty
            pred_std = np.std(forecast_values) if len(forecast_values) > 1 else np.mean(forecast_values) * 0.1
            if pred_std == 0:
                pred_std = np.mean(forecast_values) * 0.1 if np.mean(forecast_values) > 0 else 1
            
            lower_bounds = []
            upper_bounds = []
            
            for i, pred in enumerate(forecast_values):
                # Wider bounds further in the future
                horizon_factor = 1 + (i / horizon * 0.3) if horizon > 0 else 1
                margin = 1.96 * pred_std * horizon_factor * 0.12
                lower_bounds.append(max(0, pred - margin))
                upper_bounds.append(pred + margin)
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "random_forest",
                "lookback": self.lookback,
                "n_estimators": self.n_estimators,
                "trend": self._detect_trend(forecast_values),
                "top_features": dict(sorted(self.feature_importance.items(), 
                                           key=lambda x: x[1], reverse=True)[:3])
            }
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")
    
    def _detect_trend(self, forecast_values: List[float]) -> str:
        """Detect trend from forecast values."""
        if len(forecast_values) < 2:
            return "stable"
        
        # Compare first third and last third
        third = len(forecast_values) // 3
        first_avg = np.mean(forecast_values[:third]) if third > 0 else forecast_values[0]
        last_avg = np.mean(forecast_values[-third:]) if third > 0 else forecast_values[-1]
        
        if first_avg == 0:
            return "stable"
        
        change_pct = (last_avg - first_avg) / first_avg
        
        if change_pct > 0.05:
            return "upward"
        elif change_pct < -0.05:
            return "downward"
        else:
            return "stable"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata for explanation."""
        return {
            "model_name": "random_forest",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "top_features": dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]),
            "description": "Random Forest - Ensemble machine learning model capturing complex patterns"
        }
