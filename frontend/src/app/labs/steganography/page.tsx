'use client';
import { useState, useRef } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/hooks/useAuth';
import { steganographyApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Image, Upload, Eye, Download, Info } from 'lucide-react';

export default function SteganographyLabPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<'hide' | 'extract'>('hide');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState('');
  const [secret, setSecret] = useState('This is my hidden secret message!');
  const [stegoUrl, setStegoUrl] = useState('');
  const [extractResult, setExtractResult] = useState('');
  const [capacity, setCapacity] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const extractFileRef = useRef<HTMLInputElement>(null);

  const handleImageChange = async (file: File) => {
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
    setStegoUrl('');
    setError('');
    // Get capacity
    const fd = new FormData();
    fd.append('image', file);
    try { const r = await steganographyApi.capacity(fd); setCapacity(r.data); } catch {}
  };

  const hideText = async () => {
    if (!image || !secret) { setError('Please provide both an image and a secret message.'); return; }
    setLoading(true); setError(''); setStegoUrl('');
    try {
      const fd = new FormData();
      fd.append('image', image);
      fd.append('secret', secret);
      const r = await steganographyApi.hide(fd);
      const url = URL.createObjectURL(r.data);
      setStegoUrl(url);
    } catch (e: any) { setError('Failed to hide message. Try a larger image or shorter message.'); }
    finally { setLoading(false); }
  };

  const extractText = async (file: File) => {
    setLoading(true); setError(''); setExtractResult('');
    try {
      const fd = new FormData();
      fd.append('image', file);
      const r = await steganographyApi.extract(fd);
      setExtractResult(r.data.secret);
    } catch (e: any) { setError(e.response?.data?.detail || 'No hidden message found.'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Steganography Lab" subtitle="Hide and extract secret messages inside images using LSB" badge="LSB" />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="glass-card p-5 border-l-4 border-l-teal-500">
              <div className="flex items-start gap-3">
                <Info size={18} className="text-teal-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-white">LSB Steganography</p>
                  <p className="text-sm text-slate-400 mt-1">Least Significant Bit (LSB) steganography hides data by modifying the last bit of each pixel's color value. The change is imperceptible to the human eye but can store a text message inside the image.</p>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <button onClick={() => setTab('hide')} className={`lab-tab ${tab === 'hide' ? 'active' : ''}`}><Image size={14} className="inline mr-1.5" />Hide Message</button>
              <button onClick={() => setTab('extract')} className={`lab-tab ${tab === 'extract' ? 'active' : ''}`}><Eye size={14} className="inline mr-1.5" />Extract Message</button>
            </div>

            {error && <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

            {tab === 'hide' && (
              <div className="glass-card p-6 space-y-5">
                {/* Image upload */}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Cover Image (PNG or BMP recommended)</label>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-white/10 hover:border-emerald-500/30 rounded-xl p-8 text-center cursor-pointer transition-all group"
                  >
                    {imagePreview ? (
                      <div className="space-y-3">
                        <img src={imagePreview} alt="cover" className="max-h-40 mx-auto rounded-lg" />
                        {capacity && <div className="flex justify-center gap-3 flex-wrap">
                          <span className="badge badge-green">Capacity: {capacity.max_characters.toLocaleString()} chars</span>
                          <span className="badge badge-blue">{capacity.width}x{capacity.height}px</span>
                        </div>}
                      </div>
                    ) : (
                      <div className="text-slate-500 group-hover:text-slate-400 transition-colors">
                        <Upload size={32} className="mx-auto mb-3" />
                        <p className="text-sm">Click to upload image</p>
                        <p className="text-xs mt-1">PNG, BMP, JPG — Larger image = more capacity</p>
                      </div>
                    )}
                    <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={e => e.target.files?.[0] && handleImageChange(e.target.files[0])} />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Secret Message</label>
                  <textarea value={secret} onChange={e => setSecret(e.target.value)} rows={3} className="code-area" placeholder="Enter your secret message..." />
                  {capacity && <p className="text-xs text-slate-600 mt-1">{secret.length}/{capacity.max_characters} characters used</p>}
                </div>

                <button onClick={hideText} disabled={loading || !image || !secret} className="w-full py-3 rounded-xl btn-neon font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
                  {loading ? <><LoadingSpinner size={16} /> Processing...</> : <><Image size={16} /> Hide in Image</>}
                </button>

                {stegoUrl && (
                  <div className="space-y-3 pt-4 border-t border-white/5">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Stego Image (contains hidden message)</div>
                    <img src={stegoUrl} alt="stego" className="max-h-48 rounded-lg border border-emerald-500/20" />
                    <a href={stegoUrl} download="stego_image.png" className="flex items-center justify-center gap-2 py-2 px-4 rounded-lg btn-neon text-sm font-medium w-full">
                      <Download size={14} /> Download Stego Image
                    </a>
                    <p className="text-xs text-slate-500">Download this image, then use the Extract tab to verify the hidden message can be recovered.</p>
                  </div>
                )}
              </div>
            )}

            {tab === 'extract' && (
              <div className="glass-card p-6 space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Stego Image (image containing hidden message)</label>
                  <div
                    onClick={() => extractFileRef.current?.click()}
                    className="border-2 border-dashed border-white/10 hover:border-emerald-500/30 rounded-xl p-8 text-center cursor-pointer transition-all group"
                  >
                    <div className="text-slate-500 group-hover:text-slate-400 transition-colors">
                      <Upload size={32} className="mx-auto mb-3" />
                      <p className="text-sm">Click to upload stego image</p>
                      <p className="text-xs mt-1">Must be an image with a hidden LSB message</p>
                    </div>
                    <input ref={extractFileRef} type="file" accept="image/*" className="hidden" onChange={e => { if (e.target.files?.[0]) extractText(e.target.files[0]); }} />
                  </div>
                </div>
                {loading && <div className="flex items-center gap-3 text-slate-400"><LoadingSpinner size={16} /> Extracting hidden message...</div>}
                {extractResult && (
                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Extracted Secret Message</div>
                    <div className="terminal text-emerald-300">{extractResult}</div>
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
