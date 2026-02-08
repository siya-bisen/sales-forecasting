import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SalesForecast Pro',
  description: 'AI-powered sales forecasting with explainable predictions',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-slate-950 text-neutral-100" style={{ fontFamily: 'DM Sans, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}