'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '@/lib/firebase';
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();
  const [user] = useAuthState(auth);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  if (!mounted) return null;

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1a1f35 100%)', color: '#f1f5f9' }}>
      {/* Navigation */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, backgroundColor: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid #334155' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0.75rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            SalesForecast Pro
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ paddingTop: '10rem', paddingBottom: '8rem', paddingLeft: '2rem', paddingRight: '2rem', maxWidth: '90rem', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
          {/* Left Content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <h1 style={{ fontSize: '4rem', fontWeight: 'bold', lineHeight: '1.1', color: '#f1f5f9', letterSpacing: '-0.02em' }}>
              Predict Your Sales <span style={{ background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>with AI</span>
            </h1>

            <p style={{ fontSize: '1.125rem', color: '#cbd5e1', lineHeight: '1.8', maxWidth: '32rem' }}>
              Leverage advanced forecasting models and AI-powered explanations to make data-driven decisions. Analyze trends, predict future sales, and stay ahead of the competition.
            </p>

            {/* Features List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {[
                { icon: '📊', text: 'Multi-Model Forecasting (Prophet, SARIMA, Moving Average)' },
                { icon: '🤖', text: 'AI-Powered Explanations with Gemini API' },
                { icon: '📈', text: 'Interactive Charts with Confidence Intervals' },
                { icon: '🔐', text: 'Secure Firebase Authentication' },
              ].map((feature, idx) => (
                <div
                  key={idx}
                  style={{ display: 'flex', gap: '1.25rem', padding: '1.25rem 1.5rem', backgroundColor: '#1e293b', borderRadius: '0.75rem', transition: 'all 0.3s', border: '1px solid #334155' }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#334155'; e.currentTarget.style.borderColor = '#06b6d4'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#1e293b'; e.currentTarget.style.borderColor = '#334155'; }}
                >
                  <span style={{ fontSize: '1.75rem', flexShrink: 0 }}>{feature.icon}</span>
                  <span style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: '1.5' }}>{feature.text}</span>
                </div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', gap: '1.5rem', paddingTop: '1rem' }}>
              <Link href="/login">
                <button style={{ padding: '1rem 2.5rem', background: 'linear-gradient(to right, #06b6d4, #8b5cf6)', color: 'white', fontWeight: '600', borderRadius: '0.75rem', border: 'none', cursor: 'pointer', boxShadow: '0 10px 30px rgba(6, 182, 212, 0.25)', transition: 'all 0.3s', fontSize: '1rem' }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  Sign In
                </button>
              </Link>
              <Link href="/login">
                <button style={{ padding: '1rem 2.5rem', backgroundColor: 'transparent', border: '2px solid #06b6d4', color: '#06b6d4', fontWeight: '600', borderRadius: '0.75rem', cursor: 'pointer', transition: 'all 0.3s', fontSize: '1rem' }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.1)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
                >
                  Create Account
                </button>
              </Link>
            </div>
          </div>

          {/* Right Visual */}
          <div style={{ position: 'relative', height: '28rem', background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(139, 92, 246, 0.15))', borderRadius: '1.25rem', padding: '2.5rem', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
            <div style={{ height: '100%', backgroundColor: 'rgba(30, 41, 59, 0.5)', backdropFilter: 'blur(4px)', borderRadius: '0.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '2rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{ height: '0.75rem', width: '66%', backgroundColor: 'rgba(6, 182, 212, 0.5)', borderRadius: '0.25rem' }}></div>
                <div style={{ height: '0.75rem', width: '50%', backgroundColor: 'rgba(139, 92, 246, 0.5)', borderRadius: '0.25rem' }}></div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    style={{ height: '0.5rem', backgroundColor: '#334155', borderRadius: '0.25rem', width: `${80 - i * 15}%` }}
                  ></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '8rem 2rem', backgroundColor: 'rgba(30, 41, 59, 0.5)' }}>
        <div style={{ maxWidth: '90rem', margin: '0 auto' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', textAlign: 'center', marginBottom: '5rem', color: '#ffffff', letterSpacing: '-0.01em' }}>
            Why Choose SalesForecast Pro?
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2.5rem' }}>
            {[
              {
                title: 'Smart Model Selection',
                description: 'Automatically selects the best forecasting model based on your data characteristics',
                icon: '🎯',
              },
              {
                title: 'AI Explanations',
                description: 'Get detailed, understandable explanations of forecasts powered by Gemini API',
                icon: '🧠',
              },
              {
                title: 'Easy Integration',
                description: 'Simple CSV upload and intuitive interface for quick insights',
                icon: '⚡',
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                style={{ padding: '2.5rem', borderRadius: '1.25rem', backgroundColor: 'rgba(30, 41, 59, 0.7)', border: '1px solid #334155', transition: 'all 0.3s' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 40px rgba(16, 185, 129, 0.1)';
                  e.currentTarget.style.borderColor = '#475569';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.borderColor = '#334155';
                }}
              >
                <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>{feature.icon}</div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.75rem', color: '#ffffff' }}>
                  {feature.title}
                </h3>
                <p style={{ color: '#cbd5e1' }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section style={{ padding: '8rem 2rem', maxWidth: '90rem', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', textAlign: 'center', marginBottom: '5rem', color: '#ffffff', letterSpacing: '-0.01em' }}>
          Get Started Today
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2.5rem', maxWidth: '45rem', margin: '0 auto' }}>
          {[
            {
              name: 'Free Trial',
              price: '0',
              features: ['Up to 100 forecasts', '7-day rolling window', 'Basic support'],
              cta: 'Get Started',
            },
            {
              name: 'Premium',
              price: '29',
              features: ['Unlimited forecasts', 'Full model suite', '24/7 priority support', 'Advanced analytics'],
              cta: 'Start Free Trial',
            },
          ].map((plan, idx) => (
            <div
              key={idx}
              style={{ padding: '2.5rem', borderRadius: '1.25rem', backgroundColor: '#1e293b', border: '2px solid #334155', transition: 'all 0.3s' }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#ffffff' }}>
                {plan.name}
              </h3>
              <div style={{ marginBottom: '1.5rem' }}>
                <span style={{ fontSize: '2rem', fontWeight: 'bold', color: idx === 1 ? '#10b981' : '#3b82f6' }}>
                  ${plan.price}
                </span>
                <span style={{ color: '#94a3b8' }}>/month</span>
              </div>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
                {plan.features.map((feature, i) => (
                  <li key={i} style={{ display: 'flex', gap: '0.5rem', color: '#cbd5e1' }}>
                    <span style={{ color: '#10b981' }}>✓</span> {feature}
                  </li>
                ))}
              </ul>
              <Link href="/login">
                <button
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', fontWeight: '600', border: 'none', cursor: 'pointer', transition: 'all 0.3s', background: idx === 1 ? 'linear-gradient(to right, #10b981, #3b82f6)' : '#334155', color: '#ffffff' }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  {plan.cta}
                </button>
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '4rem 2rem', borderTop: '1px solid #334155', backgroundColor: '#0f172a' }}>
        <div style={{ maxWidth: '90rem', margin: '0 auto', textAlign: 'center' }}>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
            © 2026 SalesForecast Pro. Powered by Advanced AI & Machine Learning.
          </p>
        </div>
      </footer>
    </div>
  );
}
