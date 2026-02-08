'use client';

import { useState } from 'react';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email, password);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1a1f35 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      {/* Back Link */}
      <Link href="/">
        <button style={{ position: 'fixed', top: '2rem', left: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#06b6d4', transition: 'color 0.3s', fontWeight: '500', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '1rem' }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#22d3ee'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#06b6d4'}
        >
          ← Back Home
        </button>
      </Link>

      <div style={{ width: '100%', maxWidth: '28rem' }}>
        <div style={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', padding: '2.5rem', borderRadius: '1.5rem', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)', border: '1px solid #475569' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '0.5rem' }}>
              SalesForecast
            </h1>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem' }}>
              {isSignUp ? 'Create your account' : 'Sign in to your account'}
            </p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Email Field */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <label style={{ color: '#cbd5e1', fontWeight: '600', fontSize: '0.95rem' }}>Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: '100%', padding: '0.875rem 1rem', backgroundColor: '#0f172a', border: '1.5px solid #475569', borderRadius: '0.75rem', color: '#f1f5f9', fontSize: '0.95rem', transition: 'all 0.3s', fontFamily: 'DM Sans, sans-serif' }}
                onFocus={(e) => { e.currentTarget.style.borderColor = '#06b6d4'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(6, 182, 212, 0.1)'; }}
                onBlur={(e) => { e.currentTarget.style.borderColor = '#475569'; e.currentTarget.style.boxShadow = 'none'; }}
                placeholder="you@example.com"
              />
            </div>

            {/* Password Field */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <label style={{ color: '#cbd5e1', fontWeight: '600', fontSize: '0.95rem' }}>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ width: '100%', padding: '0.875rem 1rem', backgroundColor: '#0f172a', border: '1.5px solid #475569', borderRadius: '0.75rem', color: '#f1f5f9', fontSize: '0.95rem', transition: 'all 0.3s', fontFamily: 'DM Sans, sans-serif' }}
                onFocus={(e) => { e.currentTarget.style.borderColor = '#06b6d4'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(6, 182, 212, 0.1)'; }}
                onBlur={(e) => { e.currentTarget.style.borderColor = '#475569'; e.currentTarget.style.boxShadow = 'none'; }}
                placeholder="••••••••"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: '#fca5a5', fontSize: '0.9rem' }}>
                {error}
              </div>
            )}

            {/* Primary Button */}
            <button
              type="submit"
              disabled={loading}
              style={{ width: '100%', padding: '1rem', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', color: 'white', fontWeight: '600', borderRadius: '0.75rem', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.3s', fontSize: '0.95rem', opacity: loading ? 0.6 : 1 }}
              onMouseEnter={(e) => !loading && (e.currentTarget.style.transform = 'translateY(-2px)')}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              {loading ? 'Loading...' : isSignUp ? 'Create Account' : 'Sign In'}
            </button>

            {/* Toggle Button */}
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError('');
              }}
              style={{ width: '100%', padding: '1rem', backgroundColor: 'transparent', border: '2px solid #06b6d4', color: '#06b6d4', fontWeight: '500', borderRadius: '0.75rem', cursor: 'pointer', transition: 'all 0.3s', fontSize: '0.95rem' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              {isSignUp ? '← Back to Sign In' : 'Create New Account →'}
            </button>
          </form>
        </div>

        {/* Footer Text */}
        <p style={{ textAlign: 'center', marginTop: '2rem', color: '#64748b', fontSize: '0.875rem' }}>
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}

