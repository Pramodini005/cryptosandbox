'use client';
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function CopyButton({ text, className }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (<button onClick={copy} className={`copy-btn flex items-center gap-1.5 ${className || ''}`}>{copied ? <Check size={12} /> : <Copy size={12} />}{copied ? 'Copied!' : 'Copy'}</button>);
}
