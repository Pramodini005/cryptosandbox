import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(date));
}

export const MODULES = [
  { id: 'symmetric', label: 'Symmetric', href: '/labs/symmetric', icon: 'Lock', color: 'neon-green', description: 'AES-GCM, ChaCha20, Fernet' },
  { id: 'asymmetric', label: 'Asymmetric', href: '/labs/asymmetric', icon: 'Key', color: 'neon-blue', description: 'RSA, ECC, Ed25519' },
  { id: 'hashing', label: 'Hashing', href: '/labs/hashing', icon: 'Hash', color: 'neon-purple', description: 'SHA-256, BLAKE2, SHA-3' },
  { id: 'passwords', label: 'Passwords', href: '/labs/passwords', icon: 'Shield', color: 'neon-orange', description: 'bcrypt, Argon2, Entropy' },
  { id: 'signatures', label: 'Signatures', href: '/labs/signatures', icon: 'PenTool', color: 'neon-pink', description: 'Digital Sign & Verify' },
  { id: 'classical', label: 'Classical', href: '/labs/classical', icon: 'BookOpen', color: 'neon-yellow', description: 'Caesar, Vigenère, OTP' },
  { id: 'steganography', label: 'Steganography', href: '/labs/steganography', icon: 'ImageIcon', color: 'neon-green', description: 'LSB Image Hiding' },
  { id: 'key-exchange', label: 'Key Exchange', href: '/labs/key-exchange', icon: 'ArrowLeftRight', color: 'neon-blue', description: 'Diffie-Hellman' },
  { id: 'tools', label: 'Security Tools', href: '/tools', icon: 'Wrench', color: 'neon-purple', description: 'JWT, Base64, HMAC, UUID' },
];
