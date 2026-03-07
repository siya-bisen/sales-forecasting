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
        Fit polynomial regression model.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < 3:
            self.metadata = {
                "status": "insufficient_data",
                "message": "Need at least 3 data points"
            }
            return
        
        self.values = values_array
        
        # Auto-detect optimal degree if not provided
        if self.degree is None:
            self.degree = self._auto_select_degree(values_array)
        else:
            self.degree = min(max(1, self.degree), 3)  # Limit to 1-3
        
        # Create features
        X = np.arange(len(values_array)).reshape(-1, 1)
        self.poly_features = PolynomialFeatures(degree=self.degree)
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
            "interpretation": f"Degree-{self.degree} polynomial trend",
            "message": "Simple polynomial trend fitting"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate polynomial regression forecast.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
        """
        if self.model is None or self.values is None:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "polynomial_regression",
                "trend": "stable",
                "seasonality": "none"
            }
        
        forecast_values = []
        n = len(self.values)
        
        # Generate predictions for future periods
        for i in range(horizon):
            X_future = np.array([[n + i]])
            X_poly = self.poly_features.transform(X_future)
            pred = self.model.predict(X_poly)[0]
            forecast_values.append(pred)
        
        # Calculate residuals for uncertainty
        X_train = np.arange(n).reshape(-1, 1)
        X_train_poly = self.poly_features.transform(X_train)
        residuals = self.values - self.model.predict(X_train_poly)
        residual_std = np.std(residuals)
        
        # Confidence intervals (±1.96 std dev for 95% CI)
        lower_bounds = [v - 1.96 * residual_std for v in forecast_values]
        upper_bounds = [v + 1.96 * residual_std for v in forecast_values]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "polynomial_regression",
            "trend": "stable",
            "seasonality": "none"
        }
    
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
