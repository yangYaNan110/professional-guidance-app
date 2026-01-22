import { useState, useEffect, useCallback } from 'react';
import { userApi } from '../services/api';
import { UserProfile } from '../types';

interface ProfileState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  loadProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<boolean>;
}

export function useProfile(): ProfileState {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await userApi.getUserProfile();
      setProfile(response as UserProfile);
    } catch (err) {
      setError('加载用户画像失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (data: Partial<UserProfile>): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await userApi.updateProfile(data);
      setProfile(response as UserProfile);
      return true;
    } catch (err) {
      setError('更新用户画像失败');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  return {
    profile,
    isLoading,
    error,
    loadProfile,
    updateProfile,
  };
}
