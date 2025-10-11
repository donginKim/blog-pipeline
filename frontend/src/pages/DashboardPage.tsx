import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useDashboardStats, useRecentActivity, useTriggerCrawl } from '@/hooks/useApi';
import { formatDate, formatRelativeTime, getStatusColor, getStatusText } from '@/utils';
import { 
  Search, 
  Globe, 
  Target, 
  BarChart3, 
  Play, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: statsLoading, error: statsError } = useDashboardStats();
  const { data: recentActivity, isLoading: activityLoading } = useRecentActivity(10);
  const triggerCrawl = useTriggerCrawl();

  const handleTriggerCrawl = () => {
    triggerCrawl.mutate({}); // 전체 크롤링
  };

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">대시보드 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (statsError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <p className="text-red-600 mb-2">데이터를 불러올 수 없습니다</p>
          <p className="text-gray-600">{statsError.message}</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: '총 키워드',
      value: stats?.total_keywords || 0,
      icon: Search,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: '총 블로그',
      value: stats?.total_blogs || 0,
      icon: Globe,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: '총 타겟',
      value: stats?.total_targets || 0,
      icon: Target,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      title: '활성 타겟',
      value: stats?.active_targets || 0,
      icon: BarChart3,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
                <div className={`p-3 rounded-full ${card.bgColor}`}>
                  <card.icon className={`h-6 w-6 ${card.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>크롤링 관리</CardTitle>
          <CardDescription>
            전체 크롤링을 실행하거나 상태를 확인할 수 있습니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Button
              onClick={handleTriggerCrawl}
              disabled={triggerCrawl.isLoading}
              className="flex items-center space-x-2"
            >
              <Play className="h-4 w-4" />
              <span>
                {triggerCrawl.isLoading ? '실행 중...' : '전체 크롤링 실행'}
              </span>
            </Button>
            
            {triggerCrawl.isSuccess && (
              <Badge variant="default" className="flex items-center space-x-1">
                <CheckCircle className="h-3 w-3" />
                <span>크롤링 완료</span>
              </Badge>
            )}
            
            {triggerCrawl.isError && (
              <Badge variant="destructive" className="flex items-center space-x-1">
                <XCircle className="h-3 w-3" />
                <span>크롤링 실패</span>
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>최근 활동</CardTitle>
          <CardDescription>
            최근 크롤링 결과와 활동 내역을 확인할 수 있습니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {activityLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : recentActivity && recentActivity.length > 0 ? (
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      activity.status === 'success' ? 'bg-green-100' : 
                      activity.status === 'error' ? 'bg-red-100' : 'bg-yellow-100'
                    }`}>
                      {activity.status === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : activity.status === 'error' ? (
                        <XCircle className="h-4 w-4 text-red-600" />
                      ) : (
                        <Clock className="h-4 w-4 text-yellow-600" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{activity.keyword}</p>
                      <p className="text-sm text-gray-600">{activity.blog_name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge 
                      variant={getStatusColor(activity.status)}
                      className="mb-1"
                    >
                      {getStatusText(activity.status)}
                    </Badge>
                    <p className="text-sm text-gray-500">
                      {formatRelativeTime(activity.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>최근 활동이 없습니다.</p>
            </div>
          )}
        </CardContent>
      </Card>

    </div>
  );
};