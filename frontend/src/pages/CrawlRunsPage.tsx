import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useCrawlRuns, useTriggerCrawl } from '@/hooks/useApi';
import { formatRelativeTime, getStatusText } from '@/utils';
import { 
  Play, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Eye
} from 'lucide-react';

export const CrawlRunsPage: React.FC = () => {
  const [selectedRun, setSelectedRun] = useState<any>(null);
  const { data: crawlRuns, isLoading, refetch } = useCrawlRuns(100);
  const triggerCrawl = useTriggerCrawl();

  const handleTriggerCrawl = () => {
    triggerCrawl.mutate({}); // 전체 크롤링
  };

  const handleRefresh = () => {
    refetch();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'success':
        return 'default';
      case 'error':
        return 'destructive';
      case 'running':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">크롤링 실행 기록</h1>
          <p className="text-gray-600">크롤링 실행 내역과 오류를 확인하세요</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>새로고침</span>
          </Button>
          <Button
            onClick={handleTriggerCrawl}
            disabled={triggerCrawl.isLoading}
            className="flex items-center space-x-2"
          >
            <Play className="h-4 w-4" />
            <span>{triggerCrawl.isLoading ? '실행 중...' : '전체 크롤링 실행'}</span>
          </Button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">전체 실행</p>
                <p className="text-2xl font-bold text-gray-900">{crawlRuns?.length || 0}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">성공</p>
                <p className="text-2xl font-bold text-green-600">
                  {crawlRuns?.filter(run => run.status === 'completed' || run.status === 'success').length || 0}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">실패</p>
                <p className="text-2xl font-bold text-red-600">
                  {crawlRuns?.filter(run => run.status === 'failed' || run.status === 'error').length || 0}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">실행 중</p>
                <p className="text-2xl font-bold text-blue-600">
                  {crawlRuns?.filter(run => run.status === 'running').length || 0}
                </p>
              </div>
              <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Crawl Runs List */}
      <Card>
        <CardHeader>
          <CardTitle>실행 기록</CardTitle>
          <CardDescription>
            최근 크롤링 실행 내역을 확인할 수 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : !crawlRuns || crawlRuns.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>크롤링 실행 기록이 없습니다.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {crawlRuns.map((run) => (
                <div
                  key={run.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(run.status)}
                      <Badge variant={getStatusBadgeVariant(run.status)}>
                        {getStatusText(run.status)}
                      </Badge>
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-gray-900">{run.keyword || 'N/A'}</h3>
                        <span className="text-gray-400">-</span>
                        <span className="text-gray-600">{run.blog_name || 'N/A'}</span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>시작: {run.started_at ? formatRelativeTime(run.started_at) : 'N/A'}</span>
                        {run.completed_at && (
                          <span>완료: {formatRelativeTime(run.completed_at)}</span>
                        )}
                        {run.created_at && (
                          <span>생성: {formatRelativeTime(run.created_at)}</span>
                        )}
                      </div>
                      {run.error_message && (
                        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                          <strong>오류:</strong> {run.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedRun(run)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detail Modal */}
      {selectedRun && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">크롤링 실행 상세</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedRun(null)}
              >
                닫기
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">키워드</label>
                  <p className="text-gray-900">{selectedRun.keyword}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">블로그</label>
                  <p className="text-gray-900">{selectedRun.blog_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">상태</label>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(selectedRun.status)}
                    <Badge variant={getStatusBadgeVariant(selectedRun.status)}>
                      {getStatusText(selectedRun.status)}
                    </Badge>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">실행 ID</label>
                  <p className="text-gray-900">{selectedRun.id}</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-600">시작 시간</label>
                <p className="text-gray-900">{selectedRun.started_at || 'N/A'}</p>
              </div>
              
              {selectedRun.completed_at && (
                <div>
                  <label className="text-sm font-medium text-gray-600">완료 시간</label>
                  <p className="text-gray-900">{selectedRun.completed_at}</p>
                </div>
              )}
              
              {selectedRun.error_message && (
                <div>
                  <label className="text-sm font-medium text-gray-600">오류 메시지</label>
                  <div className="mt-1 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 whitespace-pre-wrap">
                    {selectedRun.error_message}
                  </div>
                </div>
              )}
              
              <div>
                <label className="text-sm font-medium text-gray-600">생성 시간</label>
                <p className="text-gray-900">{selectedRun.created_at}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

