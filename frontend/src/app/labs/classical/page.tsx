'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { classicalApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { BookOpen, Lock, Unlock } from 'lucide-react';

const CIPHERS = [
  { id: 'Caesar', name: 'Caesar Cipher', desc: 'Shift each letter by a fixed number. Julius Caesar used shift 3.', needsShift: true, needsKey: false },
  { id: 'Vigenere', name: 'Vigenere Cipher', desc: 'Polyalphabetic substitution using a repeating keyword.', needsShift: false, needsKey: true },
  { id: 'Playfair', name: 'Playfair Cipher', desc: '5x5 matrix cipher that encrypts digraphs (letter pairs).', needsShift: false, needsKey: true },
  { id: 'OTP', name: 'One-Time Pad', desc: 'Perfectly secret cipher. Random key XORed with plaintext. Unbreakable if key used once.', needsShift: false, needsKey: false },
  { id: 'RailFence', name: 'Rail Fence Cipher', desc: 'Transposition cipher that writes text in a zigzag pattern across rails.', needsShift: false, needsKey: false, needsRails: true },
  { id: 'Columnar', name: 'Columnar Transposition', desc: 'Text written row by row, read column by column based on keyword order.', needsShift: false, needsKey: true },
];

export default function ClassicalLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [selected, setSelected] = useState('Caesar');
  const [tab, setTab] = useState<'encrypt' | 'decrypt'>('encrypt');
  const [plaintext, setPlaintext] = useState('HELLO WORLD');
  const [ciphertext, setCiphertext] = useState('');
  const [shift, setShift] = useState(3);
  const [key, setKey] = useState('KEY');
  const [rails, setRails] = useState(3);
  const [result, setResult] = useState<any>(null);
  const [decResult, setDecResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const selectedCipher = CIPHERS.find(c => c.id === selected)!;

  const encrypt = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await classicalApi.encrypt({ plaintext, algorithm: selected, key: selectedCipher.needsKey ? key : undefined, shift: selectedCipher.needsShift ? shift : undefined, rails: (selectedCipher as any).needsRails ? rails : undefined });
      setResult(res.data);
      setCiphertext(res.data.ciphertext);
    } catch (err: any) { setError(err.response?.data?.detail || 'Encryption failed'); }
    finally { setLoading(false); }
  };

  const decrypt = async () => {
    setLoading(true); setError(''); setDecResult(null);
    try {
      const res = await classicalApi.decrypt({ ciphertext, algorithm: selected, key: selectedCipher.needsKey ? key : undefined, shift: selectedCipher.needsShift ? shift : undefined, rails: (selectedCipher as any).needsRails ? rails : undefined });
      setDecResult(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || 'Decryption failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Classical Cryptography" subtitle="Explore historical ciphers from Caesar to One-Time Pad" badge="Historical" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Cipher selector */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {CIPHERS.map(c => (
                <button key={c.id} onClick={() => { setSelected(c.id); setResult(null); setDecResult(null); setError(''); }} className={`p-4 rounded-xl text-left transition-all border ${selected === c.id ? 'bg-yellow-500/10 border-yellow-500/30 shadow-lg shadow-yellow-500/10' : 'glass-card border-white/10 hover:border-white/20'}`}>
                  <div className="font-semibold text-sm text-white mb-1">{c.name}</div>
                  <div className="text-xs text-slate-500 line-clamp-2">{c.desc}</div>
                </button>
              ))}
            </div>

            {/* Cipher description */}
            <div className="glass-card p-5 border-l-4 border-l-yellow-500">
              <p className="text-sm text-white font-semibold">{selectedCipher.name}</p>
              <p className="text-sm text-slate-400 mt-1">{selectedCipher.desc}</p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2">
              <button onClick={() => setTab('encrypt')} className={`lab-tab ${tab === 'encrypt' ? 'active' : ''}`}><Lock size={14} className="inline mr-1.5" />Encrypt</button>
              <button onClick={() => setTab('decrypt')} className={`lab-tab ${tab === 'decrypt' ? 'active' : ''}`}><Unlock size={14} className="inline mr-1.5" />Decrypt</button>
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            <div className="glass-card p-6 space-y-4">
              {/* Key/Shift inputs */}
              {selectedCipher.needsShift && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Shift: {shift}</label>
                  <input type="range" min={1} max={25} value={shift} onChange={e => setShift(Number(e.target.value))} className="w-full accent-yellow-500" />
                  <div className="flex justify-between text-xs text-slate-600 mt-1"><span>1</span><span className="text-yellow-400 font-bold">{shift}</span><span>25</span></div>
                </div>
              )}
              {selectedCipher.needsKey && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Keyword</label>
                  <input value={key} onChange={e => setKey(e.target.value.toUpperCase())} className="cyber-input font-mono uppercase" placeholder="Enter keyword (e.g. SECRET)" />
                </div>
              )}
              {(selectedCipher as any).needsRails && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Rails: {rails}</label>
                  <input type="range" min={2} max={8} value={rails} onChange={e => setRails(Number(e.target.value))} className="w-full accent-yellow-500" />
                </div>
              )}
              {tab === 'encrypt' ? (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Plaintext</label>
                    <textarea value={plaintext} onChange={e => setPlaintext(e.target.value)} rows={3} className="code-area" />
                  </div>
                  <button onClick={encrypt} disabled={loading || !plaintext} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <LoadingSpinner size={16} /> : <Lock size={16} />} Encrypt
                  </button>
                  {result && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <ResultBox label="Ciphertext" value={result.ciphertext} badge="Encrypted" />
                      {result.key && <ResultBox label="Key Used" value={result.key} />}
                      {result.steps.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Encryption Steps (first 10)</div>
                          <div className="terminal text-xs space-y-1">
                            {result.steps.map((s: string, i: number) => (<div key={i}><span className="text-slate-600">{String(i+1).padStart(2,'0')}.</span> {s}</div>))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Ciphertext</label>
                    <textarea value={ciphertext} onChange={e => setCiphertext(e.target.value)} rows={3} className="code-area" placeholder="Paste ciphertext to decrypt..." />
                  </div>
                  <button onClick={decrypt} disabled={loading || !ciphertext} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <LoadingSpinner size={16} /> : <Unlock size={16} />} Decrypt
                  </button>
                  {decResult && <ResultBox label="Decrypted Plaintext" value={decResult.plaintext} badge="Decrypted" />}
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
