'use client';

import { useState } from 'react';
import Papa from 'papaparse';
import { ForecastDataPoint } from '@/lib/api';

interface CSVUploadProps {
  onDataUpload: (data: ForecastDataPoint[]) => void;
}

export default function CSVUpload({ onDataUpload }: CSVUploadProps) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError('');
    setLoading(true);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const data: ForecastDataPoint[] = [];
          
          for (const row of results.data as any[]) {
            const date = row.date || row.Date || row.DATE;
            const sales = row.sales || row.Sales || row.SALES || row.value || row.Value || row.VALUE;

            if (!date || sales === undefined || sales === null || sales === '') {
              continue;
            }

            const salesValue = parseFloat(sales);
            if (isNaN(salesValue) || salesValue < 0) {
              throw new Error(`Invalid sales value: ${sales}`);
            }

            // Validate date format
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
              throw new Error(`Invalid date format: ${date}`);
            }

            const dataPoint: ForecastDataPoint = {
              date: dateObj.toISOString().split('T')[0], // Format as YYYY-MM-DD
              sales: salesValue,
            };

            // Include optional sales context columns if present
            const contextFields = [
              'ProductCategory', 'Region', 'CustomerSegment',
              'MarketingSpend', 'IsPromotion', 'Quantity', 'UnitPrice'
            ];
            
            contextFields.forEach(field => {
              const value = row[field];
              if (value !== undefined && value !== null && value !== '') {
                dataPoint[field] = isNaN(parseFloat(value)) ? value : parseFloat(value);
              }
            });

            data.push(dataPoint);
          }

          if (data.length < 2) {
            throw new Error('At least 2 data points are required');
          }

          // Sort by date
          data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

          onDataUpload(data);
        } catch (err: any) {
          setError(err.message || 'Failed to parse CSV file');
        } finally {
          setLoading(false);
        }
      },
      error: (error) => {
        setError(`CSV parsing error: ${error.message}`);
        setLoading(false);
      },
    });
  };

  return (
    <div>
      <div style={{ position: 'relative' }}>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileUpload}
          disabled={loading}
          style={{ display: 'none' }}
          id="csv-upload"
        />
        <label 
          htmlFor="csv-upload" 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            width: '100%', 
            padding: '2rem', 
            border: '2px dashed #475569', 
            borderRadius: '1rem', 
            backgroundColor: 'rgba(30, 41, 59, 0.5)', 
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s',
            opacity: loading ? 0.6 : 1
          }}
          onMouseEnter={(e) => !loading && (e.currentTarget.style.borderColor = '#06b6d4')}
          onMouseLeave={(e) => !loading && (e.currentTarget.style.borderColor = '#475569')}
        >
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📁</div>
            <span style={{ color: '#cbd5e1', fontWeight: '500', fontSize: '1rem', display: 'block', marginBottom: '0.5rem' }}>
              {loading ? '⏳ Processing CSV...' : '👆 Click to upload CSV file or drag and drop'}
            </span>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.75rem' }}>
              Required columns: <strong>date</strong> and <strong>sales</strong>
            </p>
            <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '0.5rem' }}>
              Example: 2024-01-01, 1200
            </p>
            <p style={{ color: '#64748b', fontSize: '0.8rem', marginTop: '0.75rem', fontStyle: 'italic' }}>
              Optional: ProductCategory, Region, CustomerSegment, MarketingSpend, IsPromotion, Quantity, UnitPrice
            </p>
          </div>
        </label>
      </div>
      
      {error && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: '#fca5a5', fontSize: '0.9rem' }}>
          ❌ {error}
        </div>
      )}
      <p style={{ marginTop: '1rem', color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.6' }}>
        💡 <span style={{ fontWeight: '500', color: '#cbd5e1' }}>Tip:</span> Your CSV file should contain date and sales columns. Add optional business context columns (ProductCategory, Region, Quantity, etc.) for richer insights!
      </p>
    </div>
  );
}
