'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ResultBox from '@/components/ui/ResultBox';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { toolsApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Wrench, RefreshCw } from 'lucide-react';

const TOOLS = [
  { id: 'base64', label: 'Base64 Encode/Decode' },
  { id: 'hmac', label: 'HMAC Generator' },
  { id: 'jwt', label: 'JWT Decoder' },
  { id: 'convert', label: 'Hex / Binary Converter' },
  { id: 'uuid', label: 'UUID & Random Generator' },
];

export default function ToolsPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tool, setTool] = useState('base64');
  const [b64Input, setB64Input] = useState('Hello, CryptoSandbox!');
  const [b64Action, setB64Action] = useState<'encode' | 'decode'>('encode');
  const [b64Result, setB64Result] = useState('');
  const [hmacMsg, setHmacMsg] = useState('Hello World');
  const [hmacKey, setHmacKey] = useState('supersecretkey');
  const [hmacAlgo, setHmacAlgo] = useState('SHA-256');
  const [hmacResult, setHmacResult] = useState('');
  const [jwtToken, setJwtToken] = useState('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c');
  const [jwtResult, setJwtResult] = useState<any>(null);
  const [convertInput, setConvertInput] = useState('Hello World');
  const [convertMode, setConvertMode] = useState<'hex' | 'binary' | 'from_hex'>('hex');
  const [convertResult, setConvertResult] = useState('');
  const [uuidResult, setUuidResult] = useState('');
  const [randomResult, setRandomResult] = useState('');
  const [randomLen, setRandomLen] = useState(32);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true); setError('');
    try {
      if (tool === 'base64') {
        const r = await toolsApi.base64({ data: b64Input, action: b64Action });
        setB64Result(r.data.result);
      } else if (tool === 'hmac') {
        const r = await toolsApi.hmac({ message: hmacMsg, key: hmacKey, algorithm: hmacAlgo });
        setHmacResult(r.data.hmac);
      } else if (tool === 'jwt') {
        const r = await toolsApi.jwtDecode({ token: jwtToken });
        setJwtResult(r.data);
      } else if (tool === 'convert') {
        const r = await toolsApi.convert({ text: convertInput, to: convertMode });
        setConvertResult(r.data.result);
      } else if (tool === 'uuid') {
        const [uuidR, randR] = await Promise.all([toolsApi.uuid(), toolsApi.random(randomLen)]);
        setUuidResult(uuidR.data.uuid);
        setRandomResult(randR.data.random_hex);
      }
    } catch (e: any) { setError(e.response?.data?.detail || 'Operation failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Security Tools" subtitle="Utility belt for cryptography and security operations" badge="Utility" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Tool selector */}
            <div className="flex flex-wrap gap-2">
              {TOOLS.map(t => (
                <button key={t.id} onClick={() => { setTool(t.id); setError(''); }} className={`lab-tab ${tool === t.id ? 'active' : ''}`}><Wrench size={13} className="inline mr-1.5" />{t.label}</button>
              ))}
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            <div className="glass-card p-6 space-y-5">
              {tool === 'base64' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Input</label>
                    <textarea value={b64Input} onChange={e => setB64Input(e.target.value)} rows={4} className="code-area" />
                  </div>
                  <div className="flex gap-3">
                    {(['encode', 'decode'] as const).map(a => (
                      <button key={a} onClick={() => setB64Action(a)} className={`py-2 px-4 rounded-lg text-sm border transition-all capitalize ${b64Action === a ? 'bg-purple-500/20 border-purple-500/30 text-purple-300' : 'border-white/10 text-slate-500 hover:text-white'}`}>{a}</button>
                    ))}
                  </div>
                </>
              )}

              {tool === 'hmac' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Message</label>
                      <input value={hmacMsg} onChange={e => setHmacMsg(e.target.value)} className="cyber-input font-mono" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Secret Key</label>
                      <input value={hmacKey} onChange={e => setHmacKey(e.target.value)} className="cyber-input font-mono" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Algorithm</label>
                    <div className="flex gap-2">
                      {['SHA-256', 'SHA-512', 'SHA3-256'].map(a => (
                        <button key={a} onClick={() => setHmacAlgo(a)} className={`py-2 px-4 rounded-lg text-sm border transition-all ${hmacAlgo === a ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300' : 'border-white/10 text-slate-500 hover:text-white'}`}>{a}</button>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {tool === 'jwt' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">JWT Token</label>
                  <textarea value={jwtToken} onChange={e => setJwtToken(e.target.value)} rows={4} className="code-area text-xs" />
                </div>
              )}

              {tool === 'convert' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Input</label>
                    <input value={convertInput} onChange={e => setConvertInput(e.target.value)} className="cyber-input font-mono" />
                  </div>
                  <div className="flex gap-2">
                    {[['hex', 'Text → Hex'], ['binary', 'Text → Binary'], ['from_hex', 'Hex → Text']].map(([m, l]) => (
                      <button key={m} onClick={() => setConvertMode(m as any)} className={`py-2 px-4 rounded-lg text-sm border transition-all ${convertMode === m ? 'bg-cyan-500/20 border-cyan-500/30 text-cyan-300' : 'border-white/10 text-slate-500 hover:text-white'}`}>{l}</button>
                    ))}
                  </div>
                </>
              )}

              {tool === 'uuid' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Random bytes length: {randomLen}</label>
                  <input type="range" min={8} max={64} value={randomLen} onChange={e => setRandomLen(Number(e.target.value))} className="w-full accent-emerald-500" />
                </div>
              )}

              <button onClick={run} disabled={loading} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                {loading ? <><LoadingSpinner size={16} /> Running...</> : <><Wrench size={16} /> Run</>}
              </button>

              {/* Results */}
              {tool === 'base64' && b64Result && <ResultBox label={`Base64 ${b64Action === 'encode' ? 'Encoded' : 'Decoded'}`} value={b64Result} />}
              {tool === 'hmac' && hmacResult && <ResultBox label={`HMAC-${hmacAlgo}`} value={hmacResult} badge="HMAC" />}
              {tool === 'jwt' && jwtResult && (
                <div className="space-y-3">
                  <div className={`flex items-center gap-2 p-3 rounded-lg ${jwtResult.is_valid ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border border-red-500/20 text-red-400'} text-sm font-medium`}>
                    {jwtResult.is_valid ? '✓ Valid JWT format' : '✗ Invalid: ' + jwtResult.error}
                  </div>
                  {jwtResult.is_valid && (
                    <div className="grid grid-cols-2 gap-3">
                      <div><div className="text-xs text-slate-500 mb-1">Header</div><div className="terminal text-xs py-2 px-3">{JSON.stringify(jwtResult.header, null, 2)}</div></div>
                      <div><div className="text-xs text-slate-500 mb-1">Payload</div><div className="terminal text-xs py-2 px-3">{JSON.stringify(jwtResult.payload, null, 2)}</div></div>
                    </div>
                  )}
                </div>
              )}
              {tool === 'convert' && convertResult && <ResultBox label={`${convertMode} output`} value={convertResult} />}
              {tool === 'uuid' && (
                <div className="space-y-3">
                  {uuidResult && <ResultBox label="UUID v4" value={uuidResult} badge="UUID" />}
                  {randomResult && <ResultBox label={`${randomLen} random bytes (hex)`} value={randomResult} badge="CSPRNG" />}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
