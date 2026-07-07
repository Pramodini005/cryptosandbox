'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Lock, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try { await login(username, password); router.push('/dashboard'); }
    catch (err: any) { setError(err.response?.data?.detail || 'Login failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-3xl mx-auto mb-4">🔐</div>
          <h1 className="text-2xl font-bold text-white">Welcome back</h1>
          <p className="text-slate-400 mt-1">Sign in to CryptoSandbox</p>
        </div>
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
          {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="your_username" className="cyber-input" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
            <div className="relative">
              <input type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="cyber-input pr-10" required />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">{showPw ? <EyeOff size={16} /> : <Eye size={16} />}</button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50">
            {loading ? <><LoadingSpinner size={16} /> Signing in...</> : <><Lock size={16} /> Sign In</>}
          </button>
          <p className="text-center text-sm text-slate-500">No account? <Link href="/auth/register" className="text-emerald-400 hover:text-emerald-300">Register</Link></p>
        </form>
        <p className="text-center text-xs text-slate-600 mt-4">Or <Link href="/labs/symmetric" className="text-emerald-400/70 hover:text-emerald-400">explore labs without login</Link></p>
      </div>
    </div>
  );
}
