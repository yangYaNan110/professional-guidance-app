import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, authApi, userApi } from '../services/api';
import { User, UserProfile } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const navigate = useNavigate();

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setState({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const user = await userApi.getProfile();
      setState({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setState({ user: null, isAuthenticated: false, isLoading: false });
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password });
      localStorage.setItem('access_token', response.access_token);
      await loadUser();
      navigate('/');
      return { success: true };
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      return {
        success: false,
        error: axiosError.response?.data?.detail || '登录失败，请检查邮箱和密码'
      };
    }
  };

  const register = async (email: string, password: string, nickname?: string) => {
    try {
      await authApi.register({ email, password, nickname });
      const loginResult = await login(email, password);
      return loginResult;
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      return {
        success: false,
        error: axiosError.response?.data?.detail || '注册失败，请稍后重试'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setState({ user: null, isAuthenticated: false, isLoading: false });
    navigate('/login');
  };

  return {
    ...state,
    login,
    register,
    logout,
    loadUser,
  };
}
