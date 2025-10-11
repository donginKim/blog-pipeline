import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/utils';
import {
  LayoutDashboard,
  Search,
  Globe,
  Target,
  BarChart3,
  Settings,
  Activity,
  FileText,
} from 'lucide-react';

const navigation = [
  { name: '대시보드', href: '/dashboard', icon: LayoutDashboard },
  { name: '키워드', href: '/keywords', icon: Search },
  { name: '블로그', href: '/blogs', icon: Globe },
  { name: '타겟', href: '/targets', icon: Target },
  { name: '결과', href: '/results', icon: BarChart3 },
  { name: '크롤링 기록', href: '/crawl-runs', icon: Activity },
  { name: '🤖 생성된 글', href: '/generated-posts', icon: FileText },
];

export const Sidebar: React.FC = () => {
  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200 h-screen">
      <div className="flex items-center h-16 px-6 border-b border-gray-200 min-h-[4rem] max-h-[4rem]">
        <h1 className="text-xl font-bold text-gray-900">Naver Monitor</h1>
      </div>
      
      <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                )
              }
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-gray-200 flex-shrink-0">
        <NavLink
          to="/settings"
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900 transition-colors"
        >
          <Settings className="mr-3 h-5 w-5" />
          설정
        </NavLink>
      </div>
    </div>
  );
};
