"""
Main forecasting service that orchestrates model selection and forecasting.
Integrates data validation, model eligibility, and explanation generation.
"""
from typing import List, Dict, Any, Optional
from models.moving_average import MovingAverageModel
from models.prophet_model import ProphetModel
from models.sarima_model import SARIMAModel
from services.model_selector import select_best_model
from services.evaluation import calculate_confidence_level
from services.preprocessing import validate_and_normalize_data
from services.data_validation import validate_minimum_data_points, get_data_quality_notes
from services.model_eligibility import validate_model_selection, filter_eligible_models, check_model_eligibility
from services.explanation_engine import ExplanationEngine
from services.gemini_client import GeminiClient


# Global explanation engine instance (initialized from main.py)
_explanation_engine = None


def initialize_explanation_engine(gemini_api_key: Optional[str] = None) -> None:
    """
    Initialize the global explanation engine.
    Called during app startup in main.py.
    
    Args:
        gemini_api_key: Optional Gemini API key
    """
    global _explanation_engine
    gemini_client = GeminiClient(gemini_api_key)
    _explanation_engine = ExplanationEngine(gemini_client)


def create_model(model_name: str):
    """
    Factory function to create model instance.
    
    Args:
        model_name: Name of the model to create
        
    Returns:
        Model instance
    """
    if model_name == "moving_average":
        return MovingAverageModel(window=7)
    elif model_name == "prophet":
        return ProphetModel()
    elif model_name == "sarima":
        return SARIMAModel()
    else:
        raise ValueError(f"Unknown model: {model_name}")


def generate_forecast(
    data: List[Dict[str, Any]],
    horizon: int,
    model_choice: str = "auto"
) -> Dict[str, Any]:
    """
    Generate sales forecast using specified or auto-selected model.
    Enhanced with sales-specific metadata extraction.
    
    Args:
        data: List of dictionaries with 'date' and 'sales' keys (may include additional sales features)
        horizon: Number of days to forecast (7, 30, or 90)
        model_choice: Model to use ("auto", "moving_average", "prophet", "sarima")
        
    Returns:
        Dictionary with forecast results and sales context
    """
    # Validate and normalize data
    dates, values, metadata = validate_and_normalize_data(data)
    
    # Extract sales-specific metadata from input data
    sales_context = _extract_sales_context(data)
    
    # Select model
    if model_choice == "auto":
        model_name, model_reason = select_best_model(dates, values, metadata)
    else:
        model_name = model_choice
        model_reason = {"reason": f"User selected {model_choice}"}
    
    # Create and fit model
    model = create_model(model_name)
    model.fit(dates, values)
    
    # Generate forecast
    forecast_result = model.forecast(horizon)
    
    # Calculate confidence level
    # Use backtest MAPE if available, otherwise estimate
    mape = model_reason.get("mape", 10.0)  # Default to 10% if not available
    confidence = calculate_confidence_level(
        mape,
        metadata["volatility"],
        len(values)
    )
    
    # Generate forecast dates
    from datetime import datetime, timedelta
    last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
    forecast_dates = [
        (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(horizon)
    ]
    
    # Format forecast output
    forecast_output = [
        {
            "date": date,
            "value": round(value, 2),
            "lower": round(lower, 2),
            "upper": round(upper, 2)
        }
        for date, value, lower, upper in zip(
            forecast_dates,
            forecast_result["forecast"],
            forecast_result["lower"],
            forecast_result["upper"]
        )
    ]
    
    # Get model metadata for explanation
    model_metadata = model.get_metadata()
    
    # Determine trend and seasonality from forecast
    trend = forecast_result.get("trend", "stable")
    seasonality = forecast_result.get("seasonality", "none")
    if not seasonality and metadata.get("has_seasonality"):
        seasonality = "weekly"  # Default if detected but not in result
    
    # Build comprehensive result with sales context
    result = {
        "model_used": model_name,
        "model_reason": model_reason.get("reason", "Model selected"),
        "confidence_level": confidence,
        "metrics": {
            "mape": round(mape, 2)
        },
        "forecast": forecast_output,
        "summary": {
            "trend": trend,
            "seasonality": seasonality,
            "volatility": metadata["volatility"]
        },
        "metadata": {
            "data_points": len(values),
            "forecast_horizon": horizon,
            "model_metadata": model_metadata,
            # Sales-specific context
            "product_category": sales_context.get("product_category", "All"),
            "regions": sales_context.get("regions", "All"),
            "customer_segments": sales_context.get("customer_segments", "All"),
            "avg_marketing_spend": sales_context.get("avg_marketing_spend", "Not specified"),
            "promotion_impact": sales_context.get("promotion_impact", "Not analyzed"),
            "avg_quantity": sales_context.get("avg_quantity", "N/A"),
            "avg_unit_price": sales_context.get("avg_unit_price", "N/A"),
        }
    }
    
    return result


def _extract_sales_context(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract sales-specific context from the data.
    Analyzes additional columns like ProductCategory, Region, Quantity, etc.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Dictionary with sales context
    """
    if not data:
        return {}
    
    context = {}
    
    # Extract unique categories
    if "ProductCategory" in data[0]:
        categories = set(row.get("ProductCategory") for row in data if "ProductCategory" in row)
        context["product_category"] = ", ".join(sorted(filter(None, categories))) or "All"
    
    # Extract regions
    if "Region" in data[0]:
        regions = set(row.get("Region") for row in data if "Region" in row)
        context["regions"] = ", ".join(sorted(filter(None, regions))) or "All"
    
    # Extract customer segments
    if "CustomerSegment" in data[0]:
        segments = set(row.get("CustomerSegment") for row in data if "CustomerSegment" in row)
        context["customer_segments"] = ", ".join(sorted(filter(None, segments))) or "All"
    
    # Calculate average marketing spend
    if "MarketingSpend" in data[0]:
        marketing_spends = [float(row.get("MarketingSpend", 0)) for row in data if "MarketingSpend" in row]
        if marketing_spends:
            avg_spend = sum(marketing_spends) / len(marketing_spends)
            context["avg_marketing_spend"] = f"${avg_spend:.2f}"
    
    # Analyze promotion impact
    if "IsPromotion" in data[0]:
        promo_sales = []
        non_promo_sales = []
        for row in data:
            if "IsPromotion" in row and "Sales" in row:
                if row.get("IsPromotion"):
                    promo_sales.append(float(row.get("Sales", 0)))
                else:
                    non_promo_sales.append(float(row.get("Sales", 0)))
        
        if promo_sales and non_promo_sales:
            avg_promo = sum(promo_sales) / len(promo_sales)
            avg_non_promo = sum(non_promo_sales) / len(non_promo_sales)
            impact_pct = ((avg_promo - avg_non_promo) / avg_non_promo * 100) if avg_non_promo > 0 else 0
            if impact_pct > 0:
                context["promotion_impact"] = f"Promotions increase sales by ~{impact_pct:.1f}%"
            else:
                context["promotion_impact"] = f"Promotions decrease sales by ~{abs(impact_pct):.1f}%"
    
    # Calculate average quantity
    if "Quantity" in data[0]:
        quantities = [float(row.get("Quantity", 0)) for row in data if "Quantity" in row]
        if quantities:
            context["avg_quantity"] = f"{sum(quantities) / len(quantities):.1f} units"
    
    # Calculate average unit price
    if "UnitPrice" in data[0]:
        prices = [float(row.get("UnitPrice", 0)) for row in data if "UnitPrice" in row]
        if prices:
            context["avg_unit_price"] = f"${sum(prices) / len(prices):.2f}"
    
    return context
