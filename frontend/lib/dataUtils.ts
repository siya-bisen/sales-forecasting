/**
 * Data utility functions for robust forecast data handling
 */

import { ForecastResponse } from './api';

/**
 * Safely parse forecast explanation whether it's string JSON or object
 */
export function parseExplanation(explanation: string | Record<string, string> | undefined): Record<string, string> {
  if (!explanation) {
    return { analysis: 'No explanation available' };
  }

  if (typeof explanation === 'string') {
    try {
      const parsed = JSON.parse(explanation);
      return typeof parsed === 'object' && parsed !== null ? parsed : { analysis: explanation };
    } catch (e) {
      // If JSON parsing fails, treat as plain text
      return { analysis: explanation };
    }
  }

  return explanation;
}

/**
 * Safely extract confidence level as percentage number
 */
export function getConfidenceLevel(confidence: string | number | undefined): number {
  if (!confidence) return 75; // Default fallback

  if (typeof confidence === 'number') {
    return Math.min(Math.max(confidence, 0), 100); // Clamp between 0-100
  }

  // Parse string like "95%" or "95"
  const num = parseInt(String(confidence).replace('%', ''), 10);
  return isNaN(num) ? 75 : Math.min(Math.max(num, 0), 100);
}

/**
 * Get color coding for confidence level
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 85) return '#16a34a'; // Green - High confidence
  if (confidence >= 70) return '#06b6d4'; // Cyan - Medium confidence
  return '#f59e0b'; // Orange - Lower confidence
}

/**
 * Get volatility classification
 */
export function getVolatilityClassification(volatility?: string | number): {
  text: string;
  color: string;
  icon: string;
} {
  const vol = typeof volatility === 'number' ? volatility : 
    volatility === 'high' ? 0.3 :
    volatility === 'moderate' ? 0.15 :
    volatility === 'low' ? 0.05 : 0.15;

  if (vol < 0.1) {
    return { text: 'Low', color: '#16a34a', icon: '📊' };
  } else if (vol < 0.25) {
    return { text: 'Moderate', color: '#06b6d4', icon: '📈' };
  }
  return { text: 'High', color: '#f59e0b', icon: '⚠️' };
}

/**
 * Normalize forecast data for consistent chart display
 */
export function normalizeForecastData(forecastResult: ForecastResponse | null): Array<{
  date: string;
  historical?: number;
  forecast?: number;
  lower?: number;
  upper?: number;
}> {
  if (!forecastResult || !forecastResult.forecast) {
    return [];
  }

  return forecastResult.forecast.map((point) => ({
    date: point.date,
    forecast: typeof point.value === 'number' ? point.value : parseFloat(String(point.value)),
    lower: typeof point.lower === 'number' ? point.lower : parseFloat(String(point.lower)),
    upper: typeof point.upper === 'number' ? point.upper : parseFloat(String(point.upper)),
  }));
}

/**
 * Validate forecast response has required fields
 */
export function validateForecastResponse(result: any): result is ForecastResponse {
  return (
    result &&
    typeof result === 'object' &&
    Array.isArray(result.forecast) &&
    result.forecast.length > 0 &&
    typeof result.model_used === 'string' &&
    typeof result.metrics === 'object' &&
    typeof result.metrics.mape === 'number'
  );
}

/**
 * Format currency values
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format percentage values
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value).toFixed(decimals)}%`;
}

/**
 * Get trend icon and color
 */
export function getTrendInfo(trend?: string): {
  icon: string;
  text: string;
  color: string;
} {
  switch (trend?.toLowerCase()) {
    case 'upward':
    case 'up':
      return { icon: '📈', text: 'Upward', color: '#16a34a' };
    case 'downward':
    case 'down':
      return { icon: '📉', text: 'Downward', color: '#ef4444' };
    case 'flat':
    case 'stable':
    default:
      return { icon: '➡️', text: 'Stable', color: '#06b6d4' };
  }
}

/**
 * Safely extract sales context, filtering empty values
 */
export function extractSalesContext(context: Record<string, any> | undefined): Array<{
  label: string;
  value: string;
}> {
  if (!context) return [];

  const labelMap: Record<string, string> = {
    product_category: 'Product Categories',
    regions: 'Geographic Regions',
    customer_segments: 'Customer Segments',
    avg_marketing_spend: 'Avg Marketing Spend',
    promotion_impact: 'Promotion Impact',
    avg_quantity: 'Avg Quantity',
    avg_unit_price: 'Avg Unit Price',
  };

  return Object.entries(context)
    .filter(([_, value]) => {
      const v = String(value || '').trim();
      return v && !['All', 'Not specified', 'Not analyzed', 'N/A', 'None', ''].includes(v);
    })
    .map(([key, value]) => ({
      label: labelMap[key] || key,
      value: String(value),
    }));
}

/**
 * Get data quality summary from notes
 */
export function getDataQualitySummary(notes: string[] | undefined): {
  warnings: string[];
  positives: string[];
  neutral: string[];
} {
  if (!notes || notes.length === 0) {
    return { warnings: [], positives: [], neutral: [] };
  }

  return {
    warnings: notes.filter((n) => n.includes('⚠️')),
    positives: notes.filter((n) => n.includes('✓')),
    neutral: notes.filter((n) => !n.includes('⚠️') && !n.includes('✓')),
  };
}
