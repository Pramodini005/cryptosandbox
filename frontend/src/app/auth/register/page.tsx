'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { UserPlus } from 'lucide-react';

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const update = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm) { setError('Passwords do not match'); return; }
    if (form.password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setLoading(true); setError('');
    try { await register({ username: form.username, email: form.email, full_name: form.full_name, password: form.password }); router.push('/dashboard'); }
    catch (err: any) { setError(err.response?.data?.detail || 'Registration failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-3xl mx-auto mb-4">🛡️</div>
          <h1 className="text-2xl font-bold text-white">Create Account</h1>
          <p className="text-slate-400 mt-1">Join CryptoSandbox for free</p>
        </div>
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-4">
          {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
          {[{k:'username',l:'Username',t:'text',p:'john_doe'},{k:'email',l:'Email',t:'email',p:'john@example.com'},{k:'full_name',l:'Full Name',t:'text',p:'John Doe'}].map(f => (
            <div key={f.k}>
              <label className="block text-sm font-medium text-slate-300 mb-2">{f.l}</label>
              <input type={f.t} value={(form as any)[f.k]} onChange={e => update(f.k, e.target.value)} placeholder={f.p} className="cyber-input" required={f.k !== 'full_name'} />
            </div>
          ))}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
            <input type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min. 8 characters" className="cyber-input" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Confirm Password</label>
            <input type="password" value={form.confirm} onChange={e => update('confirm', e.target.value)} placeholder="Repeat password" className="cyber-input" required />
          </div>
          <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-purple-500 hover:bg-purple-400 text-white font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50">
            {loading ? <><LoadingSpinner size={16} /> Creating account...</> : <><UserPlus size={16} /> Register</>}
          </button>
          <p className="text-center text-sm text-slate-500">Have an account? <Link href="/auth/login" className="text-emerald-400 hover:text-emerald-300">Sign In</Link></p>
        </form>
      </div>
    </div>
  );
}
