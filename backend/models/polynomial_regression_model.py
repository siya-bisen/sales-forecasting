"""
Polynomial Regression Model
Simple trend-fitting approach using polynomial functions.
Captures polynomial trends in sales data.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class PolynomialRegressionModel:
    """
    Polynomial Regression forecasting model.
    Fits a polynomial function to time series data.
    
    Features:
    - Auto-detects optimal polynomial degree (1-3)
    - Simple and interpretable
    - Fast computation
    - Good for smooth trends
    - No hyperparameters to tune
    """
    
    def __init__(self, degree: int = None):
        """
        Initialize Polynomial Regression model.
        
        Args:
            degree: Polynomial degree (auto-selected if None)
        """
        self.degree = degree
        self.model = None
        self.poly_features = None
        self.values = None
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit polynomial regression model with validation.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        # Validate input
        if not values or len(values) < 3:
            raise ValueError(f"Need at least 3 data points (have {len(values) if values else 0})")
        
        # Clean invalid values
        values_clean = [v for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
        if len(values_clean) < 3:
            raise ValueError("Not enough valid data points for polynomial fitting")
        
        values_array = np.array(values_clean, dtype=float)
        self.values = values_array
        
        # Auto-detect optimal degree if not provided
        if self.degree is None:
            self.degree = self._auto_select_degree(values_array)
        else:
            self.degree = min(max(1, self.degree), 3)  # Limit to 1-3
        
        # Create features
        X = np.arange(len(values_array)).reshape(-1, 1)
        self.poly_features = PolynomialFeatures(degree=self.degree, include_bias=False)
        X_poly = self.poly_features.fit_transform(X)
        
        # Fit model
        self.model = LinearRegression()
        self.model.fit(X_poly, values_array)
        
        # Calculate R-squared
        r_squared = self.model.score(X_poly, values_array)
        
        # Extract trend interpretation
        trend_direction = self._get_trend_direction()
        
        self.metadata = {
            "type": "Polynomial Regression",
            "degree": self.degree,
            "r_squared": round(r_squared, 4),
            "trend_direction": trend_direction,
            "data_points_used": len(values_array),
            "fitted": True,
            "interpretation": f"Degree-{self.degree} polynomial fit",
            "message": "Polynomial trend fitting model"
        }
        
        self.fitted = True
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate polynomial regression forecast with confidence intervals.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if not self.fitted or self.model is None or self.values is None:
            raise ValueError("Model must be fitted before forecasting")
        
        if horizon < 1:
            raise ValueError("Horizon must be at least 1")
        
        try:
            forecast_values = []
            n = len(self.values)
            
            # Generate predictions for future periods
            for i in range(horizon):
                X_future = np.array([[n + i]])
                X_poly = self.poly_features.transform(X_future)
                pred = float(self.model.predict(X_poly)[0])
                forecast_values.append(max(0, pred))
            
            # Calculate residuals for uncertainty
            X_train = np.arange(n).reshape(-1, 1)
            X_train_poly = self.poly_features.transform(X_train)
            residuals = self.values - self.model.predict(X_train_poly)
            residual_std = np.std(residuals) if np.std(residuals) > 0 else np.mean(forecast_values) * 0.1
            if residual_std == 0:
                residual_std = np.mean(forecast_values) * 0.1 if np.mean(forecast_values) > 0 else 1
            
            # Confidence intervals with horizon-based expansion
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
                "degree": self.degree,
                "confidence_level": 0.95,
                "method": "Polynomial Regression"
            }
        except Exception as e:
            raise ValueError(f"Polynomial regression forecast failed: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _auto_select_degree(self, values: np.ndarray) -> int:
        """Auto-select optimal polynomial degree."""
        if len(values) < 5:
            return 1
        
        X = np.arange(len(values)).reshape(-1, 1)
        best_degree = 1
        best_score = -np.inf
        
        # Try degrees 1-3
        for degree in [1, 2, 3]:
            poly_features = PolynomialFeatures(degree=degree)
            X_poly = poly_features.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, values)
            
            # Use AIC for model selection
            predictions = model.predict(X_poly)
            residuals = values - predictions
            mse = np.mean(residuals ** 2)
            n_params = degree + 1
            aic = 2 * n_params + len(values) * np.log(mse + 1e-8)
            
            score = -aic  # Lower AIC is better
            
            if score > best_score:
                best_score = score
                best_degree = degree
        
        return best_degree
    
    def _get_trend_direction(self) -> str:
        """Get trend direction from polynomial coefficients."""
        if self.model is None:
            return "stable"
        
        # Coefficient of highest degree term indicates direction
        coefficients = self.model.coef_
        
        if len(coefficients) > 1:
            high_degree_coef = coefficients[-1]
            
            if high_degree_coef > 0.001:
                return "upward"
            elif high_degree_coef < -0.001:
                return "downward"
        
        return "stable"
