import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, LoginRequest, AuthContextType } from '@/types';
import { apiService } from '@/services/api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        try {
          const userData = await apiService.getCurrentUser();
          setUser(userData);
          setToken(storedToken);
        } catch (error) {
          console.error('인증 오류:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      const response = await apiService.login(credentials);
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      
      const userData = await apiService.getCurrentUser();
      setUser(userData);
      
      toast.success('로그인 성공!');
      
      // 로그인 성공 후 대시보드로 리다이렉트
      navigate('/dashboard');
    } catch (error: any) {
      const message = error.response?.data?.detail || '로그인에 실패했습니다.';
      toast.error(message);
      throw error;
    }
  };

  const logout = (): void => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    toast.success('로그아웃되었습니다.');
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
