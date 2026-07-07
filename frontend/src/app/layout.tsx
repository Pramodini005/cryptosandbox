import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CryptoSandbox - Cryptography Learning Platform',
  description: 'Enterprise-grade Cryptography & Cybersecurity Learning Sandbox. Learn AES, RSA, hashing, steganography, and more through interactive labs.',
  keywords: ['cryptography', 'cybersecurity', 'AES', 'RSA', 'hashing', 'steganography', 'learning'],
  authors: [{ name: 'CryptoSandbox' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0f172a',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔐</text></svg>" />
      </head>
      <body className="cyber-bg min-h-screen">
        {children}
      </body>
    </html>
  );
}
