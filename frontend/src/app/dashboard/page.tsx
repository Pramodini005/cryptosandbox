'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { useAuth } from '@/hooks/useAuth';
import { userApi } from '@/lib/api';
import { UserStats } from '@/types';
import { formatDate } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Lock, Key, Hash, Shield, PenTool, BookOpen, Image, ArrowLeftRight, Wrench, Trophy, Clock, Activity } from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const moduleColors: Record<string, string> = {
  symmetric: '#00ff88', asymmetric: '#00d4ff', hashing: '#bf5af2',
  passwords: '#ff6b35', signatures: '#ff2d78', classical: '#ffd60a',
  steganography: '#00ff88', 'key-exchange': '#00d4ff', tools: '#94a3b8',
};

export default function DashboardPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) router.push('/auth/login');
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      userApi.stats().then(r => setStats(r.data)).catch(() => {}).finally(() => setStatsLoading(false));
    }
  }, [user]);

  if (authLoading) return (<div className="min-h-screen cyber-bg flex items-center justify-center"><LoadingSpinner size={40} /></div>);
  if (!user) return null;

  const chartData = stats ? Object.entries(stats.operations_by_module).map(([module, count]) => ({ module, count, color: moduleColors[module] || '#94a3b8' })) : [];

  return (
    <div className="min-h-screen cyber-bg flex">
      <Sidebar user={user} onLogout={() => { logout(); router.push('/'); }} />
      <div className="flex-1 ml-64 flex flex-col">
        <Header title="Dashboard" subtitle={`Welcome back, ${user.username}!`} badge="Live" />
        <main className="flex-1 p-6 space-y-6">
          {/* Stats cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-5">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-emerald-500/10"><Activity size={22} className="text-emerald-400" /></div>
                <div><div className="text-2xl font-bold text-white">{stats?.total_operations || 0}</div><div className="text-sm text-slate-400">Total Operations</div></div>
              </div>
            </div>
            <div className="glass-card p-5">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-cyan-500/10"><Trophy size={22} className="text-cyan-400" /></div>
                <div><div className="text-2xl font-bold text-white">{stats?.achievements.length || 0}</div><div className="text-sm text-slate-400">Achievements</div></div>
              </div>
            </div>
            <div className="glass-card p-5">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-purple-500/10"><Clock size={22} className="text-purple-400" /></div>
                <div><div className="text-sm font-semibold text-white">{stats?.member_since ? formatDate(stats.member_since) : '—'}</div><div className="text-sm text-slate-400">Member Since</div></div>
              </div>
            </div>
          </div>

          {/* Chart */}
          {chartData.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-6">Operations by Module</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis dataKey="module" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(0,255,136,0.2)', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, i) => (<Cell key={i} fill={entry.color} />))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activity */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Recent Activity</h3>
              {statsLoading ? <LoadingSpinner /> : stats?.recent_logs.length ? (
                <div className="space-y-3">
                  {stats.recent_logs.slice(0, 8).map(log => (
                    <div key={log.id} className="flex items-center gap-3 p-3 rounded-lg bg-white/3 border border-white/5">
                      <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: moduleColors[log.module] || '#64748b' }} />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-white font-medium truncate">{log.operation}</div>
                        <div className="text-xs text-slate-500">{formatDate(log.created_at)}</div>
                      </div>
                      <span className={`badge ${log.status === 'success' ? 'badge-green' : 'badge-orange'} text-[10px]`}>{log.status}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Activity size={32} className="mx-auto mb-3 opacity-30" />
                  <p className="text-sm">No activity yet. Try a lab!</p>
                </div>
              )}
            </div>

            {/* Achievements */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Achievements</h3>
              {stats?.achievements.length ? (
                <div className="space-y-3">
                  {stats.achievements.map(a => (
                    <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/10">
                      <Trophy size={20} className="text-yellow-400 flex-shrink-0" />
                      <div><div className="text-sm font-semibold text-white">{a.badge}</div><div className="text-xs text-slate-400">{a.description}</div></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Trophy size={32} className="mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Perform 10 operations to unlock your first badge!</p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
