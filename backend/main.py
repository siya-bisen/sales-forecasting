"""
FastAPI main application for Sales Forecasting Copilot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import forecast, explain
from services.forecasting import initialize_explanation_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Sales Forecasting Copilot API",
    description="MVP Sales Forecasting API with multiple models and AI explanations",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    # Initialize explanation engine with Gemini API key (if available)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    initialize_explanation_engine(gemini_api_key)
    
    # Initialize Gemini in explain route for backward compatibility
    if gemini_api_key:
        explain.initialize_gemini(gemini_api_key)

# Include routers
app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(explain.router, prefix="/api", tags=["explain"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sales Forecasting Copilot API",
        "version": "1.0.0",
        "endpoints": {
            "forecast": "/api/forecast",
            "explain": "/api/explain"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
