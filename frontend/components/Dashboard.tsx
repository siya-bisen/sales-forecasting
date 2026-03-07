'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useAuthState } from 'react-firebase-hooks/auth';
import CSVUpload from './CSVUpload';
import ForecastChart from './ForecastChart';
import { ForecastDataPoint, ForecastResponse } from '@/lib/api';
import { saveSalesData, getSalesData } from '@/lib/firestore';

export default function Dashboard() {
  const [user, loading] = useAuthState(auth);
  const router = useRouter();
  const [salesData, setSalesData] = useState<ForecastDataPoint[]>([]);
  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      loadSavedData();
    }
  }, [user]);

  const loadSavedData = async () => {
    if (!user) return;
    const saved = await getSalesData(user);
    if (saved) {
      setSalesData(saved);
    }
  };

  const handleDataUpload = async (data: ForecastDataPoint[]) => {
    setSalesData(data);
    if (user) {
      await saveSalesData(user, data);
    }
    setForecastResult(null);
  };

  const handleForecastGenerated = (result: ForecastResponse) => {
    setForecastResult(result);
  };

  const handleSignOut = async () => {
    await signOut(auth);
    router.push('/');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1a1f35 100%)', fontFamily: 'DM Sans, sans-serif' }}>
      {/* Header */}
      <header style={{ position: 'sticky', top: 0, zIndex: 40, backgroundColor: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid #334155' }}>
        <div style={{ maxWidth: '90rem', margin: '0 auto', padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 'bold', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '0.05em' }}>
            SalesForecast Pro
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '2.5rem', height: '2.5rem', borderRadius: '50%', background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: '600', fontSize: '1.1rem', boxShadow: '0 2px 8px rgba(139, 92, 246, 0.2)' }}>
                {user.email?.[0].toUpperCase()}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ color: '#f1f5f9', fontSize: '1rem', fontWeight: '600' }}>Welcome</span>
                <span style={{ color: '#cbd5e1', fontSize: '0.9rem', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user.email}
                </span>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              style={{ padding: '0.75rem 1.5rem', background: 'linear-gradient(to right, #ef4444, #ec4899)', color: 'white', fontWeight: '600', borderRadius: '0.75rem', border: 'none', cursor: 'pointer', transition: 'all 0.3s', fontSize: '1rem', boxShadow: '0 2px 8px rgba(236, 72, 153, 0.2)' }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main style={{ padding: '2rem', maxWidth: '90rem', margin: '0 auto' }}>
        {/* Upload Section */}
        <div style={{ borderRadius: '1.5rem', border: '1px solid #334155', background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(4px)', padding: '2.5rem', marginBottom: '2.5rem', boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)', transition: 'all 0.3s' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#06b6d4'; e.currentTarget.style.boxShadow = '0 15px 50px rgba(6, 182, 212, 0.1)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#334155'; e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)'; }}
        >
          <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#f1f5f9' }}>
            📊 Upload Sales Data
          </h2>
          <p style={{ color: '#cbd5e1', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
            Upload a CSV file with your historical sales data to generate accurate forecasts
          </p>
          <CSVUpload onDataUpload={handleDataUpload} />
          {salesData.length > 0 && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', borderRadius: '0.75rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <p style={{ color: '#86efac', fontSize: '0.95rem', fontWeight: '500' }}>
                ✓ {salesData.length} data points loaded successfully
              </p>
            </div>
          )}
        </div>

        {/* Forecast Section */}
        {salesData.length > 0 && (
          <div style={{ borderRadius: '1.5rem', border: '1px solid #334155', background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(4px)', padding: '2.5rem', boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '2rem', color: '#f1f5f9' }}>
              📈 Forecast Results
            </h2>
            <ForecastChart
              salesData={salesData}
              forecastResult={forecastResult}
              onForecastGenerated={handleForecastGenerated}
              loading={loadingForecast}
            />
          </div>
        )}

        {/* Empty State */}
        {salesData.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '4rem 2rem', borderRadius: '1.5rem', border: '2px dashed #475569', backgroundColor: 'rgba(30, 41, 59, 0.3)' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>📊</div>
            <p style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem', color: '#e2e8f0' }}>
              No data uploaded yet
            </p>
            <p style={{ color: '#94a3b8', fontSize: '1rem' }}>
              Upload a CSV file to get started with AI-powered sales forecasting
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
