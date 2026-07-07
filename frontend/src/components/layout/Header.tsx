'use client';
import { Bell, Search } from 'lucide-react';

interface HeaderProps { title: string; subtitle?: string; badge?: string; }

export default function Header({ title, subtitle, badge }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-emerald-900/20 bg-slate-950/50 backdrop-blur-xl">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-white">{title}</h1>
          {badge && <span className="badge badge-green text-xs">{badge}</span>}
        </div>
        {subtitle && <p className="text-sm text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        <div className="relative hidden md:block">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input type="text" placeholder="Search labs..." className="pl-9 pr-4 py-2 rounded-lg text-sm bg-white/5 border border-white/10 text-slate-300 placeholder-slate-600 focus:outline-none focus:border-emerald-500/50 w-48" />
        </div>
        <button className="relative p-2 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-400 rounded-full"></span>
        </button>
      </div>
    </header>
  );
}
