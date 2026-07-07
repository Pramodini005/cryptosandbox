'use client';
import { useState, useEffect, useCallback } from 'react';
import { authApi } from '@/lib/api';
import { User } from '@/types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) { setLoading(false); return; }
    try { const res = await authApi.me(); setUser(res.data); }
    catch { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); setUser(null); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchMe(); }, [fetchMe]);

  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password });
    localStorage.setItem('access_token', res.data.access_token);
    localStorage.setItem('refresh_token', res.data.refresh_token);
    await fetchMe();
  };

  const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); setUser(null); };

  const register = async (data: { username: string; email: string; full_name: string; password: string }) => {
    await authApi.register(data); await login(data.username, data.password);
  };

  return { user, loading, login, logout, register };
}
