'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { asymmetricApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { PenTool, CheckCircle, XCircle, Key, AlertTriangle } from 'lucide-react';

export default function SignaturesLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [algo, setAlgo] = useState('RSA');
  const [keys, setKeys] = useState<any>(null);
  const [message, setMessage] = useState('I hereby certify that this document is authentic and has not been tampered with.');
  const [signature, setSignature] = useState('');
  const [verifyMsg, setVerifyMsg] = useState('');
  const [verifyResult, setVerifyResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generate = async () => {
    setLoading(true); setError('');
    try { const r = await asymmetricApi.generateKeys({ algorithm: algo, key_size: 2048, curve: 'P-256' }); setKeys(r.data); }
    catch (e: any) { setError(e.response?.data?.detail || 'Key gen failed'); }
    finally { setLoading(false); }
  };

  const sign = async () => {
    if (!keys) { setError('Generate keys first'); return; }
    setLoading(true); setError(''); setSignature(''); setVerifyResult(null);
    try {
      const r = await asymmetricApi.sign({ message, private_key: keys.private_key, algorithm: algo });
      setSignature(r.data.signature);
      setVerifyMsg(message);
    } catch (e: any) { setError(e.response?.data?.detail || 'Signing failed'); }
    finally { setLoading(false); }
  };

  const verify = async () => {
    if (!keys || !signature) return;
    setLoading(true); setError('');
    try {
      const r = await asymmetricApi.verify({ message: verifyMsg, signature, public_key: keys.public_key, algorithm: algo });
      setVerifyResult(r.data);
    } catch (e: any) { setError(e.response?.data?.detail || 'Verify failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Digital Signature Lab" subtitle="Sign messages and detect tampering" badge="PKI" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="glass-card p-5 border-l-4 border-l-pink-500">
              <p className="text-sm font-medium text-white">How Digital Signatures Work</p>
              <p className="text-sm text-slate-400 mt-1">A digital signature uses your private key to sign a message hash. Anyone with your public key can verify it. If even one character is changed, verification fails — proving tampering.</p>
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            <div className="glass-card p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                  <select value={algo} onChange={e => setAlgo(e.target.value)} className="cyber-select w-40">
                    {['RSA', 'ECC', 'Ed25519'].map(a => <option key={a}>{a}</option>)}
                  </select>
                </div>
                <div className="flex-1" />
                <button onClick={generate} disabled={loading} className="py-2 px-4 rounded-lg btn-neon text-sm font-medium flex items-center gap-2">
                  {loading ? <LoadingSpinner size={14} /> : <Key size={14} />} Generate Keys
                </button>
              </div>
              {keys && <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10 flex items-center gap-2 text-sm text-emerald-400"><CheckCircle size={14} /> {algo} key pair generated — Fingerprint: <span className="font-mono text-xs text-emerald-300 truncate">{keys.fingerprint}</span></div>}
            </div>

            <div className="glass-card p-6 space-y-4">
              <h3 className="font-semibold text-white">Sign Message</h3>
              <textarea value={message} onChange={e => setMessage(e.target.value)} rows={4} className="code-area" />
              <button onClick={sign} disabled={loading || !keys} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                {loading ? <LoadingSpinner size={16} /> : <PenTool size={16} />} Sign with Private Key
              </button>
              {signature && <ResultBox label="Digital Signature (Base64)" value={signature} badge="Signed" rows={3} />}
            </div>

            {signature && (
              <div className="glass-card p-6 space-y-4">
                <h3 className="font-semibold text-white">Verify Signature</h3>
                <p className="text-xs text-slate-500">Try modifying the message below to see tamper detection in action.</p>
                <textarea value={verifyMsg} onChange={e => setVerifyMsg(e.target.value)} rows={4} className="code-area" />
                {verifyMsg !== message && (
                  <div className="flex items-center gap-2 text-orange-400 text-xs p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                    <AlertTriangle size={14} /> Message has been modified from the original — signature should fail!
                  </div>
                )}
                <button onClick={verify} disabled={loading} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <LoadingSpinner size={16} /> : <CheckCircle size={16} />} Verify Signature
                </button>
                {verifyResult && (
                  <div className={`p-5 rounded-xl border flex items-center gap-4 ${verifyResult.valid ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                    {verifyResult.valid ? <CheckCircle size={28} className="text-emerald-400 flex-shrink-0" /> : <XCircle size={28} className="text-red-400 flex-shrink-0" />}
                    <div>
                      <div className={`font-bold text-lg ${verifyResult.valid ? 'text-emerald-400' : 'text-red-400'}`}>{verifyResult.valid ? 'Signature Valid ✓' : 'Signature Invalid ✗'}</div>
                      <div className="text-sm text-slate-400 mt-1">{verifyResult.message}</div>
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
