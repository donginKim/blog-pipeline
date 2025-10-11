import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { LogOut, User } from 'lucide-react';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 h-16 min-h-[4rem] max-h-[4rem] flex-shrink-0">
      <div className="flex items-center justify-between h-full px-8">
        <div className="flex items-center">
          <h2 className="text-lg font-semibold text-gray-900">
            안녕하세요, {user?.username}님!
          </h2>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <User className="h-4 w-4" />
            <span>{user?.email}</span>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={logout}
            className="flex items-center space-x-2"
          >
            <LogOut className="h-4 w-4" />
            <span>로그아웃</span>
          </Button>
        </div>
      </div>
    </header>
  );
};
