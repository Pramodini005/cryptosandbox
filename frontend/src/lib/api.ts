import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token if present
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auto logout on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      const isAuthRoute = window.location.pathname.startsWith('/auth');
      if (!isAuthRoute) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  register: (data: { username: string; email: string; full_name: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

// Symmetric
export const symmetricApi = {
  encrypt: (data: object) => api.post('/symmetric/encrypt', data),
  decrypt: (data: object) => api.post('/symmetric/decrypt', data),
};

// Asymmetric
export const asymmetricApi = {
  generateKeys: (data: object) => api.post('/asymmetric/generate-keys', data),
  encrypt: (data: object) => api.post('/asymmetric/encrypt', data),
  decrypt: (data: object) => api.post('/asymmetric/decrypt', data),
  sign: (data: object) => api.post('/asymmetric/sign', data),
  verify: (data: object) => api.post('/asymmetric/verify', data),
};

// Hashing
export const hashApi = {
  compute: (data: object) => api.post('/hash/compute', data),
  compare: (data: object) => api.post('/hash/compare', data),
};

// Password
export const passwordApi = {
  analyze: (data: object) => api.post('/password/analyze', data),
  hash: (data: object) => api.post('/password/hash', data),
  verify: (data: object) => api.post('/password/verify', data),
  generate: (data?: object) => api.post('/password/generate', data || {}),
};

// Classical
export const classicalApi = {
  encrypt: (data: object) => api.post('/classical/encrypt', data),
  decrypt: (data: object) => api.post('/classical/decrypt', data),
};

// Steganography
export const steganographyApi = {
  hide: (formData: FormData) =>
    api.post('/steganography/hide', formData, { headers: { 'Content-Type': 'multipart/form-data' }, responseType: 'blob' }),
  extract: (formData: FormData) =>
    api.post('/steganography/extract', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  capacity: (formData: FormData) =>
    api.post('/steganography/capacity', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
};

// Key Exchange
export const keyExchangeApi = {
  diffieHellman: (data?: object) => api.post('/key-exchange/diffie-hellman', data || {}),
};

// Tools
export const toolsApi = {
  base64: (data: object) => api.post('/tools/base64', data),
  hmac: (data: object) => api.post('/tools/hmac', data),
  jwtDecode: (data: object) => api.post('/tools/jwt-decode', data),
  uuid: () => api.get('/tools/uuid'),
  random: (length?: number) => api.get(`/tools/random/${length || 32}`),
  convert: (data: object) => api.post('/tools/convert', data),
};

// User
export const userApi = {
  stats: () => api.get('/user/stats'),
};
