'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { symmetricApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Lock, Unlock, RefreshCw, Info } from 'lucide-react';

const ALGORITHMS = ['AES-GCM', 'AES-CBC', 'AES-CTR', 'ChaCha20', 'Fernet'];
const KEY_SIZES = [128, 192, 256];

export default function SymmetricLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<'encrypt' | 'decrypt'>('encrypt');
  const [algo, setAlgo] = useState('AES-GCM');
  const [keySize, setKeySize] = useState(256);
  const [plaintext, setPlaintext] = useState('Hello, Cryptography World! This is a secret message.');
  const [key, setKey] = useState('');
  const [ciphertext, setCiphertext] = useState('');
  const [decKey, setDecKey] = useState('');
  const [decCiphertext, setDecCiphertext] = useState('');
  const [result, setResult] = useState<any>(null);
  const [decResult, setDecResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const encrypt = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await symmetricApi.encrypt({ plaintext, algorithm: algo, key: key || undefined, key_size: keySize });
      setResult(res.data);
      setDecKey(res.data.key);
      setDecCiphertext(res.data.ciphertext);
    } catch (err: any) { setError(err.response?.data?.detail || 'Encryption failed'); }
    finally { setLoading(false); }
  };

  const decrypt = async () => {
    setLoading(true); setError(''); setDecResult(null);
    try {
      const res = await symmetricApi.decrypt({ ciphertext: decCiphertext, algorithm: algo, key: decKey });
      setDecResult(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || 'Decryption failed'); }
    finally { setLoading(false); }
  };

  const algoInfo: Record<string, { desc: string; keyLen: string; use: string }> = {
    'AES-GCM': { desc: 'Authenticated encryption — provides both confidentiality and integrity.', keyLen: '128/192/256-bit key, 96-bit nonce', use: 'TLS 1.3, HTTPS, disk encryption' },
    'AES-CBC': { desc: 'Cipher Block Chaining — each block depends on the previous.', keyLen: '128/192/256-bit key, 128-bit IV', use: 'Legacy TLS, file encryption' },
    'AES-CTR': { desc: 'Counter mode — turns AES into a stream cipher.', keyLen: '128/192/256-bit key, 128-bit nonce', use: 'Disk sector encryption, network' },
    'ChaCha20': { desc: 'Stream cipher by DJB — fast & secure on low-power devices.', keyLen: '256-bit key, 96-bit nonce', use: 'TLS 1.3 (mobile), WireGuard VPN' },
    'Fernet': { desc: 'Symmetric encryption with HMAC authentication (Python cryptography library).', keyLen: '256-bit key (base64)', use: 'Application-level encryption' },
  };

  const info = algoInfo[algo];

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Symmetric Cryptography Lab" subtitle="Encrypt and decrypt messages with modern symmetric algorithms" badge="AES · ChaCha20" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">

            {/* Algorithm Info */}
            <div className="glass-card p-5 border-l-4 border-l-emerald-500">
              <div className="flex items-start gap-3">
                <Info size={18} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-white font-medium">{algo}</p>
                  <p className="text-sm text-slate-400 mt-1">{info.desc}</p>
                  <div className="flex flex-wrap gap-3 mt-2">
                    <span className="badge badge-blue">Key: {info.keyLen}</span>
                    <span className="badge badge-green">Used in: {info.use}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Config */}
            <div className="glass-card p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                  <select value={algo} onChange={e => setAlgo(e.target.value)} className="cyber-select">
                    {ALGORITHMS.map(a => <option key={a} value={a}>{a}</option>)}
                  </select>
                </div>
                {algo !== 'Fernet' && algo !== 'ChaCha20' && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Key Size</label>
                    <select value={keySize} onChange={e => setKeySize(Number(e.target.value))} className="cyber-select">
                      {KEY_SIZES.map(k => <option key={k} value={k}>{k}-bit</option>)}
                    </select>
                  </div>
                )}
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2">
              {(['encrypt', 'decrypt'] as const).map(t => (
                <button key={t} onClick={() => setTab(t)} className={`lab-tab capitalize ${tab === t ? 'active' : ''}`}>
                  {t === 'encrypt' ? <><Lock size={14} className="inline mr-1.5" />Encrypt</> : <><Unlock size={14} className="inline mr-1.5" />Decrypt</>}
                </button>
              ))}
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {tab === 'encrypt' ? (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Plaintext</label>
                  <textarea value={plaintext} onChange={e => setPlaintext(e.target.value)} rows={4} className="code-area" placeholder="Enter message to encrypt..." />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Encryption Key (hex) — leave empty to auto-generate</label>
                  <input value={key} onChange={e => setKey(e.target.value)} className="cyber-input font-mono" placeholder="Leave blank for auto-generated key" />
                </div>
                <button onClick={encrypt} disabled={loading || !plaintext} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Encrypting...</> : <><Lock size={16} /> Encrypt</>}
                </button>
                {result && (
                  <div className="space-y-4 pt-4 border-t border-white/5">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10">
                        <div className="text-xs text-slate-500 mb-1">Algorithm</div>
                        <div className="text-sm font-bold text-emerald-400">{result.algorithm}</div>
                      </div>
                      <div className="p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/10">
                        <div className="text-xs text-slate-500 mb-1">Key Size</div>
                        <div className="text-sm font-bold text-cyan-400">{result.key_size}-bit</div>
                      </div>
                    </div>
                    <ResultBox label="Ciphertext (Base64)" value={result.ciphertext} badge="Encrypted" />
                    <ResultBox label="Encryption Key (hex)" value={result.key} />
                    {result.iv && <ResultBox label="IV / Nonce (hex)" value={result.iv} />}
                    <ResultBox label="Ciphertext (Hex)" value={result.ciphertext_hex} />
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Ciphertext (Base64)</label>
                  <textarea value={decCiphertext} onChange={e => setDecCiphertext(e.target.value)} rows={3} className="code-area" placeholder="Paste ciphertext here..." />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Decryption Key</label>
                  <input value={decKey} onChange={e => setDecKey(e.target.value)} className="cyber-input font-mono" placeholder="Paste hex key here..." />
                </div>
                <button onClick={decrypt} disabled={loading || !decCiphertext || !decKey} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Decrypting...</> : <><Unlock size={16} /> Decrypt</>}
                </button>
                {decResult && <ResultBox label="Decrypted Plaintext" value={decResult.plaintext} badge="Decrypted" />}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
