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
  const chartData : any[] = [];
  
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

      {/* AI Explanation Section - Structured JSON UI */}
      {forecastResult && forecastResult.explanation && (
        <div style={{ padding: '1.5rem', borderRadius: '1.25rem', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(6, 182, 212, 0.15))', border: '2px solid #8b5cf6', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h3 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: '600' }}>🤖 AI Analysis with Gemini</h3>
            <span style={{ fontSize: '0.75rem', fontWeight: '600', padding: '0.5rem 0.875rem', borderRadius: '9999px', backgroundColor: 'rgba(139, 92, 246, 0.2)', color: '#a78bfa' }}>
              ✨ AI-Powered
            </span>
          </div>
          {/* Display Gemini explanation as JSON sections */}
          {(() => {
            const explanation = forecastResult.explanation;
            const keys = [
              'business_context',
              'model_insights',
              'trend_seasonality',
              'risks_volatility',
              'recommendations',
              'analysis', // fallback
            ];
            const labels = {
              business_context: 'Business Context',
              model_insights: 'Model Insights',
              trend_seasonality: 'Trend & Seasonality',
              risks_volatility: 'Risks & Volatility',
              recommendations: 'Recommendations',
              analysis: 'Analysis',
            };
            const sections = keys
              .filter((key) => explanation[key])
              .map((key) => ({ label: labels[key], content: explanation[key] }));
            if (sections.length === 0) {
              sections.push({ label: 'Analysis', content: JSON.stringify(explanation) });
            }
            return (
              <div>
                {sections.map((section, idx) => (
                  <div key={idx} style={{ marginBottom: '1rem' }}>
                    <h5 style={{ color: '#a78bfa', fontWeight: '600', fontSize: '1rem', marginBottom: '0.5rem' }}>{section.label}</h5>
                    <p style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: '1.6' }}>{section.content}</p>
                  </div>
                ))}
                <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(139, 92, 246, 0.3)' }}>
                  <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>✓ Powered by Google Gemini AI</p>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Sales Context Section */}
      {forecastResult && forecastResult.sales_context && (
        <div style={{ padding: '1.5rem', borderRadius: '1.25rem', backgroundColor: 'rgba(34, 197, 94, 0.08)', border: '1px solid #22c55e', marginBottom: '1.5rem' }}>
          <h4 style={{ color: '#22c55e', fontWeight: '700', marginBottom: '1rem', fontSize: '1.15rem', letterSpacing: '0.02em' }}>📊 Sales Business Context</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem' }}>
            {Object.entries(forecastResult.sales_context)
              .filter(([_, value]) => value && !['All', 'Not specified', 'Not analyzed', 'N/A'].includes(value))
              .map(([key, value]) => {
                const labelMap: { [key: string]: string } = {
                  product_category: 'Product Categories',
                  regions: 'Geographic Regions',
                  customer_segments: 'Customer Segments',
                  avg_marketing_spend: 'Avg Marketing Spend',
                  promotion_impact: 'Promotion Impact',
                  avg_quantity: 'Avg Quantity',
                  avg_unit_price: 'Avg Unit Price',
                };
                return (
                  <div key={key} style={{ minWidth: '220px', flex: '1 1 220px', padding: '1rem', backgroundColor: 'rgba(34, 197, 94, 0.13)', borderRadius: '1rem', boxShadow: '0 2px 8px rgba(34,197,94,0.08)' }}>
                    <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.35rem' }}>{labelMap[key] || key}</div>
                    <div style={{ color: '#16a34a', fontSize: '1.05rem', fontWeight: '700' }}>{value}</div>
                  </div>
                );
              })}
            {/* Fallback if all values are default */}
            {Object.values(forecastResult.sales_context).every(
              (v) => !v || ['All', 'Not specified', 'Not analyzed', 'N/A'].includes(v)
            ) && (
              <div style={{ width: '100%', padding: '1.5rem', backgroundColor: 'rgba(34, 197, 94, 0.08)', borderRadius: '1rem', border: '1.5px dashed #22c55e' }}>
                <div style={{ color: '#cbd5e1', fontSize: '1rem', marginBottom: '0.75rem', fontWeight: '600' }}>✨ Enhance Your Forecast with Business Context</div>
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1rem', lineHeight: '1.5' }}>
                  Your CSV file only contains date and sales data. Add optional business context columns to get deeper AI insights!
                </p>
                <div style={{ backgroundColor: 'rgba(34, 197, 94, 0.15)', padding: '1rem', borderRadius: '0.75rem', marginBottom: '1rem' }}>
                  <p style={{ color: '#22c55e', fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.5rem' }}>📋 Suggested columns to add:</p>
                  <ul style={{ color: '#cbd5e1', fontSize: '0.85rem', marginLeft: '1.5rem', lineHeight: '1.6' }}>
                    <li><strong>ProductCategory</strong>: Types of products (e.g., Electronics, Software)</li>
                    <li><strong>Region</strong>: Geographic regions (e.g., North America, Europe, Asia)</li>
                    <li><strong>CustomerSegment</strong>: Customer types (e.g., Enterprise, SMB)</li>
                    <li><strong>MarketingSpend</strong>: Marketing investment amount</li>
                    <li><strong>IsPromotion</strong>: Promotion active (1=yes, 0=no)</li>
                    <li><strong>Quantity</strong>: Number of units sold</li>
                    <li><strong>UnitPrice</strong>: Price per unit</li>
                  </ul>
                </div>
                <p style={{ color: '#64748b', fontSize: '0.8rem', fontStyle: 'italic' }}>
                  With these columns, the AI will analyze product mix, regional trends, customer behavior, marketing ROI, and promotion effectiveness!
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Data Quality Notes */}
      {forecastResult && forecastResult.notes && (
        <div style={{ padding: '1.5rem', borderRadius: '1.25rem', backgroundColor: 'rgba(6, 182, 212, 0.08)', border: '1px solid #06b6d4', marginBottom: '1.5rem' }}>
          <h4 style={{ color: '#06b6d4', fontWeight: '700', marginBottom: '1rem', fontSize: '1.15rem', letterSpacing: '0.02em' }}>📋 Data Quality & Insights</h4>
          {forecastResult.notes.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {forecastResult.notes.map((note, idx) => {
                // Parse the note to identify type (⚠️, ✓, 📈, etc.)
                const firstChar = note.charAt(0);
                const isWarning = note.includes('⚠️');
                const isPositive = note.includes('✓');
                const isInfo = !isWarning && !isPositive;
                
                let bgColor = 'rgba(6, 182, 212, 0.15)';
                let borderColor = '#06b6d4';
                let iconColor = '#06b6d4';
                
                if (isWarning) {
                  bgColor = 'rgba(245, 158, 11, 0.15)';
                  borderColor = '#f59e0b';
                  iconColor = '#f59e0b';
                } else if (isPositive) {
                  bgColor = 'rgba(34, 197, 94, 0.15)';
                  borderColor = '#22c55e';
                  iconColor = '#22c55e';
                }
                
                return (
                  <div
                    key={idx}
                    style={{
                      padding: '0.875rem 1rem',
                      borderRadius: '0.875rem',
                      backgroundColor: bgColor,
                      border: `1px solid ${borderColor}`,
                      color: '#cbd5e1',
                      fontSize: '0.9rem',
                      lineHeight: '1.6',
                      display: 'flex',
                      gap: '0.75rem',
                      alignItems: 'flex-start'
                    }}
                  >
                    <span style={{ color: iconColor, flexShrink: 0, marginTop: '0.05rem' }}>
                      {note.split(' ')[0]}
                    </span>
                    <span>{note.substring(note.indexOf(' ') + 1)}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ padding: '1rem', borderRadius: '0.875rem', backgroundColor: 'rgba(6, 182, 212, 0.15)', border: '1px solid #06b6d4', color: '#cbd5e1', fontSize: '0.9rem' }}>
              ✓ Data quality analysis complete
            </div>
          )}
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(6, 182, 212, 0.3)' }}>
            <p style={{ color: '#64748b', fontSize: '0.8rem', margin: 0 }}>
              💡 <strong style={{ color: '#cbd5e1' }}>Tip:</strong> These insights are based on your uploaded data. Review notes marked with ⚠️ to understand data characteristics affecting forecast accuracy.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

