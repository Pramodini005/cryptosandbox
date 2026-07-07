'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Lock, Key, Hash, Shield, PenTool, BookOpen, Image, ArrowLeftRight, Wrench, LayoutDashboard, LogOut, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', color: 'text-slate-400' },
  { href: '/labs/symmetric', icon: Lock, label: 'Symmetric', color: 'text-emerald-400' },
  { href: '/labs/asymmetric', icon: Key, label: 'Asymmetric', color: 'text-cyan-400' },
  { href: '/labs/hashing', icon: Hash, label: 'Hashing', color: 'text-purple-400' },
  { href: '/labs/passwords', icon: Shield, label: 'Passwords', color: 'text-orange-400' },
  { href: '/labs/signatures', icon: PenTool, label: 'Signatures', color: 'text-pink-400' },
  { href: '/labs/classical', icon: BookOpen, label: 'Classical', color: 'text-yellow-400' },
  { href: '/labs/steganography', icon: Image, label: 'Steganography', color: 'text-emerald-400' },
  { href: '/labs/key-exchange', icon: ArrowLeftRight, label: 'Key Exchange', color: 'text-cyan-400' },
  { href: '/tools', icon: Wrench, label: 'Security Tools', color: 'text-purple-400' },
];

interface SidebarProps {
  user?: { username: string; email: string } | null;
  onLogout?: () => void;
}

export default function Sidebar({ user, onLogout }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  return (
    <aside className={cn('fixed left-0 top-0 h-full z-40 flex flex-col transition-all duration-300', collapsed ? 'w-16' : 'w-64', 'bg-slate-950/95 backdrop-blur-xl border-r border-emerald-900/20')}>
      <div className="flex items-center justify-between p-4 border-b border-emerald-900/20">
        {!collapsed && (<div className="flex items-center gap-2"><div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-sm">🔐</div><div><div className="font-bold text-sm text-white">CryptoSandbox</div><div className="text-[10px] text-emerald-400/70">Cybersecurity Lab</div></div></div>)}
        <button onClick={() => setCollapsed(!collapsed)} className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors">{collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}</button>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (<Link key={item.href} href={item.href} className={cn('flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200', collapsed && 'justify-center', isActive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:text-white hover:bg-white/5')} title={collapsed ? item.label : undefined}><Icon size={18} className={cn(isActive ? 'text-emerald-400' : item.color, 'flex-shrink-0')} />{!collapsed && <span>{item.label}</span>}{!collapsed && isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400" />}</Link>);
        })}
      </nav>
      {user && (<div className="p-3 border-t border-emerald-900/20"><div className={cn('flex items-center gap-3', collapsed && 'justify-center')}><div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">{user.username[0].toUpperCase()}</div>{!collapsed && (<div className="flex-1 min-w-0"><div className="text-sm font-medium text-white truncate">{user.username}</div><div className="text-xs text-slate-500 truncate">{user.email}</div></div>)}{!collapsed && onLogout && (<button onClick={onLogout} className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition-colors" title="Logout"><LogOut size={15} /></button>)}</div></div>)}
    </aside>
  );
}
