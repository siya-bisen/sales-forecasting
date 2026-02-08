"""
Data preprocessing utilities for time series forecasting.
"""
from typing import List, Tuple, Dict, Any
import pandas as pd
from datetime import datetime
import numpy as np


def validate_and_normalize_data(data: List[Dict[str, Any]]) -> Tuple[List[str], List[float], Dict[str, Any]]:
    """
    Validate and normalize time series data.
    
    Args:
        data: List of dictionaries with 'date' and 'sales' keys
        
    Returns:
        Tuple of (dates, values, metadata)
        
    Raises:
        ValueError: If data is invalid
    """
    if not data or len(data) < 2:
        raise ValueError("At least 2 data points are required")
    
    dates = []
    values = []
    
    for item in data:
        # Validate date
        try:
            date_str = str(item.get('date', ''))
            parsed_date = pd.to_datetime(date_str)
            dates.append(date_str)
        except:
            raise ValueError(f"Invalid date format: {item.get('date')}")
        
        # Validate sales value
        try:
            sales_value = float(item.get('sales', 0))
            if sales_value < 0:
                raise ValueError(f"Sales value cannot be negative: {sales_value}")
            values.append(sales_value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid sales value: {item.get('sales')}")
    
    # Sort by date
    df = pd.DataFrame({'date': pd.to_datetime(dates), 'value': values})
    df = df.sort_values('date').reset_index(drop=True)
    
    # Check for duplicates
    if df['date'].duplicated().any():
        # Aggregate duplicates by taking mean
        df = df.groupby('date')['value'].mean().reset_index()
    
    # Fill missing dates (optional - could also raise error)
    # For MVP, we'll just use available data
    
    dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
    values = df['value'].tolist()
    
    # Calculate metadata
    metadata = {
        "data_points": len(values),
        "date_range": {
            "start": dates[0],
            "end": dates[-1]
        },
        "statistics": {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values))
        },
        "volatility": calculate_volatility(values),
        "trend": detect_trend(values),
        "has_seasonality": detect_seasonality(dates, values)
    }
    
    return dates, values, metadata


def calculate_volatility(values: List[float]) -> str:
    """
    Calculate volatility level of the time series.
    
    Args:
        values: List of sales values
        
    Returns:
        Volatility level: "low", "moderate", or "high"
    """
    if len(values) < 2:
        return "low"
    
    # Calculate coefficient of variation
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if mean_val == 0:
        return "high"
    
    cv = std_val / mean_val
    
    if cv < 0.1:
        return "low"
    elif cv < 0.3:
        return "moderate"
    else:
        return "high"


def detect_trend(values: List[float]) -> str:
    """
    Detect trend direction in the time series.
    
    Args:
        values: List of sales values
        
    Returns:
        Trend: "upward", "downward", or "stable"
    """
    if len(values) < 2:
        return "stable"
    
    # Simple linear regression slope
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    
    # Normalize by mean
    mean_val = np.mean(values)
    if mean_val > 0:
        slope_pct = slope / mean_val
        if slope_pct > 0.01:
            return "upward"
        elif slope_pct < -0.01:
            return "downward"
    
    return "stable"


def detect_seasonality(dates: List[str], values: List[float]) -> bool:
    """
    Detect if time series has seasonality.
    
    Args:
        dates: List of date strings
        values: List of sales values
        
    Returns:
        True if seasonality detected, False otherwise
    """
    if len(values) < 14:
        return False
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'value': values
    })
    
    # Check for weekly seasonality
    df['day_of_week'] = df['date'].dt.dayofweek
    weekly_variance = df.groupby('day_of_week')['value'].var().mean()
    overall_variance = df['value'].var()
    
    # If weekly variance is significantly different, there's seasonality
    if weekly_variance > 0 and overall_variance > 0:
        ratio = weekly_variance / overall_variance
        if ratio > 0.5:  # Threshold for seasonality
            return True
    
    return False
