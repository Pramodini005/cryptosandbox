'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { keyExchangeApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { ArrowLeftRight, CheckCircle } from 'lucide-react';
import { DHKeyExchange } from '@/types';

export default function KeyExchangeLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [bits, setBits] = useState(512);
  const [result, setResult] = useState<DHKeyExchange | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const simulate = async () => {
    setLoading(true); setError(''); setResult(null);
    try { const r = await keyExchangeApi.diffieHellman({ bits }); setResult(r.data); }
    catch (e: any) { setError(e.response?.data?.detail || 'DH simulation failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Key Exchange Lab" subtitle="Interactive Diffie-Hellman key exchange simulation" badge="DH" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="glass-card p-5 border-l-4 border-l-cyan-500">
              <p className="text-sm font-semibold text-white">Diffie-Hellman Key Exchange</p>
              <p className="text-sm text-slate-400 mt-1">Alice and Bob each generate a private key. They exchange public keys over an insecure channel. Using mathematical properties of modular exponentiation, both arrive at the same shared secret — without ever sending it over the wire.</p>
              <div className="flex gap-2 mt-3">
                <span className="badge badge-green">Foundation of HTTPS</span>
                <span className="badge badge-blue">Perfect Forward Secrecy</span>
                <span className="badge badge-purple">No shared secret transmitted</span>
              </div>
            </div>

            <div className="glass-card p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Key Size (bits)</label>
                <div className="flex gap-3">
                  {[512, 1024].map(b => (
                    <button key={b} onClick={() => setBits(b)} className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${bits === b ? 'bg-cyan-500/20 border-cyan-500/30 text-cyan-300' : 'border-white/10 text-slate-500 hover:text-white hover:bg-white/5'}`}>{b}-bit {b === 512 ? '(fast demo)' : ''}</button>
                  ))}
                </div>
              </div>
              <button onClick={simulate} disabled={loading} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                {loading ? <><LoadingSpinner size={16} /> Simulating...</> : <><ArrowLeftRight size={16} /> Run Diffie-Hellman Simulation</>}
              </button>
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {result && (
              <div className="space-y-4">
                {/* Alice & Bob columns */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="glass-card p-5 border-t-2 border-t-emerald-500">
                    <div className="text-lg font-bold text-emerald-400 mb-3">💻 Alice</div>
                    <div className="space-y-3">
                      <div><div className="text-xs text-slate-500 mb-1">Private Key (secret)</div><div className="terminal text-xs py-2 px-3 truncate text-red-400">{result.alice_private}</div></div>
                      <div><div className="text-xs text-slate-500 mb-1">Public Key (shared)</div><div className="terminal text-xs py-2 px-3 truncate">{result.alice_public}</div></div>
                    </div>
                  </div>
                  <div className="glass-card p-5 border-t-2 border-t-cyan-500">
                    <div className="text-lg font-bold text-cyan-400 mb-3">💻 Bob</div>
                    <div className="space-y-3">
                      <div><div className="text-xs text-slate-500 mb-1">Private Key (secret)</div><div className="terminal text-xs py-2 px-3 truncate text-red-400">{result.bob_private}</div></div>
                      <div><div className="text-xs text-slate-500 mb-1">Public Key (shared)</div><div className="terminal text-xs py-2 px-3 truncate">{result.bob_public}</div></div>
                    </div>
                  </div>
                </div>

                {/* Shared params */}
                <div className="glass-card p-5">
                  <div className="text-sm font-semibold text-slate-300 mb-3">Shared Public Parameters</div>
                  <div className="grid grid-cols-2 gap-3">
                    <div><div className="text-xs text-slate-500 mb-1">Prime (p)</div><div className="terminal text-xs py-2 px-3 truncate">{result.p}</div></div>
                    <div><div className="text-xs text-slate-500 mb-1">Generator (g)</div><div className="terminal text-xs py-2 px-3">{result.g}</div></div>
                  </div>
                </div>

                {/* Shared secret */}
                <div className={`glass-card p-6 border-2 ${result.secrets_match ? 'border-emerald-500/40' : 'border-red-500/40'}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle size={24} className={result.secrets_match ? 'text-emerald-400' : 'text-red-400'} />
                    <div className="font-bold text-lg text-white">{result.secrets_match ? 'Shared Secret Established!' : 'Secret Mismatch!'}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div><div className="text-xs text-slate-500 mb-1">Alice&apos;s Computed Secret</div><div className="terminal text-xs py-2 px-3 text-emerald-300">{result.alice_shared_secret}</div></div>
                    <div><div className="text-xs text-slate-500 mb-1">Bob&apos;s Computed Secret</div><div className="terminal text-xs py-2 px-3 text-cyan-300">{result.bob_shared_secret}</div></div>
                  </div>
                  {result.secrets_match && <p className="text-sm text-slate-400 mt-3">✨ Both Alice and Bob computed the identical shared secret using only public information — without ever transmitting it!</p>}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
