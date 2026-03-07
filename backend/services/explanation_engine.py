"""
Explanation engine that orchestrates Gemini API and rule-based fallbacks.
Provides unified interface for generating forecast explanations.
Enhanced with sales-specific context and CSV data integration.
"""
from typing import Dict, Any, Tuple, Optional
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
        forecast_metadata: Dict[str, Any],
        csv_data: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate explanation using Gemini if available, otherwise use rules.
        
        Args:
            forecast_metadata: Structured metadata about the forecast
            csv_data: Optional CSV data for richer context
            
        Returns:
            Tuple of (explanation_text, source) where source is "gemini" or "rule-based"
        """
            # Try Gemini first
        if self.gemini_client.is_available:
            prompt = self.gemini_client.build_prompt(forecast_metadata)
            explanation = self.gemini_client.generate_explanation(prompt, csv_data=csv_data)
            
            if explanation:
                return explanation, "gemini"
        
        # Fall back to rule-based explanation
            if self.gemini_client.is_available:
                prompt = self.gemini_client.build_prompt(forecast_metadata)
                explanation = self.gemini_client.generate_explanation(prompt, csv_data=csv_data)
                if explanation:
                    # If Gemini returns a string, wrap in dict
                    if isinstance(explanation, str):
                        explanation = {"analysis": explanation}
                    return explanation, "gemini"
            # Fall back to rule-based explanation
            explanation = self._generate_rule_based_explanation(forecast_metadata, csv_data)
            return {"analysis": explanation}, "rule-based"
    
    def _generate_rule_based_explanation(
        self,
        metadata: Dict[str, Any],
        csv_data: Optional[str] = None
    ) -> str:
        """
        Generate rule-based explanation from structured metadata.
        
        Args:
            metadata: Forecast metadata
            csv_data: Optional CSV data for context
            
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
        
        # Sales-specific fields
        product_category = metadata.get("product_category")
        regions = metadata.get("regions")
        customer_segments = metadata.get("customer_segments")
        promotion_impact = metadata.get("promotion_impact")
        
        explanation_parts = []
        
        # Model explanation
        if model_used == "prophet":
            model_desc = (
                "Prophet was selected because it excels at handling seasonal patterns and trends in sales data. "
            )
        elif model_used == "sarima":
            model_desc = (
                "SARIMA was chosen as it's specifically designed for sales time series with "
                "both trends and seasonal components. "
            )
        elif model_used == "moving_average":
            model_desc = (
                "Moving Average was selected, providing a stable baseline for sales forecasting. "
            )
        else:
            model_desc = f"The {model_used} model was selected for this sales forecast. "
        
        explanation_parts.append(model_desc)
        
        # Reason for selection
        if model_reason:
            explanation_parts.append(f"Specifically: {model_reason}. ")
        
        # Sales-specific context
        context_parts = []
        if product_category:
            context_parts.append(f"Product categories in analysis: {product_category}")
        if regions:
            context_parts.append(f"Geographic regions: {regions}")
        if customer_segments:
            context_parts.append(f"Customer segments: {customer_segments}")
        
        if context_parts:
            explanation_parts.append("Business Context: " + "; ".join(context_parts) + ". ")
        
        # Trend explanation
        if trend == "upward":
            explanation_parts.append("The forecast indicates an upward trend in sales, suggesting revenue growth. ")
        elif trend == "downward":
            explanation_parts.append("The forecast shows a downward trend in sales, requiring attention to performance drivers. ")
        else:
            explanation_parts.append("The forecast suggests relatively stable sales performance. ")
        
        # Seasonality explanation
        if seasonality == "weekly":
            explanation_parts.append("Weekly seasonality patterns are present - prepare for cyclical demand fluctuations. ")
        elif seasonality == "monthly":
            explanation_parts.append("Monthly seasonality patterns were identified - plan inventory and resources accordingly. ")
        elif seasonality == "yearly":
            explanation_parts.append("Yearly/annual seasonality patterns affect this business - anticipate seasonal peaks and troughs. ")
        
        # Promotion impact
        if promotion_impact:
            explanation_parts.append(f"Promotion impact noted: {promotion_impact}. ")
        
        # Confidence and volatility
        if confidence == "high":
            confidence_desc = "Confidence in this forecast is high, enabling reliable sales planning and resource allocation."
        elif confidence == "medium":
            confidence_desc = (
                "Confidence is moderate - use the forecast as primary guidance, but monitor actual "
                "sales performance against predictions."
            )
        else:
            confidence_desc = "Confidence is low - treat this as a rough estimate; gather additional business context for better insights."
        
        explanation_parts.append(confidence_desc)
        
        # Volatility note
        if volatility == "high":
            explanation_parts.append(
                "High volatility detected - factor in buffer stock, flexible resourcing, and contingency plans."
            )
        elif volatility == "low":
            explanation_parts.append(
                "Low volatility indicates stable, predictable sales patterns."
            )
        
        # Data points note
        if data_points > 0:
            if data_points < 30:
                explanation_parts.append(
                    f"With {data_points} data points, consider collecting more historical data to improve forecast reliability."
                )
            elif data_points >= 365:
                explanation_parts.append(
                    f"Excellent historical coverage with {data_points} data points supports reliable long-term forecasting."
                )
        
        return " ".join(explanation_parts).strip()
