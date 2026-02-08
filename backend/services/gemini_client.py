"""
Gemini API client for generating AI explanations.
Handles API calls, error handling, and graceful fallback.
"""
from typing import Dict, Any, Optional
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiClient:
    """Client for Gemini API with error handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key. If None, looks for GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.is_available = False
        
        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-3-flash-preview')
                self.is_available = True
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                self.is_available = False
    
    def generate_explanation(self, prompt: str) -> Optional[str]:
        """
        Generate explanation using Gemini API.
        
        Args:
            prompt: Structured prompt for Gemini
            
        Returns:
            Explanation string, or None if Gemini unavailable
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            response = self.client.generate_content(
                prompt,
                stream=False,
                safety_settings=self._get_safety_settings()
            )
            # Ensure the response is complete
            response.resolve()
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            # Log error but don't raise - let caller handle fallback
            print(f"Warning: Gemini API error: {e}")
            return None
    
    def _get_safety_settings(self) -> list:
        """Get safe default safety settings for content generation."""
        try:
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            return [
                {
                    "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": HarmBlockThreshold.BLOCK_NONE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": HarmBlockThreshold.BLOCK_NONE,
                },
            ]
        except ImportError:
            return []
    
    def build_prompt(self, metadata: Dict[str, Any]) -> str:
        """
        Build structured prompt for Gemini from forecast metadata.
        
        Args:
            metadata: Forecast metadata (structured, no raw numbers)
            
        Returns:
            Formatted prompt string
        """
        model_used = metadata.get("model_used", "unknown")
        model_reason = metadata.get("model_reason", "N/A")
        confidence = metadata.get("confidence_level", "unknown")
        data_points = metadata.get("data_points", "N/A")
        forecast_horizon = metadata.get("forecast_horizon_days", "N/A")
        trend = metadata.get("trend", "unknown")
        seasonality = metadata.get("seasonality", "none")
        volatility = metadata.get("volatility", "unknown")
        mape = metadata.get("mape", "N/A")
        
        prompt = f"""You are a sales forecasting analyst explaining a forecast to a business user.

Forecast Metadata:
- Model Used: {model_used}
- Model Selection Reason: {model_reason}
- Confidence Level: {confidence}
- Data Points: {data_points}
- Forecast Horizon: {forecast_horizon} days
- Trend: {trend}
- Seasonality: {seasonality}
- Volatility: {volatility}
- MAPE (Mean Absolute Percentage Error): {mape}%

IMPORTANT RULES:
1. NEVER generate numerical forecast values - only explain patterns and trends
2. NEVER override or contradict the model's output
3. Focus on explaining WHY the model was chosen and what it means
4. Discuss confidence level and what factors affect it
5. Mention risks and assumptions
6. Use clear, business-friendly language
7. Keep response concise (2-3 sentences for key points)

Please provide a professional explanation of this forecast following all the rules above. Make it a comprehensive analysis in plain text format, and avoid any Markdown formatting."""
        
        return prompt
