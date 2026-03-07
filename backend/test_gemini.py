#!/usr/bin/env python3
"""
Test script to verify Gemini API integration is working correctly.
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.gemini_client import GeminiClient
from services.explanation_engine import ExplanationEngine

def test_gemini_integration():
    """Test Gemini API integration."""
    print("=" * 60)
    print("TESTING GEMINI API INTEGRATION")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GEMINI_API_KEY not set in environment")
        print("   System will use rule-based fallback for explanations")
    else:
        print("\n✓ GEMINI_API_KEY found in environment")
    
    # Test GeminiClient initialization
    print("\n1. Testing GeminiClient initialization...")
    try:
        client = GeminiClient(api_key)
        print(f"   ✓ GeminiClient created")
        print(f"   ✓ Gemini available: {client.is_available}")
        print(f"   ✓ Client object: {client.client}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test CSV summarization
    print("\n2. Testing CSV summarization...")
    try:
        csv_data = """Date,Sales,ProductCategory,Region
2024-01-01,1000,Electronics,North America
2024-01-02,1500,Apparel,Europe
2024-01-03,1200,Home,APAC"""
        
        summary = client._summarize_csv(csv_data)
        print(f"   ✓ CSV summarization successful")
        print(f"   Summary preview:\n{summary[:200]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test prompt building
    print("\n3. Testing prompt building...")
    try:
        metadata = {
            "model_used": "prophet",
            "model_reason": "Strong seasonality detected",
            "confidence_level": "high",
            "data_points": 100,
            "forecast_horizon_days": 30,
            "trend": "upward",
            "seasonality": "weekly",
            "volatility": "moderate",
            "mape": 8.5,
            "product_category": "Electronics",
            "regions": "North America, Europe",
            "customer_segments": "Enterprise, SMB",
            "avg_marketing_spend": "$2,000",
            "promotion_impact": "10% lift"
        }
        
        prompt = client.build_prompt(metadata)
        print(f"   ✓ Prompt built successfully")
        print(f"   ✓ Prompt length: {len(prompt)} characters")
        print(f"   Preview:\n{prompt[:300]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test ExplanationEngine initialization
    print("\n4. Testing ExplanationEngine initialization...")
    try:
        engine = ExplanationEngine(client)
        print(f"   ✓ ExplanationEngine created")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test rule-based explanation
    print("\n5. Testing rule-based explanation generation...")
    try:
        explanation, source = engine.generate_explanation(metadata)
        print(f"   ✓ Explanation generated")
        print(f"   ✓ Source: {source}")
        print(f"   ✓ Length: {len(explanation)} characters")
        print(f"   Preview:\n{explanation[:300]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test explanation with CSV
    print("\n6. Testing explanation with CSV context...")
    try:
        explanation, source = engine.generate_explanation(metadata, csv_data=csv_data)
        print(f"   ✓ Explanation with CSV generated")
        print(f"   ✓ Source: {source}")
        print(f"   ✓ Length: {len(explanation)} characters")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    
    if api_key:
        print("\n📝 Note: Gemini API is configured. Live API calls should work.")
    else:
        print("\n📝 Note: Gemini API not configured. Using rule-based fallback.")
    
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)
