'use client';
import CopyButton from './CopyButton';

interface ResultBoxProps { label: string; value: string; rows?: number; badge?: string; }

export default function ResultBox({ label, value, rows, badge }: ResultBoxProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</label>
        <div className="flex items-center gap-2">{badge && <span className="badge badge-green">{badge}</span>}{value && <CopyButton text={value} />}</div>
      </div>
      <div className="terminal" style={{ minHeight: rows ? `${rows * 24}px` : '48px' }}>
        {value || <span className="text-slate-600">Output will appear here...</span>}
      </div>
    </div>
  );
}
