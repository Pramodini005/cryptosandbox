'use client';
import { useState, useEffect } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { passwordApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Shield, RefreshCw, Hash, CheckCircle, XCircle } from 'lucide-react';
import { PasswordAnalysis } from '@/types';

const KDF_ALGOS = ['bcrypt', 'argon2', 'pbkdf2', 'scrypt'];

export default function PasswordLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<'analyze' | 'hash' | 'generate'>('analyze');
  const [password, setPassword] = useState('');
  const [analysis, setAnalysis] = useState<PasswordAnalysis | null>(null);
  const [kdfAlgo, setKdfAlgo] = useState('bcrypt');
  const [hashResult, setHashResult] = useState('');
  const [verifyPw, setVerifyPw] = useState('');
  const [verifyHash, setVerifyHash] = useState('');
  const [verifyResult, setVerifyResult] = useState<boolean | null>(null);
  const [genResult, setGenResult] = useState<any>(null);
  const [genOptions, setGenOptions] = useState({ length: 16, use_uppercase: true, use_lowercase: true, use_digits: true, use_symbols: true, exclude_ambiguous: false, passphrase: false, word_count: 4 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzePassword = async (pw?: string) => {
    const p = pw ?? password;
    if (!p) return;
    try {
      const res = await passwordApi.analyze({ password: p });
      setAnalysis(res.data);
    } catch {}
  };

  useEffect(() => {
    const timer = setTimeout(() => analyzePassword(), 400);
    return () => clearTimeout(timer);
  }, [password]);

  const hashPassword = async () => {
    setLoading(true); setError(''); setHashResult('');
    try {
      const res = await passwordApi.hash({ password, algorithm: kdfAlgo });
      setHashResult(res.data.hash);
      setVerifyHash(res.data.hash);
      setVerifyPw(password);
    } catch (err: any) { setError(err.response?.data?.detail || 'Hash failed'); }
    finally { setLoading(false); }
  };

  const verifyPassword = async () => {
    setLoading(true); setError('');
    try {
      const res = await passwordApi.verify({ password: verifyPw, hash: verifyHash, algorithm: kdfAlgo });
      setVerifyResult(res.data.valid);
    } catch (err: any) { setError(err.response?.data?.detail || 'Verify failed'); }
    finally { setLoading(false); }
  };

  const generatePassword = async () => {
    setLoading(true);
    try {
      const res = await passwordApi.generate(genOptions);
      setGenResult(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || 'Generate failed'); }
    finally { setLoading(false); }
  };

  const strengthColors: Record<string, string> = {
    'Very Weak': '#ef4444', 'Weak': '#f97316', 'Fair': '#eab308', 'Good': '#22c55e', 'Strong': '#00d4ff', 'Very Strong': '#bf5af2',
  };

  const strengthPercent: Record<string, number> = {
    'Very Weak': 10, 'Weak': 25, 'Fair': 45, 'Good': 65, 'Strong': 82, 'Very Strong': 100,
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Password Security Lab" subtitle="Analyze strength, hash with KDFs, and generate secure passwords" badge="bcrypt · Argon2" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex gap-2">
              {(['analyze', 'hash', 'generate'] as const).map(t => (
                <button key={t} onClick={() => setTab(t)} className={`lab-tab capitalize ${tab === t ? 'active' : ''}`}>{t === 'analyze' ? 'Strength Analyzer' : t === 'hash' ? 'KDF Hashing' : 'Generate Password'}</button>
              ))}
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {tab === 'analyze' && (
              <div className="glass-card p-6 space-y-6">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Password</label>
                  <input type="text" value={password} onChange={e => setPassword(e.target.value)} className="cyber-input font-mono text-lg" placeholder="Type a password to analyze..." />
                </div>
                {analysis && (
                  <div className="space-y-5">
                    {/* Strength Bar */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-slate-300">Strength</span>
                        <span className="font-bold text-sm" style={{ color: strengthColors[analysis.strength] }}>{analysis.strength}</span>
                      </div>
                      <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full strength-bar-fill rounded-full" style={{ width: `${strengthPercent[analysis.strength]}%`, background: strengthColors[analysis.strength], boxShadow: `0 0 10px ${strengthColors[analysis.strength]}60` }} />
                      </div>
                    </div>

                    {/* Stats grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { label: 'Entropy', value: `${analysis.entropy_bits.toFixed(1)} bits`, color: 'text-cyan-400' },
                        { label: 'Score', value: `${analysis.score}/100`, color: 'text-purple-400' },
                        { label: 'Length', value: `${analysis.length} chars`, color: 'text-emerald-400' },
                        { label: 'Crack Time', value: analysis.estimated_crack_time, color: 'text-orange-400' },
                      ].map(s => (
                        <div key={s.label} className="p-3 rounded-xl bg-white/3 border border-white/5 text-center">
                          <div className={`text-lg font-bold ${s.color}`}>{s.value}</div>
                          <div className="text-xs text-slate-500">{s.label}</div>
                        </div>
                      ))}
                    </div>

                    {/* Checks */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {[
                        { label: 'Uppercase', ok: analysis.has_uppercase },
                        { label: 'Lowercase', ok: analysis.has_lowercase },
                        { label: 'Numbers', ok: analysis.has_digits },
                        { label: 'Symbols', ok: analysis.has_symbols },
                        { label: 'Not Common', ok: !analysis.is_common },
                        { label: '12+ chars', ok: analysis.length >= 12 },
                      ].map(c => (
                        <div key={c.label} className={`flex items-center gap-2 p-2 rounded-lg ${c.ok ? 'bg-emerald-500/5 border border-emerald-500/15' : 'bg-red-500/5 border border-red-500/15'}`}>
                          {c.ok ? <CheckCircle size={14} className="text-emerald-400 flex-shrink-0" /> : <XCircle size={14} className="text-red-400 flex-shrink-0" />}
                          <span className={`text-xs font-medium ${c.ok ? 'text-emerald-300' : 'text-red-300'}`}>{c.label}</span>
                        </div>
                      ))}
                    </div>

                    {/* Suggestions */}
                    {analysis.suggestions.length > 0 && (
                      <div className="p-4 rounded-xl bg-orange-500/5 border border-orange-500/15">
                        <div className="text-xs font-semibold text-orange-400 mb-2">Suggestions</div>
                        <ul className="space-y-1">
                          {analysis.suggestions.map((s, i) => <li key={i} className="text-sm text-slate-400 flex items-start gap-2"><span className="text-orange-400 mt-0.5">•</span>{s}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {tab === 'hash' && (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                  <div className="grid grid-cols-4 gap-2">
                    {KDF_ALGOS.map(a => (<button key={a} onClick={() => setKdfAlgo(a)} className={`py-2 rounded-lg text-sm font-medium border transition-all ${kdfAlgo === a ? 'bg-orange-500/20 border-orange-500/30 text-orange-300' : 'border-white/10 text-slate-500 hover:text-white hover:bg-white/5'}`}>{a}</button>))}
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Password</label>
                  <input type="text" value={password} onChange={e => setPassword(e.target.value)} className="cyber-input font-mono" placeholder="Enter password to hash..." />
                </div>
                <button onClick={hashPassword} disabled={loading || !password} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Hashing...</> : <><Hash size={16} /> Hash Password</>}
                </button>
                {hashResult && <ResultBox label={`${kdfAlgo} Hash`} value={hashResult} badge="Secure Hash" rows={3} />}
                {hashResult && (
                  <div className="space-y-3 pt-4 border-t border-white/5">
                    <h4 className="text-sm font-semibold text-slate-300">Verify Password</h4>
                    <input type="text" value={verifyPw} onChange={e => setVerifyPw(e.target.value)} className="cyber-input font-mono" placeholder="Password to verify" />
                    <textarea value={verifyHash} onChange={e => setVerifyHash(e.target.value)} rows={3} className="code-area" placeholder="Paste hash here..." />
                    <button onClick={verifyPassword} disabled={loading || !verifyPw || !verifyHash} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                      {loading ? <LoadingSpinner size={16} /> : <Shield size={16} />} Verify
                    </button>
                    {verifyResult !== null && (
                      <div className={`p-4 rounded-xl border ${verifyResult ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'} flex items-center gap-3`}>
                        {verifyResult ? <CheckCircle size={20} /> : <XCircle size={20} />}
                        <span className="font-semibold">{verifyResult ? 'Password matches hash!' : 'Password does NOT match hash.'}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {tab === 'generate' && (
              <div className="glass-card p-6 space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Length: {genOptions.length}</label>
                    <input type="range" min={8} max={128} value={genOptions.length} onChange={e => setGenOptions(o => ({ ...o, length: Number(e.target.value) }))} className="w-full accent-emerald-500" />
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" id="passphrase" checked={genOptions.passphrase} onChange={e => setGenOptions(o => ({ ...o, passphrase: e.target.checked }))} className="accent-emerald-500" />
                    <label htmlFor="passphrase" className="text-sm text-slate-300 cursor-pointer">Passphrase mode</label>
                  </div>
                </div>
                {!genOptions.passphrase && (
                  <div className="grid grid-cols-2 gap-3">
                    {[{k:'use_uppercase',l:'Uppercase (A-Z)'},{k:'use_lowercase',l:'Lowercase (a-z)'},{k:'use_digits',l:'Numbers (0-9)'},{k:'use_symbols',l:'Symbols (!@#...)'},{k:'exclude_ambiguous',l:'Exclude ambiguous (0/O/l/I)'}].map(opt => (
                      <div key={opt.k} className="flex items-center gap-2">
                        <input type="checkbox" id={opt.k} checked={(genOptions as any)[opt.k]} onChange={e => setGenOptions(o => ({ ...o, [opt.k]: e.target.checked }))} className="accent-emerald-500" />
                        <label htmlFor={opt.k} className="text-sm text-slate-300 cursor-pointer">{opt.l}</label>
                      </div>
                    ))}
                  </div>
                )}
                <button onClick={generatePassword} disabled={loading} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <LoadingSpinner size={16} /> : <RefreshCw size={16} />} Generate
                </button>
                {genResult && (
                  <div className="space-y-3 pt-4 border-t border-white/5">
                    <ResultBox label="Generated Password" value={genResult.password} badge={genResult.strength} />
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-white/3 border border-white/5 text-center">
                        <div className="text-lg font-bold text-emerald-400">{genResult.entropy_bits.toFixed(1)}</div>
                        <div className="text-xs text-slate-500">bits of entropy</div>
                      </div>
                      <div className="p-3 rounded-lg bg-white/3 border border-white/5 text-center">
                        <div className="text-lg font-bold text-cyan-400">{genResult.strength}</div>
                        <div className="text-xs text-slate-500">strength</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
