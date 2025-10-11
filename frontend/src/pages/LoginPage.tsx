import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Search } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await login(formData);
    } catch (error) {
      // Error is handled by the auth hook
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-primary rounded-full p-3">
              <Search className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Naver Monitor
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            네이버 블로그 모니터링 시스템에 로그인하세요
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>로그인</CardTitle>
            <CardDescription>
              계정 정보를 입력하여 로그인하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="사용자명"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="사용자명을 입력하세요"
              />
              
              <Input
                label="비밀번호"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="비밀번호를 입력하세요"
              />
              
              <Button
                type="submit"
                className="w-full"
                loading={isLoading}
                disabled={!formData.username || !formData.password}
              >
                로그인
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                계정이 없으신가요?{' '}
                <a href="#" className="font-medium text-primary hover:text-primary/80">
                  관리자에게 문의하세요
                </a>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

