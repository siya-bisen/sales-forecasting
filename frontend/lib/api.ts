/**
 * API client for backend communication.
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ForecastDataPoint {
  date: string;
  sales: number;
}

export interface ForecastRequest {
  data: ForecastDataPoint[];
  horizon: 7 | 30 | 90;
  model: 'auto' | 'moving_average' | 'prophet' | 'sarima';
}

export interface ForecastResponse {
  data_points: number;
  model_used: string;
  model_reason: string;
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
