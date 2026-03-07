"""
Forecast API endpoint.
Integrates data validation, model eligibility, and explanation generation.
Enhanced with CSV data and sales context integration.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional, Tuple
from services import forecasting
from services.forecasting import generate_forecast
from services.data_validation import validate_minimum_data_points, get_data_quality_notes, DataValidationError
from services.model_eligibility import validate_model_selection, ModelIneligibilityError
import io
import csv


router = APIRouter()


class ForecastRequest(BaseModel):
    """Request model for forecast endpoint."""
    data: List[Dict[str, Any]] = Field(..., description="Time series data with 'date' and 'sales' keys, may include additional sales features")
    horizon: Literal[7, 30, 90] = Field(..., description="Forecast horizon in days")
    model: Literal[
        "auto", 
        "moving_average", 
        "weighted_moving_average",
        "holts_linear_trend",
        "polynomial_regression",
        "exponential_smoothing",
        "seasonal_naive",
        "theta",
        "arima",
        "bayesian_structural",
        "prophet",
        "vector_ar",
        "xgboost",
        "random_forest",
        "gradient_boosting",
        "lstm",
        "sarima",
        "neural_prophet"
    ] = Field(
        default="auto",
        description="Model to use for forecasting"
    )


class ForecastResponse(BaseModel):
    """Response model for forecast endpoint."""
    data_points: int
    model_used: str
    model_reason: str
    confidence_level: str
    metrics: Dict[str, float]
    forecast: List[Dict[str, Any]]
    summary: Dict[str, str]
    explanation: dict
    explanation_source: str
    notes: List[str]
    sales_context: Dict[str, Any]


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_endpoint(request: ForecastRequest):
    """
    Generate sales forecast with AI-powered explanations.
    
    Accepts time series data and returns forecast with:
    - Confidence intervals
    - Model selection reasoning
    - AI explanation (Gemini) or rule-based fallback
    - Data quality notes
    - Sales business context
    
    Enforces minimum data requirements (2+ points) and model eligibility rules.
    Enhanced to analyze sales-specific features if provided.
    """
    try:
        # Validate minimum data requirements
        validate_minimum_data_points(request.data)
        
        # Validate model selection eligibility (if not auto)
        if request.model != "auto":
            validate_model_selection(request.model, len(request.data))
        
        # Generate forecast with all necessary fields
        result = generate_forecast(
            data=request.data,
            horizon=request.horizon,
            model_choice=request.model
        )
        
        # Convert data to CSV format for Gemini analysis
        csv_data = _convert_to_csv(request.data)
        
        # Generate explanation with CSV context and sales metadata
        explanation, explanation_source = _generate_explanation(
            result, 
            csv_data=csv_data
        )
        # Ensure explanation is a dict (for JSON Gemini response)
        if isinstance(explanation, str):
            explanation = {"analysis": explanation}
        
        # Get data quality notes with actual data analysis
        # Extract values from original request data for analysis
        data_values = [float(item.get("sales", 0)) for item in request.data]
        notes = get_data_quality_notes(
            metadata=result["metadata"],
            values=data_values
        )
        
        # Extract sales context from metadata
        sales_context = {
            "product_category": result["metadata"].get("product_category", "All"),
            "regions": result["metadata"].get("regions", "All"),
            "customer_segments": result["metadata"].get("customer_segments", "All"),
            "avg_marketing_spend": result["metadata"].get("avg_marketing_spend", "Not specified"),
            "promotion_impact": result["metadata"].get("promotion_impact", "Not analyzed"),
            "avg_quantity": result["metadata"].get("avg_quantity", "N/A"),
            "avg_unit_price": result["metadata"].get("avg_unit_price", "N/A"),
        }
        
        # Build response
        response_data = {
            "data_points": result["metadata"]["data_points"],
            "model_used": result["model_used"],
            "model_reason": result["model_reason"],
            "confidence_level": result["confidence_level"],
            "metrics": result["metrics"],
            "forecast": result["forecast"],
            "summary": result["summary"],
            "explanation": explanation,
            "explanation_source": explanation_source,
            "notes": notes,
            "sales_context": sales_context
        }
        
        return ForecastResponse(**response_data)
    
    except (DataValidationError, ModelIneligibilityError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


def _convert_to_csv(data: List[Dict[str, Any]]) -> str:
    """
    Convert data to CSV string format.
    
    Args:
        data: List of dictionaries
        
    Returns:
        CSV formatted string
    """
    if not data:
        return ""
    
    output = io.StringIO()
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def _generate_explanation(forecast_result: Dict[str, Any], csv_data: Optional[str] = None) -> Tuple[str, str]:
    """
    Generate explanation using Gemini or rule-based fallback.
    Enhanced with CSV data context.
    
    Args:
        forecast_result: Forecast result dictionary
        csv_data: Optional CSV data as string
        
    Returns:
        Tuple of (explanation_text, source) where source is "gemini" or "rule-based"
    """
    explanation_engine = forecasting._explanation_engine
    if not explanation_engine:
        return "Explanation engine not initialized.", "rule-based"
    
    # Prepare metadata for explanation engine
    metadata = {
        "model_used": forecast_result["model_used"],
        "model_reason": forecast_result["model_reason"],
        "confidence_level": forecast_result["confidence_level"],
        "data_points": forecast_result["metadata"]["data_points"],
        "forecast_horizon_days": forecast_result["metadata"]["forecast_horizon"],
        "trend": forecast_result["summary"]["trend"],
        "seasonality": forecast_result["summary"]["seasonality"],
        "volatility": forecast_result["summary"]["volatility"],
        "mape": forecast_result["metrics"].get("mape", 10.0),
        # Add sales context
        "product_category": forecast_result["metadata"].get("product_category", "All"),
        "regions": forecast_result["metadata"].get("regions", "All"),
        "customer_segments": forecast_result["metadata"].get("customer_segments", "All"),
        "avg_marketing_spend": forecast_result["metadata"].get("avg_marketing_spend", "Not specified"),
        "promotion_impact": forecast_result["metadata"].get("promotion_impact", "Not analyzed"),
    }
    
    explanation, source = explanation_engine.generate_explanation(metadata, csv_data=csv_data)
    return explanation, source
