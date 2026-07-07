'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { asymmetricApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Key, Lock, Unlock, PenTool, CheckCircle, XCircle } from 'lucide-react';

const TABS = ['keygen', 'encrypt', 'sign'] as const;

export default function AsymmetricLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<typeof TABS[number]>('keygen');
  const [algo, setAlgo] = useState('RSA');
  const [keySize, setKeySize] = useState(2048);
  const [curve, setCurve] = useState('P-256');
  const [keys, setKeys] = useState<{ public_key: string; private_key: string; fingerprint: string } | null>(null);
  const [encPlaintext, setEncPlaintext] = useState('Secret message for Bob');
  const [encResult, setEncResult] = useState('');
  const [decResult, setDecResult] = useState('');
  const [signMessage, setSignMessage] = useState('This document is authentic.');
  const [signature, setSignature] = useState('');
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateKeys = async () => {
    setLoading(true); setError(''); setKeys(null);
    try {
      const res = await asymmetricApi.generateKeys({ algorithm: algo, key_size: keySize, curve });
      setKeys(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || 'Key generation failed'); }
    finally { setLoading(false); }
  };

  const encrypt = async () => {
    if (!keys) { setError('Generate keys first'); return; }
    setLoading(true); setError('');
    try {
      const res = await asymmetricApi.encrypt({ plaintext: encPlaintext, public_key: keys.public_key });
      setEncResult(res.data.ciphertext);
    } catch (err: any) { setError(err.response?.data?.detail || 'Encryption failed'); }
    finally { setLoading(false); }
  };

  const decrypt = async () => {
    if (!keys || !encResult) return;
    setLoading(true); setError('');
    try {
      const res = await asymmetricApi.decrypt({ ciphertext: encResult, private_key: keys.private_key });
      setDecResult(res.data.plaintext);
    } catch (err: any) { setError(err.response?.data?.detail || 'Decryption failed'); }
    finally { setLoading(false); }
  };

  const sign = async () => {
    if (!keys) { setError('Generate keys first'); return; }
    setLoading(true); setError(''); setSignature(''); setVerifyResult(null);
    try {
      const res = await asymmetricApi.sign({ message: signMessage, private_key: keys.private_key, algorithm: algo });
      setSignature(res.data.signature);
    } catch (err: any) { setError(err.response?.data?.detail || 'Signing failed'); }
    finally { setLoading(false); }
  };

  const verify = async (tampered?: boolean) => {
    if (!keys || !signature) return;
    setLoading(true); setError('');
    try {
      const msg = tampered ? signMessage + ' (tampered)' : signMessage;
      const res = await asymmetricApi.verify({ message: msg, signature, public_key: keys.public_key, algorithm: algo });
      setVerifyResult(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || 'Verify failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Asymmetric Cryptography Lab" subtitle="RSA, ECC, and Ed25519 key operations" badge="RSA · ECC · Ed25519" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex gap-2">
              {TABS.map(t => (<button key={t} onClick={() => setTab(t)} className={`lab-tab capitalize ${tab === t ? 'active' : ''}`}>{t === 'keygen' ? '1. Key Generation' : t === 'encrypt' ? '2. Encrypt / Decrypt' : '3. Sign / Verify'}</button>))}
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {/* Key Gen */}
            {tab === 'keygen' && (
              <div className="glass-card p-6 space-y-5">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                    <select value={algo} onChange={e => setAlgo(e.target.value)} className="cyber-select">
                      {['RSA', 'ECC', 'Ed25519'].map(a => <option key={a}>{a}</option>)}
                    </select>
                  </div>
                  {algo === 'RSA' && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Key Size</label>
                      <select value={keySize} onChange={e => setKeySize(Number(e.target.value))} className="cyber-select">
                        {[1024, 2048, 4096].map(k => <option key={k} value={k}>{k}-bit</option>)}
                      </select>
                    </div>
                  )}
                  {algo === 'ECC' && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Curve</label>
                      <select value={curve} onChange={e => setCurve(e.target.value)} className="cyber-select">
                        {['P-256', 'P-384', 'P-521'].map(c => <option key={c}>{c}</option>)}
                      </select>
                    </div>
                  )}
                </div>
                <button onClick={generateKeys} disabled={loading} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Generating...</> : <><Key size={16} /> Generate Key Pair</>}
                </button>
                {keys && (
                  <div className="space-y-4 pt-4 border-t border-white/5">
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/10">
                      <Key size={16} className="text-cyan-400" />
                      <span className="text-sm text-slate-400">Fingerprint:</span>
                      <span className="text-sm font-mono text-cyan-300 truncate">{keys.fingerprint}</span>
                    </div>
                    <ResultBox label="Public Key (PEM)" value={keys.public_key} rows={5} badge="Share this" />
                    <ResultBox label="Private Key (PEM)" value={keys.private_key} rows={7} badge="Keep Secret!" />
                  </div>
                )}
              </div>
            )}

            {/* Encrypt */}
            {tab === 'encrypt' && (
              <div className="space-y-4">
                {!keys && <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-sm">⚠️ Generate keys first in the Key Generation tab.</div>}
                <div className="glass-card p-6 space-y-4">
                  <h3 className="text-sm font-semibold text-slate-300">Encrypt with Public Key (RSA OAEP)</h3>
                  <textarea value={encPlaintext} onChange={e => setEncPlaintext(e.target.value)} rows={3} className="code-area" placeholder="Message to encrypt..." />
                  <button onClick={encrypt} disabled={loading || !keys} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <LoadingSpinner size={16} /> : <Lock size={16} />} Encrypt with Public Key
                  </button>
                  {encResult && <ResultBox label="Ciphertext (Base64)" value={encResult} badge="Encrypted" />}
                </div>
                {encResult && (
                  <div className="glass-card p-6 space-y-4">
                    <h3 className="text-sm font-semibold text-slate-300">Decrypt with Private Key</h3>
                    <button onClick={decrypt} disabled={loading || !keys} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                      {loading ? <LoadingSpinner size={16} /> : <Unlock size={16} />} Decrypt with Private Key
                    </button>
                    {decResult && <ResultBox label="Decrypted Plaintext" value={decResult} badge="Decrypted" />}
                  </div>
                )}
              </div>
            )}

            {/* Sign */}
            {tab === 'sign' && (
              <div className="space-y-4">
                {!keys && <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-sm">⚠️ Generate keys first in the Key Generation tab.</div>}
                <div className="glass-card p-6 space-y-4">
                  <h3 className="text-sm font-semibold text-slate-300">Sign Message with Private Key</h3>
                  <textarea value={signMessage} onChange={e => setSignMessage(e.target.value)} rows={3} className="code-area" />
                  <button onClick={sign} disabled={loading || !keys} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <LoadingSpinner size={16} /> : <PenTool size={16} />} Sign Message
                  </button>
                  {signature && <ResultBox label="Digital Signature (Base64)" value={signature} badge="Signed" rows={3} />}
                </div>
                {signature && (
                  <div className="glass-card p-6 space-y-4">
                    <h3 className="text-sm font-semibold text-slate-300">Verify Signature</h3>
                    <div className="flex gap-3">
                      <button onClick={() => verify(false)} disabled={loading} className="flex-1 py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 text-sm disabled:opacity-50">
                        {loading ? <LoadingSpinner size={14} /> : <CheckCircle size={14} />} Verify (original)
                      </button>
                      <button onClick={() => verify(true)} disabled={loading} className="flex-1 py-3 rounded-xl bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-400 font-semibold flex items-center justify-center gap-2 text-sm transition-all disabled:opacity-50">
                        {loading ? <LoadingSpinner size={14} /> : <XCircle size={14} />} Verify (tampered)
                      </button>
                    </div>
                    {verifyResult && (
                      <div className={`p-4 rounded-xl border flex items-center gap-3 ${verifyResult.valid ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                        {verifyResult.valid ? <CheckCircle size={20} /> : <XCircle size={20} />}
                        <span className="font-semibold">{verifyResult.message}</span>
                      </div>
                    )}
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
