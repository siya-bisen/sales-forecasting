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


def get_data_quality_notes() -> List[str]:
    """
    Get informational notes about data quality.
    
    Returns:
        List of note strings to include in responses
    """
    return [
        "More historical data generally leads to more accurate forecasts."
    ]
