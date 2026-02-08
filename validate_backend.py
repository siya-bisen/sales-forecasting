#!/usr/bin/env python
"""
Quick validation script for backend dependencies and imports.
"""
import sys

def test_imports():
    """Test all required imports."""
    print("Testing backend imports...")
    
    try:
        import fastapi
        print("✓ fastapi imported successfully")
    except ImportError as e:
        print(f"✗ fastapi import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✓ pydantic imported successfully")
    except ImportError as e:
        print(f"✗ pydantic import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        from prophet import Prophet
        print("✓ prophet imported successfully")
    except ImportError as e:
        print(f"✗ prophet import failed: {e}")
        return False
    
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        print("✓ statsmodels imported successfully")
    except ImportError as e:
        print(f"✗ statsmodels import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✓ google-generativeai imported successfully")
    except ImportError as e:
        print(f"✗ google-generativeai import failed: {e}")
        return False
    
    return True

def test_backend_modules():
    """Test backend module imports."""
    print("\nTesting backend modules...")
    
    try:
        from backend.services.gemini_client import GeminiClient
        print("✓ GeminiClient imported successfully")
    except ImportError as e:
        print(f"✗ GeminiClient import failed: {e}")
        return False
    
    try:
        from backend.services.explanation_engine import ExplanationEngine
        print("✓ ExplanationEngine imported successfully")
    except ImportError as e:
        print(f"✗ ExplanationEngine import failed: {e}")
        return False
    
    try:
        from backend.services.data_validation import validate_minimum_data_points
        print("✓ data_validation imported successfully")
    except ImportError as e:
        print(f"✗ data_validation import failed: {e}")
        return False
    
    try:
        from backend.services.model_eligibility import check_model_eligibility
        print("✓ model_eligibility imported successfully")
    except ImportError as e:
        print(f"✗ model_eligibility import failed: {e}")
        return False
    
    try:
        from backend.models.moving_average import MovingAverageModel
        print("✓ MovingAverageModel imported successfully")
    except ImportError as e:
        print(f"✗ MovingAverageModel import failed: {e}")
        return False
    
    try:
        from backend.models.prophet_model import ProphetModel
        print("✓ ProphetModel imported successfully")
    except ImportError as e:
        print(f"✗ ProphetModel import failed: {e}")
        return False
    
    try:
        from backend.models.sarima_model import SARIMAModel
        print("✓ SARIMAModel imported successfully")
    except ImportError as e:
        print(f"✗ SARIMAModel import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("Backend Validation Test")
    print("=" * 50)
    
    if not test_imports():
        print("\n✗ Some dependencies are missing!")
        return 1
    
    if not test_backend_modules():
        print("\n✗ Some backend modules failed to import!")
        return 1
    
    print("\n" + "=" * 50)
    print("✓ All validations passed!")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
