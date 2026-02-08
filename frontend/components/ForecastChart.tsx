'use client';

import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ComposedChart,
} from 'recharts';
import { ForecastDataPoint, ForecastResponse, generateForecast, explainForecast } from '@/lib/api';

interface ForecastChartProps {
  salesData: ForecastDataPoint[];
  forecastResult: ForecastResponse | null;
  onForecastGenerated: (result: ForecastResponse) => void;
  loading: boolean;
}

export default function ForecastChart({
  salesData,
  forecastResult,
  onForecastGenerated,
  loading: externalLoading,
}: ForecastChartProps) {
  const [horizon, setHorizon] = useState<7 | 30 | 90>(30);
  const [model, setModel] = useState<'auto' | 'moving_average' | 'prophet' | 'sarima'>('auto');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateForecast = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await generateForecast({
        data: salesData,
        horizon,
        model,
      });
      onForecastGenerated(result);
    } catch (err: any) {
      setError(err.message || 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = [];
  
  // Historical data
  salesData.forEach((point) => {
    chartData.push({
      date: point.date,
      historical: point.sales,
      forecast: null,
      lower: null,
      upper: null,
    });
  });

  // Forecast data
  if (forecastResult) {
    forecastResult.forecast.forEach((point) => {
      chartData.push({
        date: point.date,
        historical: null,
        forecast: point.value,
        lower: point.lower,
        upper: point.upper,
      });
    });
  }

  return (
    <div>
      {/* Controls Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem', padding: '1.5rem', borderRadius: '1rem', backgroundColor: 'rgba(30, 41, 59, 0.5)', border: '1px solid #475569' }}>
        {/* Horizon Select */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ color: '#cbd5e1', fontWeight: '600', fontSize: '0.9rem' }}>Forecast Horizon</label>
          <select
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value) as 7 | 30 | 90)}
            style={{ padding: '0.75rem 1rem', backgroundColor: '#0f172a', border: '1.5px solid #475569', borderRadius: '0.75rem', color: '#f1f5f9', cursor: 'pointer', fontFamily: 'DM Sans, sans-serif', fontSize: '0.95rem', transition: 'all 0.3s' }}
            onFocus={(e) => e.currentTarget.style.borderColor = '#06b6d4'}
            onBlur={(e) => e.currentTarget.style.borderColor = '#475569'}
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>
        </div>

        {/* Model Select */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ color: '#cbd5e1', fontWeight: '600', fontSize: '0.9rem' }}>Forecasting Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value as any)}
            style={{ padding: '0.75rem 1rem', backgroundColor: '#0f172a', border: '1.5px solid #475569', borderRadius: '0.75rem', color: '#f1f5f9', cursor: 'pointer', fontFamily: 'DM Sans, sans-serif', fontSize: '0.95rem', transition: 'all 0.3s' }}
            onFocus={(e) => e.currentTarget.style.borderColor = '#06b6d4'}
            onBlur={(e) => e.currentTarget.style.borderColor = '#475569'}
          >
            <option value="auto">Auto (Recommended)</option>
            <option value="moving_average">Moving Average</option>
            <option value="prophet">Prophet</option>
            <option value="sarima">SARIMA</option>
          </select>
        </div>

        {/* Generate Button */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
          <button
            onClick={handleGenerateForecast}
            disabled={loading || externalLoading}
            style={{ padding: '0.75rem 1.5rem', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', color: 'white', fontWeight: '600', borderRadius: '0.75rem', border: 'none', cursor: loading || externalLoading ? 'not-allowed' : 'pointer', transition: 'all 0.3s', opacity: loading || externalLoading ? 0.6 : 1, fontSize: '0.95rem' }}
            onMouseEnter={(e) => !loading && !externalLoading && (e.currentTarget.style.transform = 'translateY(-2px)')}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
          >
            {loading || externalLoading ? '⏳ Generating...' : '⚡ Generate Forecast'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{ padding: '1rem', marginBottom: '1.5rem', borderRadius: '0.75rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', fontSize: '0.9rem' }}>
          ❌ {error}
        </div>
      )}

      {/* Forecast Info Cards */}
      {forecastResult && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
          {[
            { label: 'Data Points', value: forecastResult.data_points, icon: '📊' },
            { label: 'Model Used', value: forecastResult.model_used, icon: '🎯' },
            { label: 'Confidence', value: `${forecastResult.confidence_level}%`, icon: '📈' },
            { label: 'MAPE', value: `${forecastResult.metrics.mape}%`, icon: '📉' },
            { label: 'Trend', value: forecastResult.summary.trend, icon: '⬆️' },
          ].map((item, idx) => (
            <div
              key={idx}
              style={{ padding: '1.25rem', borderRadius: '1rem', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: '1px solid #475569', transition: 'all 0.3s', cursor: 'default' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#06b6d4'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#475569'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{item.icon}</div>
              <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500', marginBottom: '0.5rem' }}>
                {item.label}
              </div>
              <div style={{ color: '#f1f5f9', fontSize: '1rem', fontWeight: '600' }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Chart */}
      {forecastResult && (
        <div style={{ marginBottom: '2rem', padding: '1.5rem', borderRadius: '1.25rem', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: '1px solid #475569' }}>
          <h3 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem' }}>Sales Forecast Chart</h3>
          <div style={{ height: '400px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#cbd5e1' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12, fill: '#cbd5e1' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#e2e8f0',
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="historical"
                  stroke="#06b6d4"
                  fill="#06b6d4"
                  fillOpacity={0.2}
                  name="Historical Sales"
                />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  name="Forecast"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="upper"
                  stroke="#8b5cf6"
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  name="Upper Bound"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="lower"
                  stroke="#8b5cf6"
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  name="Lower Bound"
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* AI Explanation Section */}
      {forecastResult && forecastResult.explanation && (
        <div style={{ padding: '1.5rem', borderRadius: '1.25rem', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(6, 182, 212, 0.15))', border: '2px solid #8b5cf6', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h3 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: '600' }}>🤖 AI Analysis with Gemini</h3>
            <span style={{ fontSize: '0.75rem', fontWeight: '600', padding: '0.5rem 0.875rem', borderRadius: '9999px', backgroundColor: 'rgba(139, 92, 246, 0.2)', color: '#a78bfa' }}>
              ✨ AI-Powered
            </span>
          </div>
          <p style={{ color: '#cbd5e1', lineHeight: '1.6', fontSize: '0.95rem', marginBottom: '1rem' }}>
            {forecastResult.explanation}
          </p>
          <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(139, 92, 246, 0.3)' }}>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              ✓ Powered by Google Gemini AI
            </p>
          </div>
        </div>
      )}

      {/* Data Quality Notes */}
      {forecastResult && forecastResult.notes && forecastResult.notes.length > 0 && (
        <div style={{ padding: '1.5rem', borderRadius: '1.25rem', backgroundColor: 'rgba(6, 182, 212, 0.1)', border: '1px solid #06b6d4' }}>
          <h4 style={{ color: '#06b6d4', fontWeight: '600', marginBottom: '0.75rem' }}>📝 Data Quality Notes</h4>
          <ul style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: '1.6' }}>
            {forecastResult.notes.map((note, idx) => (
              <li key={idx} style={{ marginBottom: '0.5rem' }}>• {note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

