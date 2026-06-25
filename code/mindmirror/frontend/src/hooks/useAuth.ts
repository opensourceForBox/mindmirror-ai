import { useState, useEffect, useCallback } from 'react';
import {
  getStoredUser,
  getToken,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getMe,
  type AuthUser,
  type LoginPayload,
  type RegisterPayload,
} from '../services/authService';

export interface UseAuthReturn {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(getStoredUser);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 初始化：校验 token 有效性
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => {
        apiLogout();
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    setError(null);
    try {
      const u = await apiLogin(payload);
      setUser(u);
    } catch (e) {
      const msg = e instanceof Error ? e.message : '登录失败';
      setError(msg);
      throw e;
    }
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    setError(null);
    try {
      const u = await apiRegister(payload);
      setUser(u);
    } catch (e) {
      const msg = e instanceof Error ? e.message : '注册失败';
      setError(msg);
      throw e;
    }
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
}
