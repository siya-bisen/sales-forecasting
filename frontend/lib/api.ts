/**
 * API client for backend communication.
 * Enhanced with sales-specific context and CSV data support.
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ForecastDataPoint {
  date: string;
  sales: number;
  [key: string]: any; // Support additional sales features
}

export interface ForecastRequest {
  data: ForecastDataPoint[];
  horizon: 7 | 30 | 90;
  model: 'auto' | 'moving_average' | 'weighted_moving_average' | 'holts_linear_trend' | 'polynomial_regression' | 'exponential_smoothing' | 'seasonal_naive' | 'theta' | 'arima' | 'bayesian_structural' | 'prophet' | 'vector_ar' | 'xgboost' | 'random_forest' | 'gradient_boosting' | 'lstm' | 'sarima' | 'neural_prophet';
}

export interface SalesContext {
  product_category: string;
  regions: string;
  customer_segments: string;
  avg_marketing_spend: string;
  promotion_impact: string;
  avg_quantity: string;
  avg_unit_price: string;
}

export interface ModelInfo {
  description: string;
  mape: number;
  data_points_used: number;
  model_type?: string;
  key_features?: string[];
}

export interface ForecastResponse {
  data_points: number;
  model_used: string;
  model_reason: string;
  model_info?: ModelInfo;
  tested_models?: number;
  model_performance?: Record<string, number>;
  confidence_level: string;
  metrics: {
    mape: number;
  };
  forecast: Array<{
    date: string;
    value: number;
    lower: number;
    upper: number;
  }>;
  summary: {
    trend: string;
    seasonality: string;
    volatility: string;
  };
  explanation: string;
  explanation_source: 'gemini' | 'rule-based';
  notes: string[];
  sales_context: SalesContext;
}

export interface ExplainRequest {
  forecast_result: ForecastResponse;
  user_question?: string;
}

export interface ExplainResponse {
  explanation: string;
}

export async function generateForecast(request: ForecastRequest): Promise<ForecastResponse> {
  const response = await fetch(`${API_URL}/api/forecast`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Forecast generation failed');
  }

  return response.json();
}

export async function explainForecast(request: ExplainRequest): Promise<ExplainResponse> {
  const response = await fetch(`${API_URL}/api/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Explanation generation failed');
  }

  return response.json();
}
