'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { hashApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Hash, GitCompare, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ALGORITHMS = ['MD5', 'SHA-1', 'SHA-224', 'SHA-256', 'SHA-384', 'SHA-512', 'SHA3-256', 'SHA3-512', 'BLAKE2b', 'BLAKE2s'];
const COMPARE_SET = ['MD5', 'SHA-1', 'SHA-256', 'SHA-512', 'SHA3-256', 'BLAKE2b'];

const algoMeta: Record<string, { bits: number; secure: boolean; color: string }> = {
  'MD5': { bits: 128, secure: false, color: '#ef4444' },
  'SHA-1': { bits: 160, secure: false, color: '#f97316' },
  'SHA-224': { bits: 224, secure: true, color: '#eab308' },
  'SHA-256': { bits: 256, secure: true, color: '#22c55e' },
  'SHA-384': { bits: 384, secure: true, color: '#00d4ff' },
  'SHA-512': { bits: 512, secure: true, color: '#00d4ff' },
  'SHA3-256': { bits: 256, secure: true, color: '#bf5af2' },
  'SHA3-512': { bits: 512, secure: true, color: '#bf5af2' },
  'BLAKE2b': { bits: 512, secure: true, color: '#00ff88' },
  'BLAKE2s': { bits: 256, secure: true, color: '#00ff88' },
};

export default function HashingLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<'single' | 'compare'>('single');
  const [algo, setAlgo] = useState('SHA-256');
  const [text, setText] = useState('Hello, World!');
  const [result, setResult] = useState<any>(null);
  const [compareText, setCompareText] = useState('Hello, World!');
  const [compareResults, setCompareResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const computeHash = async () => {
    setLoading(true); setError(''); setResult(null);
    try { const res = await hashApi.compute({ text, algorithm: algo }); setResult(res.data); }
    catch (err: any) { setError(err.response?.data?.detail || 'Hash computation failed'); }
    finally { setLoading(false); }
  };

  const compareHashes = async () => {
    setLoading(true); setError(''); setCompareResults(null);
    try { const res = await hashApi.compare({ text: compareText, algorithms: COMPARE_SET }); setCompareResults(res.data); }
    catch (err: any) { setError(err.response?.data?.detail || 'Comparison failed'); }
    finally { setLoading(false); }
  };

  const chartData = compareResults ? Object.entries(compareResults.results).map(([alg, data]: any) => ({ alg, bits: data.length_bits, color: algoMeta[alg]?.color || '#94a3b8' })) : [];

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Hashing Laboratory" subtitle="Compute and compare cryptographic hash functions" badge="SHA · BLAKE2" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">

            {/* Info */}
            <div className="glass-card p-5 border-l-4 border-l-purple-500">
              <div className="flex items-start gap-3">
                <Info size={18} className="text-purple-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-white">About Cryptographic Hash Functions</p>
                  <p className="text-sm text-slate-400 mt-1">One-way functions that map arbitrary data to a fixed-size digest. Any change in input produces a completely different output (avalanche effect). Used for integrity verification, digital signatures, and password storage.</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="badge badge-green">One-Way</span>
                    <span className="badge badge-blue">Deterministic</span>
                    <span className="badge badge-purple">Avalanche Effect</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2">
              <button onClick={() => setTab('single')} className={`lab-tab ${tab === 'single' ? 'active' : ''}`}><Hash size={14} className="inline mr-1.5" />Single Hash</button>
              <button onClick={() => setTab('compare')} className={`lab-tab ${tab === 'compare' ? 'active' : ''}`}><GitCompare size={14} className="inline mr-1.5" />Compare Algorithms</button>
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {tab === 'single' ? (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                    {ALGORITHMS.map(a => {
                      const meta = algoMeta[a];
                      return (
                        <button key={a} onClick={() => setAlgo(a)} className={`px-3 py-2 rounded-lg text-xs font-medium transition-all border ${algo === a ? 'bg-purple-500/20 border-purple-500/40 text-purple-300' : 'border-white/10 text-slate-500 hover:text-white hover:bg-white/5'}`}>
                          {a}
                          <div className={`mt-1 w-1.5 h-1.5 rounded-full mx-auto ${meta?.secure ? 'bg-emerald-400' : 'bg-red-400'}`} />
                        </button>
                      );
                    })}
                  </div>
                  <p className="text-xs text-slate-600 mt-2">🟢 Secure 🔴 Deprecated/Broken</p>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Input Text</label>
                  <textarea value={text} onChange={e => setText(e.target.value)} rows={4} className="code-area" placeholder="Enter text to hash..." />
                </div>
                <button onClick={computeHash} disabled={loading || !text} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Computing...</> : <><Hash size={16} /> Compute Hash</>}
                </button>
                {result && (
                  <div className="space-y-4 pt-4 border-t border-white/5">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/10 text-center">
                        <div className="text-xs text-slate-500 mb-1">Algorithm</div>
                        <div className="text-sm font-bold text-purple-400">{result.algorithm}</div>
                      </div>
                      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10 text-center">
                        <div className="text-xs text-slate-500 mb-1">Output Length</div>
                        <div className="text-sm font-bold text-emerald-400">{result.length} bits</div>
                      </div>
                      <div className="p-4 rounded-xl bg-slate-800/50 border border-white/5 text-center">
                        <div className="text-xs text-slate-500 mb-1">Hex chars</div>
                        <div className="text-sm font-bold text-slate-300">{result.hex.length}</div>
                      </div>
                    </div>
                    <ResultBox label="Hash (Hex)" value={result.hex} badge="Digest" />
                    <ResultBox label="Binary (first 64 bits)" value={result.binary} />
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Input Text</label>
                  <textarea value={compareText} onChange={e => setCompareText(e.target.value)} rows={3} className="code-area" placeholder="Enter text to hash with all algorithms..." />
                </div>
                <button onClick={compareHashes} disabled={loading || !compareText} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Comparing...</> : <><GitCompare size={16} /> Compare All</>}
                </button>
                {compareResults && (
                  <div className="space-y-4 pt-4 border-t border-white/5">
                    <h3 className="text-sm font-semibold text-slate-300">Hash Length Comparison (bits)</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={chartData}>
                        <XAxis dataKey="alg" tick={{ fill: '#64748b', fontSize: 11 }} />
                        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                        <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(191,90,242,0.3)', borderRadius: '8px', color: '#fff' }} />
                        <Bar dataKey="bits" radius={[4, 4, 0, 0]}>
                          {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    <div className="space-y-2">
                      {Object.entries(compareResults.results).map(([alg, data]: any) => (
                        <div key={alg} className="p-3 rounded-lg bg-white/3 border border-white/5">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-semibold text-white">{alg}</span>
                            <div className="flex gap-2">
                              <span className="badge badge-purple">{data.length_bits} bits</span>
                              {algoMeta[alg]?.secure ? <span className="badge badge-green">Secure</span> : <span className="badge badge-orange">Deprecated</span>}
                            </div>
                          </div>
                          <div className="terminal text-xs py-2 px-3">{data.hash}</div>
                        </div>
                      ))}
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
