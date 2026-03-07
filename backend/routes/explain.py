"""
Gemini AI explanation endpoint.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


router = APIRouter()

# Initialize Gemini (will be configured in main.py)
genai_client = None


def initialize_gemini(api_key: str):
    """Initialize Gemini client with API key."""
    global genai_client
    if api_key and GENAI_AVAILABLE:
        try:
            genai.configure(api_key=api_key)
            genai_client = genai.GenerativeModel('gemini-3-flash-preview')
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini in explain route: {e}")
            genai_client = None


class ExplainRequest(BaseModel):
    """Request model for explain endpoint."""
    forecast_result: Dict[str, Any] = Field(..., description="Forecast result from /forecast endpoint")
    user_question: str = Field(default="", description="Optional user question about the forecast")


class ExplainResponse(BaseModel):
    """Response model for explain endpoint."""
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
async def explain_endpoint(request: ExplainRequest):
    """
    Generate AI explanation of forecast using Gemini.
    
    Receives ONLY structured metadata (no raw numbers) and explains:
    - Forecast behavior
    - Model choice
    - Confidence level
    - Risks and assumptions
    """
    if not genai_client:
        # Fallback explanation if Gemini is not configured
        return ExplainResponse(
            explanation="Gemini API not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        # Extract only metadata (no raw forecast numbers)
        forecast_metadata = {
            "model_used": request.forecast_result.get("model_used"),
            "model_reason": request.forecast_result.get("model_reason"),
            "confidence_level": request.forecast_result.get("confidence_level"),
            "metrics": request.forecast_result.get("metrics", {}),
            "summary": request.forecast_result.get("summary", {}),
            "metadata": request.forecast_result.get("metadata", {})
        }
        
        # Build prompt for Gemini
        prompt = build_explanation_prompt(forecast_metadata, request.user_question)
        
        # Generate explanation
        if genai_client:
            response = genai_client.generate_content(prompt, stream=False)
            response.resolve()
            explanation = response.text if hasattr(response, 'text') else str(response)
            return ExplainResponse(explanation=explanation)
        else:
            # Fallback if client not initialized
            explanation = generate_fallback_explanation(request.forecast_result)
            return ExplainResponse(explanation=explanation)
    
    except Exception as e:
        # Fallback to rule-based explanation
        print(f"Gemini API error: {e}")
        explanation = generate_fallback_explanation(request.forecast_result)
        return ExplainResponse(explanation=explanation)


def build_explanation_prompt(metadata: Dict[str, Any], user_question: str) -> str:
    """
    Build prompt for Gemini explanation.
    
    Args:
        metadata: Forecast metadata (no raw numbers)
        user_question: Optional user question
        
    Returns:
        Formatted prompt string
    """
    base_prompt = f"""You are a sales forecasting analyst explaining a forecast to a business user.

Forecast Metadata:
- Model Used: {metadata.get('model_used', 'unknown')}
- Model Selection Reason: {metadata.get('model_reason', 'N/A')}
- Confidence Level: {metadata.get('confidence_level', 'unknown')}
- MAPE (Mean Absolute Percentage Error): {metadata.get('metrics', {}).get('mape', 'N/A')}%
- Trend: {metadata.get('summary', {}).get('trend', 'unknown')}
- Seasonality: {metadata.get('summary', {}).get('seasonality', 'none')}
- Volatility: {metadata.get('summary', {}).get('volatility', 'unknown')}
- Data Points: {metadata.get('metadata', {}).get('data_points', 'N/A')}
- Forecast Horizon: {metadata.get('metadata', {}).get('forecast_horizon', 'N/A')} days

IMPORTANT RULES:
1. NEVER generate numerical forecast values - only explain patterns and trends
2. NEVER override or contradict the model's output
3. Focus on explaining WHY the model was chosen and what it means
4. Discuss confidence level and what factors affect it
5. Mention risks and assumptions
6. Use clear, business-friendly language

"""
    
    if user_question:
        prompt = base_prompt + f"\nUser Question: {user_question}\n\nPlease answer the user's question while following the rules above."
    else:
        prompt = base_prompt + "\nPlease provide a comprehensive explanation of this forecast following the rules above."
    
    return prompt


def generate_fallback_explanation(forecast_result: Dict[str, Any]) -> str:
    """
    Generate rule-based explanation if Gemini fails.
    
    Args:
        forecast_result: Full forecast result
        
    Returns:
        Explanation string
    """
    model_used = forecast_result.get("model_used", "unknown")
    model_reason = forecast_result.get("model_reason", "")
    confidence = forecast_result.get("confidence_level", "medium")
    trend = forecast_result.get("summary", {}).get("trend", "stable")
    seasonality = forecast_result.get("summary", {}).get("seasonality", "none")
    volatility = forecast_result.get("summary", {}).get("volatility", "moderate")
    
    explanation_parts = []
    
    # Model explanation
    if model_used == "prophet":
        explanation_parts.append("Prophet was selected for this forecast because it excels at handling seasonal patterns and trends.")
    elif model_used == "sarima":
        explanation_parts.append("SARIMA was chosen as it's well-suited for time series with both trends and seasonality.")
    else:
        explanation_parts.append("A moving average model was used, providing a stable baseline forecast.")
    
    if model_reason:
        explanation_parts.append(f"Specifically: {model_reason}.")
    
    # Trend explanation
    if trend == "upward":
        explanation_parts.append("The forecast indicates an upward trend in sales.")
    elif trend == "downward":
        explanation_parts.append("The forecast shows a downward trend in sales.")
    else:
        explanation_parts.append("The forecast suggests relatively stable sales.")
    
    # Seasonality explanation
    if seasonality == "weekly":
        explanation_parts.append("Weekly seasonality patterns were detected in your data.")
    elif seasonality == "yearly":
        explanation_parts.append("Yearly seasonality patterns were identified.")
    
    # Confidence explanation
    if confidence == "high":
        explanation_parts.append("Confidence in this forecast is high, indicating reliable predictions.")
    elif confidence == "medium":
        explanation_parts.append("Confidence is moderate - the forecast should be used with some caution.")
    else:
        explanation_parts.append("Confidence is low - consider this forecast as a rough estimate.")
    
    # Volatility note
    if volatility == "high":
        explanation_parts.append("Note: High volatility in historical data may affect forecast accuracy.")
    
    return " ".join(explanation_parts)
