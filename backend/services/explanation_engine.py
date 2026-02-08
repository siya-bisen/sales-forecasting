"""
Explanation engine that orchestrates Gemini API and rule-based fallbacks.
Provides unified interface for generating forecast explanations.
"""
from typing import Dict, Any, Tuple
from services.gemini_client import GeminiClient


class ExplanationEngine:
    """Engine for generating explanations with Gemini fallback."""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize explanation engine.
        
        Args:
            gemini_client: Configured GeminiClient instance
        """
        self.gemini_client = gemini_client
    
    def generate_explanation(
        self,
        forecast_metadata: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Generate explanation using Gemini if available, otherwise use rules.
        
        Args:
            forecast_metadata: Structured metadata about the forecast
            
        Returns:
            Tuple of (explanation_text, source) where source is "gemini" or "rule-based"
        """
        # Try Gemini first
        if self.gemini_client.is_available:
            prompt = self.gemini_client.build_prompt(forecast_metadata)
            explanation = self.gemini_client.generate_explanation(prompt)
            
            if explanation:
                return explanation, "gemini"
        
        # Fall back to rule-based explanation
        explanation = self._generate_rule_based_explanation(forecast_metadata)
        return explanation, "rule-based"
    
    def _generate_rule_based_explanation(
        self,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate rule-based explanation from structured metadata.
        
        Args:
            metadata: Forecast metadata
            
        Returns:
            Explanation string
        """
        model_used = metadata.get("model_used", "unknown")
        model_reason = metadata.get("model_reason", "")
        confidence = metadata.get("confidence_level", "medium")
        trend = metadata.get("trend", "stable")
        seasonality = metadata.get("seasonality", "none")
        volatility = metadata.get("volatility", "moderate")
        data_points = metadata.get("data_points", 0)
        
        explanation_parts = []
        
        # Model explanation
        if model_used == "prophet":
            model_desc = (
                "Prophet was selected because it excels at handling seasonal patterns and trends. "
            )
        elif model_used == "sarima":
            model_desc = (
                "SARIMA was chosen as it's specifically designed for time series with "
                "both trends and seasonal components. "
            )
        elif model_used == "moving_average":
            model_desc = (
                "Moving Average was selected, providing a stable and straightforward baseline forecast. "
            )
        else:
            model_desc = f"The {model_used} model was selected. "
        
        explanation_parts.append(model_desc)
        
        # Reason for selection
        if model_reason:
            explanation_parts.append(f"Specifically: {model_reason}. ")
        
        # Trend explanation
        if trend == "upward":
            explanation_parts.append("The forecast indicates an upward trend in sales. ")
        elif trend == "downward":
            explanation_parts.append("The forecast shows a downward trend in sales. ")
        else:
            explanation_parts.append("The forecast suggests relatively stable sales with minimal trend. ")
        
        # Seasonality explanation
        if seasonality == "weekly":
            explanation_parts.append("Weekly seasonality patterns were detected in your historical data. ")
        elif seasonality == "monthly":
            explanation_parts.append("Monthly seasonality patterns were identified in your data. ")
        elif seasonality == "yearly":
            explanation_parts.append("Yearly/annual seasonality patterns were detected. ")
        
        # Confidence and volatility
        if confidence == "high":
            confidence_desc = "Confidence in this forecast is high, indicating reliable predictions."
        elif confidence == "medium":
            confidence_desc = (
                "Confidence is moderate - the forecast should be used as guidance "
                "alongside other business factors."
            )
        else:
            confidence_desc = "Confidence is low - consider this forecast as a rough estimate only."
        
        explanation_parts.append(confidence_desc)
        
        # Volatility note
        if volatility == "high":
            explanation_parts.append(
                "Note: High volatility in historical data may affect forecast accuracy."
            )
        
        # Data points note
        if data_points > 0:
            if data_points < 30:
                explanation_parts.append(
                    f"With {data_points} data points, more historical data would improve accuracy."
                )
        
        return " ".join(explanation_parts).strip()
