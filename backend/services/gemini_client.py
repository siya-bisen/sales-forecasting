"""
Gemini API client for generating AI explanations.
Handles API calls, error handling, and graceful fallback.
Enhanced to include CSV data and sales-specific analysis.
"""
from typing import Dict, Any, Optional, List
import os
import io
import pandas as pd

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiClient:
    """Client for Gemini API with error handling and CSV support."""
    
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
    
    def generate_explanation(self, prompt: str, csv_data: Optional[str] = None) -> Optional[str]:
        """
        Generate explanation using Gemini API with optional CSV context.
        
        Args:
            prompt: Structured prompt for Gemini
            csv_data: Optional CSV data as string for richer analysis
            
        Returns:
            Explanation string, or None if Gemini unavailable
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            # Build request with CSV context if provided
            content_parts = []
            
            # Add CSV data context if available
            if csv_data:
                csv_summary = self._summarize_csv(csv_data)
                content_parts.append(f"CSV Data Summary:\n{csv_summary}\n\n")
            
            # Add the main prompt
            content_parts.append(prompt)
            full_content = "".join(content_parts)
            # Ask Gemini to respond in JSON
            full_content += "\n\nRespond ONLY in JSON format with key-value pairs for: business_context, model_insights, trend_seasonality, risks_volatility, recommendations."
            response = self.client.generate_content(
                full_content,
                stream=False,
                safety_settings=self._get_safety_settings()
            )
            response.resolve()
            if response and hasattr(response, 'text') and response.text:
                import json
                try:
                    return json.loads(response.text.strip())
                except Exception:
                    return {"analysis": response.text.strip()}
            return None
        except Exception as e:
            # Log error but don't raise - let caller handle fallback
            print(f"Warning: Gemini API error: {e}")
            return None
    
    def _summarize_csv(self, csv_data: str) -> str:
        """
        Create a summary of CSV data for context.
        
        Args:
            csv_data: CSV data as string
            
        Returns:
            Formatted summary of the data
        """
        try:
            df = pd.read_csv(io.StringIO(csv_data))
            
            summary = f"Records: {len(df)}\n"
            summary += f"Columns: {', '.join(df.columns)}\n"
            summary += f"Date Range: {df.get('Date', df.iloc[:, 0]).iloc[0]} to {df.get('Date', df.iloc[:, 0]).iloc[-1]}\n"
            
            # Add numeric column stats
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                summary += f"{col} - Min: {df[col].min():.2f}, Max: {df[col].max():.2f}, Avg: {df[col].mean():.2f}\n"
            
            # Add categorical information
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if col != 'Date':
                    unique_vals = df[col].unique()
                    if len(unique_vals) <= 10:
                        summary += f"{col}: {', '.join(map(str, unique_vals))}\n"
            
            return summary
        except Exception as e:
            return f"Could not parse CSV: {str(e)}"
    
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
    
    def build_prompt(self, metadata: Dict[str, Any], include_csv_insights: bool = True) -> str:
        """
        Build structured prompt for Gemini from forecast metadata.
        
        Args:
            metadata: Forecast metadata (structured, no raw numbers)
            include_csv_insights: Whether to include insights from CSV data analysis
            
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
        
        # Sales-specific metadata
        product_category = metadata.get("product_category", "Not available")
        regions = metadata.get("regions", "Not available")
        customer_segments = metadata.get("customer_segments", "Not available")
        avg_marketing_spend = metadata.get("avg_marketing_spend", "Not available")
        promotion_impact = metadata.get("promotion_impact", "Not available")
        
        prompt = f"""You are an expert sales forecasting analyst explaining a forecast to business stakeholders.

FORECAST ANALYSIS:
- Model Used: {model_used}
- Model Selection Reason: {model_reason}
- Confidence Level: {confidence}
- Data Points Analyzed: {data_points}
- Forecast Horizon: {forecast_horizon} days
- Trend: {trend}
- Seasonality: {seasonality}
- Volatility: {volatility}
- Forecast Accuracy (MAPE): {mape}%

SALES BUSINESS CONTEXT:
- Product Categories: {product_category}
- Geographic Regions: {regions}
- Customer Segments: {customer_segments}
- Average Marketing Spend: {avg_marketing_spend}
- Promotion Impact: {promotion_impact}

ANALYSIS GUIDELINES:
1. Provide business-focused insights on sales performance
2. Explain forecast implications for revenue, inventory, and resource planning
3. Discuss seasonal patterns and regional variations
4. Address risks, opportunities, and actionable recommendations
5. DO NOT generate specific forecast numbers - only explain trends and patterns
6. DO NOT contradict the model's output
7. Use clear, non-technical language suitable for executives
8. Highlight factors that could impact forecast accuracy (market conditions, seasonality, promotions)
9. Suggest key metrics to monitor
10. Provide plain text format without Markdown

Generate a comprehensive professional analysis that helps stakeholders understand the forecast and make informed business decisions."""
        
        return prompt
