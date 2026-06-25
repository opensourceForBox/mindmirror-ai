/**
 * 认证服务：登录 / 注册 / 获取当前用户
 * token 存储于 localStorage
 */
const API_BASE = '/api';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: string;
  parent_id?: number | null;
  is_active?: boolean;
  created_at?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  role: 'child' | 'parent';
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

// ─── Token 管理 ────────────────────────────────────────────────────────────────
const TOKEN_KEY = 'mindmirror_token';
const USER_KEY = 'mindmirror_user';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

function storeUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// ─── 请求工具 ──────────────────────────────────────────────────────────────────
async function authRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as Record<string, string>).detail ?? `请求失败 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

// ─── API 方法 ──────────────────────────────────────────────────────────────────
export async function login(payload: LoginPayload): Promise<AuthUser> {
  const data = await authRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setToken(data.access_token);
  storeUser(data.user);
  return data.user;
}

export async function register(payload: RegisterPayload): Promise<AuthUser> {
  const data = await authRequest<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setToken(data.access_token);
  storeUser(data.user);
  return data.user;
}

export async function getMe(): Promise<AuthUser> {
  const user = await authRequest<AuthUser>('/auth/me');
  storeUser(user);
  return user;
}

export function logout(): void {
  removeToken();
}
