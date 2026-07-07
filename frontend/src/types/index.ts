export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface OperationLog {
  id: number;
  operation: string;
  module: string;
  input_preview: string;
  status: string;
  created_at: string;
}

export interface Achievement {
  id: number;
  badge: string;
  description: string;
  earned_at: string;
}

export interface UserStats {
  total_operations: number;
  operations_by_module: Record<string, number>;
  recent_logs: OperationLog[];
  achievements: Achievement[];
  member_since: string;
}

export interface SymmetricEncryptResponse {
  ciphertext: string;
  ciphertext_hex: string;
  ciphertext_base64: string;
  key: string;
  iv?: string;
  algorithm: string;
  key_size: number;
}

export interface HashResponse {
  hash: string;
  algorithm: string;
  length: number;
  hex: string;
  binary: string;
}

export interface PasswordAnalysis {
  score: number;
  strength: string;
  entropy_bits: number;
  estimated_crack_time: string;
  suggestions: string[];
  has_uppercase: boolean;
  has_lowercase: boolean;
  has_digits: boolean;
  has_symbols: boolean;
  length: number;
  is_common: boolean;
}

export interface DHKeyExchange {
  p: string;
  g: string;
  alice_private: string;
  alice_public: string;
  bob_private: string;
  bob_public: string;
  alice_shared_secret: string;
  bob_shared_secret: string;
  secrets_match: boolean;
}
