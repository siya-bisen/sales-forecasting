"""
Forecast API endpoint.
Integrates data validation, model eligibility, and explanation generation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional, Tuple
from services import forecasting
from services.forecasting import generate_forecast
from services.data_validation import validate_minimum_data_points, get_data_quality_notes, DataValidationError
from services.model_eligibility import validate_model_selection, ModelIneligibilityError


router = APIRouter()


class ForecastRequest(BaseModel):
    """Request model for forecast endpoint."""
    data: List[Dict[str, Any]] = Field(..., description="Time series data with 'date' and 'sales' keys")
    horizon: Literal[7, 30, 90] = Field(..., description="Forecast horizon in days")
    model: Literal["auto", "moving_average", "prophet", "sarima"] = Field(
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
    explanation: str
    explanation_source: str
    notes: List[str]


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_endpoint(request: ForecastRequest):
    """
    Generate sales forecast with AI-powered explanations.
    
    Accepts time series data and returns forecast with:
    - Confidence intervals
    - Model selection reasoning
    - AI explanation (Gemini) or rule-based fallback
    - Data quality notes
    
    Enforces minimum data requirements (2+ points) and model eligibility rules.
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
        
        # Generate explanation
        explanation, explanation_source = _generate_explanation(result)
        
        # Get data quality notes
        notes = get_data_quality_notes()
        
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
            "notes": notes
        }
        
        return ForecastResponse(**response_data)
    
    except (DataValidationError, ModelIneligibilityError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


def _generate_explanation(forecast_result: Dict[str, Any]) -> Tuple[str, str]:
    """
    Generate explanation using Gemini or rule-based fallback.
    
    Args:
        forecast_result: Forecast result dictionary
        
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
        "mape": forecast_result["metrics"].get("mape", 10.0)
    }
    
    explanation, source = explanation_engine.generate_explanation(metadata)
    return explanation, source
