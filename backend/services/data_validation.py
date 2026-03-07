"""
Data validation service for minimum data requirements.
Enforces global data eligibility rules.
"""
from typing import List, Dict, Any


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


def validate_minimum_data_points(data: List[Dict[str, Any]]) -> None:
    """
    Validate that minimum data points requirement is met.
    
    Args:
        data: List of data points with 'date' and 'sales' keys
        
    Raises:
        DataValidationError: If fewer than 2 data points provided
    """
    if not data or len(data) < 2:
        raise DataValidationError(
            "At least 2 data points are required to generate a forecast."
        )


def get_data_quality_notes(metadata: Dict[str, Any] = None, values: List[float] = None) -> List[str]:
    """
    Generate meaningful data quality notes based on actual data characteristics.
    
    Args:
        metadata: Optional metadata dictionary from preprocessing
        values: Optional list of sales values
        
    Returns:
        List of meaningful note strings to include in responses
    """
    notes = []
    
    if not metadata or not values:
        return ["✓ Data validation complete. Ready for forecasting."]
    
    data_points = metadata.get("data_points", 0)
    volatility = metadata.get("volatility", "moderate")
    trend = metadata.get("trend", "stable")
    has_seasonality = metadata.get("has_seasonality", False)
    stats = metadata.get("statistics", {})
    
    # Data point quality
    if data_points < 10:
        notes.append(f"⚠️ Limited historical data ({data_points} points). Consider adding more data for better accuracy.")
    elif data_points < 30:
        notes.append(f"✓ Good dataset size ({data_points} points). Forecast confidence moderate to high.")
    else:
        notes.append(f"✓ Excellent dataset ({data_points} points). Strong forecast confidence expected.")
    
    # Volatility assessment
    if volatility == "high":
        notes.append("⚠️ High volatility detected. Forecast ranges may be wider than usual. Consider external factors affecting sales.")
    elif volatility == "low":
        notes.append("✓ Low volatility. Stable and predictable sales pattern detected.")
    else:
        notes.append("✓ Moderate volatility. Healthy balance between stability and variation.")
    
    # Trend analysis
    if trend == "upward":
        notes.append("📈 Upward trend detected. Sales showing growth pattern.")
    elif trend == "downward":
        notes.append("📉 Downward trend detected. Sales showing decline pattern.")
    else:
        notes.append("➡️ Stable trend. No significant growth or decline detected.")
    
    # Seasonality check
    if has_seasonality:
        notes.append("🔄 Seasonality pattern detected. Forecast accounts for periodic fluctuations.")
    
    # Range and spread analysis
    if stats:
        min_val = stats.get("min", 0)
        max_val = stats.get("max", 0)
        mean_val = stats.get("mean", 0)
        std_val = stats.get("std", 0)
        
        # Calculate coefficient of variation
        if mean_val > 0:
            cv = (std_val / mean_val) * 100
            if cv > 50:
                notes.append(f"📊 High variation coefficient ({cv:.1f}%). Wide range between min (${min_val:.0f}) and max (${max_val:.0f}).")
        
        # Outlier detection (simple: values beyond 2 std devs)
        outliers = sum(1 for v in values if abs(v - mean_val) > 2 * std_val) if std_val > 0 else 0
        if outliers > 0:
            outlier_pct = (outliers / len(values)) * 100
            notes.append(f"🔍 {outliers} potential outlier(s) detected ({outlier_pct:.1f}% of data). Verify unusual sales events.")
    
    # General best practices
    if len(notes) < 3:
        notes.append("✓ Data quality is acceptable for forecasting.")
    
    return notes
