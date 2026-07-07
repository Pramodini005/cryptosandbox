'use client';
import Link from 'next/link';
import { Lock, Key, Hash, Shield, PenTool, BookOpen, Image, ArrowLeftRight, Wrench, ChevronRight, Github, Star, Zap, CheckCircle } from 'lucide-react';

const labs = [
  { href: '/labs/symmetric', icon: Lock, label: 'Symmetric', desc: 'AES-GCM, AES-CBC, ChaCha20, Fernet', color: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/20', badge: 'Most Popular' },
  { href: '/labs/asymmetric', icon: Key, label: 'Asymmetric', desc: 'RSA, ECC, Ed25519 keys & encryption', color: 'from-cyan-500/20 to-cyan-600/10', border: 'border-cyan-500/20', badge: '' },
  { href: '/labs/hashing', icon: Hash, label: 'Hashing Lab', desc: 'SHA-256, SHA-3, BLAKE2, MD5 & more', color: 'from-purple-500/20 to-purple-600/10', border: 'border-purple-500/20', badge: '' },
  { href: '/labs/passwords', icon: Shield, label: 'Password Security', desc: 'Strength analysis, bcrypt, Argon2', color: 'from-orange-500/20 to-orange-600/10', border: 'border-orange-500/20', badge: 'Essential' },
  { href: '/labs/signatures', icon: PenTool, label: 'Digital Signatures', desc: 'Sign, verify, tamper detection', color: 'from-pink-500/20 to-pink-600/10', border: 'border-pink-500/20', badge: '' },
  { href: '/labs/classical', icon: BookOpen, label: 'Classical Ciphers', desc: 'Caesar, Vigenere, Playfair, OTP', color: 'from-yellow-500/20 to-yellow-600/10', border: 'border-yellow-500/20', badge: 'Historical' },
  { href: '/labs/steganography', icon: Image, label: 'Steganography', desc: 'Hide & extract secrets in images', color: 'from-emerald-500/20 to-teal-600/10', border: 'border-teal-500/20', badge: 'Unique' },
  { href: '/labs/key-exchange', icon: ArrowLeftRight, label: 'Key Exchange', desc: 'Diffie-Hellman simulation', color: 'from-blue-500/20 to-blue-600/10', border: 'border-blue-500/20', badge: '' },
  { href: '/tools', icon: Wrench, label: 'Security Tools', desc: 'JWT, Base64, HMAC, UUID, Hex', color: 'from-slate-500/20 to-slate-600/10', border: 'border-slate-500/20', badge: 'Utility' },
];

const features = [
  'AES-GCM, AES-CBC, AES-CTR encryption',
  'RSA & ECC key generation + signing',
  'SHA-256, SHA-3, BLAKE2 hashing',
  'Password entropy & crack time analysis',
  'Image steganography (LSB)',
  'Diffie-Hellman key exchange',
  'Classical cipher suite',
  'JWT decoder & security tools',
];

export default function HomePage() {
  return (
    <div className="min-h-screen cyber-bg">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-xl">🔐</div>
          <div>
            <span className="font-bold text-white text-lg">CryptoSandbox</span>
            <span className="ml-2 badge badge-green text-[10px]">v1.0</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/auth/login" className="text-sm text-slate-400 hover:text-white transition-colors px-4 py-2">Sign In</Link>
          <Link href="/auth/register" className="text-sm bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-4 py-2 rounded-lg transition-colors">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 text-center relative overflow-hidden">
        {/* Glow blobs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium mb-8">
          <Zap size={14} />
          Enterprise-Grade Cryptography Learning Platform
        </div>

        <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-tight">
          Learn
          <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent"> Cryptography</span>
          <br />Interactively
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          A production-grade cybersecurity learning sandbox for students, researchers, and professionals.
          Explore modern and classical cryptographic algorithms through hands-on interactive labs.
        </p>

        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link href="/labs/symmetric" className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-8 py-3.5 rounded-xl transition-all hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/25">
            Start Learning <ChevronRight size={18} />
          </Link>
          <Link href="/dashboard" className="flex items-center gap-2 border border-white/10 hover:border-white/20 text-white font-medium px-8 py-3.5 rounded-xl transition-all hover:bg-white/5">
            Dashboard
          </Link>
        </div>

        {/* Stats */}
        <div className="flex items-center justify-center gap-12 mt-16 flex-wrap">
          {[['9', 'Lab Modules'], ['25+', 'Algorithms'], ['100%', 'Open Labs'], ['0', 'Setup Required']].map(([num, label]) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-black text-white">{num}</div>
              <div className="text-sm text-slate-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Labs Grid */}
      <section className="px-6 py-16 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">Interactive Labs</h2>
          <p className="text-slate-400">Hands-on cryptography experiments — no setup required</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {labs.map((lab) => {
            const Icon = lab.icon;
            return (
              <Link key={lab.href} href={lab.href} className={`lab-card bg-gradient-to-br ${lab.color} border ${lab.border} group`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 rounded-xl bg-white/5 border border-white/10 group-hover:bg-white/10 transition-colors">
                    <Icon size={22} className="text-white" />
                  </div>
                  {lab.badge && <span className="badge badge-green text-[10px]">{lab.badge}</span>}
                </div>
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">{lab.label}</h3>
                <p className="text-sm text-slate-400">{lab.desc}</p>
                <div className="mt-4 flex items-center text-xs text-slate-500 group-hover:text-emerald-400 transition-colors">
                  Open Lab <ChevronRight size={12} className="ml-1" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 max-w-4xl mx-auto">
        <div className="glass-card p-10">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">What You Will Learn</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {features.map((f) => (
              <div key={f} className="flex items-center gap-3">
                <CheckCircle size={18} className="text-emerald-400 flex-shrink-0" />
                <span className="text-slate-300 text-sm">{f}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-slate-500 text-sm">
        CryptoSandbox © {new Date().getFullYear()} — Cryptography & Cybersecurity Learning Platform
      </footer>
    </div>
  );
}
