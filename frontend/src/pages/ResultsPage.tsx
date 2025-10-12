import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useCrawlResults, useCrawlRuns, useKeywords, useBlogs, useTargets } from '@/hooks/useApi';
import { formatRelativeTime } from '@/utils';
import { BarChart3, ExternalLink, Filter, RefreshCw, ChevronDown, ChevronUp, Clock, CheckCircle, XCircle, Star, Calendar, Tag } from 'lucide-react';

type ViewMode = 'runs' | 'keywords' | 'dates';

export const ResultsPage: React.FC = () => {
  const [filters, setFilters] = useState({
    keyword_id: '',
    blog_id: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [expandedRuns, setExpandedRuns] = useState<number[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('runs');

  const { data: results, isLoading: resultsLoading, refetch: refetchResults } = useCrawlResults({
    keyword_id: filters.keyword_id ? parseInt(filters.keyword_id) : undefined,
    blog_id: filters.blog_id ? parseInt(filters.blog_id) : undefined,
    limit: 500,
  });

  const { data: runs, isLoading: runsLoading, refetch: refetchRuns } = useCrawlRuns(100);
  const { data: keywords } = useKeywords();
  const { data: blogs } = useBlogs();
  const { data: targets } = useTargets();

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      keyword_id: '',
      blog_id: '',
    });
  };

  const handleRefresh = () => {
    refetchResults();
    refetchRuns();
  };

  const toggleRun = (runId: number) => {
    setExpandedRuns(prev => 
      prev.includes(runId) 
        ? prev.filter(id => id !== runId)
        : [...prev, runId]
    );
  };

  const toggleAllRuns = () => {
    if (expandedRuns.length === runs?.length) {
      setExpandedRuns([]);
    } else {
      setExpandedRuns(runs?.map(r => r.id) || []);
    }
  };

  // 등록된 대상 블로그인지 확인하는 함수
  const isTargetBlog = (url: string, keywordName: string) => {
    if (!targets || !blogs) return false;
    
    // 현재 크롤링의 키워드 찾기
    const keyword = keywords?.find(k => k.keyword === keywordName);
    if (!keyword) return false;
    
    // 이 키워드와 연결된 타겟들의 블로그 URL 패턴 가져오기
    const keywordTargets = targets.filter(t => t.keyword_id === keyword.id);
    const targetBlogIds = keywordTargets.map(t => t.blog_id);
    const targetBlogs = blogs.filter(b => targetBlogIds.includes(b.id));
    
    // URL이 등록된 블로그 패턴과 일치하는지 확인
    return targetBlogs.some(blog => url.includes(blog.url_pattern));
  };

  // 크롤링 실행별로 결과 그룹화
  const groupedResults = runs?.map(run => {
    const runResults = results?.filter(r => 
      r.crawl_run_id === run.id
    ) || [];
    
    return {
      run,
      results: runResults,
      count: runResults.length,
    };
  }) || [];

  // 키워드별로 결과 그룹화
  const groupedByKeyword = useMemo(() => {
    if (!results || !runs) return [];
    
    const keywordMap = new Map<string, any>();
    
    results.forEach(result => {
      const run = runs.find(r => r.id === result.crawl_run_id);
      if (!run) return;
      
      const keyword = run.keyword || 'Unknown';
      if (!keywordMap.has(keyword)) {
        keywordMap.set(keyword, {
          keyword,
          results: [],
          count: 0,
        });
      }
      
      keywordMap.get(keyword).results.push({ ...result, run });
      keywordMap.get(keyword).count++;
    });
    
    return Array.from(keywordMap.values()).sort((a, b) => 
      b.count - a.count
    );
  }, [results, runs]);

  // 날짜별로 결과 그룹화
  const groupedByDate = useMemo(() => {
    if (!results || !runs) return [];
    
    const dateMap = new Map<string, any>();
    
    results.forEach(result => {
      const run = runs.find(r => r.id === result.crawl_run_id);
      if (!run || !run.started_at) return;
      
      // 날짜만 추출 (YYYY-MM-DD)
      const date = run.started_at.split(' ')[0];
      if (!dateMap.has(date)) {
        dateMap.set(date, {
          date,
          results: [],
          count: 0,
        });
      }
      
      dateMap.get(date).results.push({ ...result, run });
      dateMap.get(date).count++;
    });
    
    // 날짜 역순으로 정렬 (최신이 위)
    return Array.from(dateMap.values()).sort((a, b) => 
      b.date.localeCompare(a.date)
    );
  }, [results, runs]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'running':
        return <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-600" />;
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
          <h1 className="text-3xl font-bold text-gray-900">크롤링 결과</h1>
          <p className="text-gray-600">크롤링으로 수집된 블로그 글 목록을 확인하세요</p>
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
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2"
          >
            <Filter className="h-4 w-4" />
            <span>필터</span>
          </Button>
          <Button
            variant="outline"
            onClick={toggleAllRuns}
            className="flex items-center space-x-2"
          >
            {expandedRuns.length === runs?.length ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            <span>{expandedRuns.length === runs?.length ? '모두 접기' : '모두 펼치기'}</span>
          </Button>
        </div>
      </div>

      {/* View Mode Selector */}
      <div className="flex items-center space-x-2 bg-gray-100 p-1 rounded-lg w-fit">
        <Button
          variant={viewMode === 'runs' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setViewMode('runs')}
          className="flex items-center space-x-2"
        >
          <Clock className="h-4 w-4" />
          <span>실행별</span>
        </Button>
        <Button
          variant={viewMode === 'keywords' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setViewMode('keywords')}
          className="flex items-center space-x-2"
        >
          <Tag className="h-4 w-4" />
          <span>키워드별</span>
        </Button>
        <Button
          variant={viewMode === 'dates' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setViewMode('dates')}
          className="flex items-center space-x-2"
        >
          <Calendar className="h-4 w-4" />
          <span>날짜별</span>
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">총 크롤링 실행</p>
                <p className="text-2xl font-bold text-gray-900">{runs?.length || 0}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">총 결과</p>
                <p className="text-2xl font-bold text-blue-600">{results?.length || 0}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">성공</p>
                <p className="text-2xl font-bold text-green-600">
                  {runs?.filter(r => r.status === 'completed' || r.status === 'success').length || 0}
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
                  {runs?.filter(r => r.status === 'failed' || r.status === 'error').length || 0}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle>필터</CardTitle>
            <CardDescription>결과를 필터링하여 검색하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">키워드</label>
                <select
                  value={filters.keyword_id}
                  onChange={(e) => handleFilterChange('keyword_id', e.target.value)}
                  className="input"
                >
                  <option value="">모든 키워드</option>
                  {keywords?.map((keyword) => (
                    <option key={keyword.id} value={keyword.id}>
                      {keyword.keyword}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">블로그</label>
                <select
                  value={filters.blog_id}
                  onChange={(e) => handleFilterChange('blog_id', e.target.value)}
                  className="input"
                >
                  <option value="">모든 블로그</option>
                  {blogs?.map((blog) => (
                    <option key={blog.id} value={blog.id}>
                      {blog.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <Button variant="outline" onClick={clearFilters} className="w-full">
                  필터 초기화
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results View */}
      <div className="space-y-4">
        {runsLoading || resultsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : !results || results.length === 0 ? (
          <Card>
            <CardContent className="p-8">
              <div className="text-center text-gray-500">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>크롤링 결과가 없습니다</p>
                <p className="text-sm mt-2">크롤링을 실행하여 결과를 수집하세요</p>
              </div>
            </CardContent>
          </Card>
        ) : viewMode === 'keywords' ? (
          /* 키워드별 뷰 */
          groupedByKeyword.map(({ keyword, results: keywordResults, count }) => (
            <Card key={keyword}>
              <CardHeader 
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleRun(keyword as any)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Tag className="h-5 w-5 text-blue-600" />
                    <div>
                      <CardTitle className="text-lg">{keyword}</CardTitle>
                      <CardDescription className="mt-1">
                        <span className="text-xs">
                          {keywordResults.length}개 결과
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{count}</div>
                      <div className="text-xs text-gray-500">결과</div>
                    </div>
                    <Button variant="ghost" size="sm">
                      {expandedRuns.includes(keyword as any) ? (
                        <ChevronUp className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              {expandedRuns.includes(keyword as any) && (
                <CardContent>
                  <div className="space-y-2">
                    {keywordResults.map((result: any) => {
                      const isMyBlog = isTargetBlog(result.url, keyword);
                      
                      return (
                        <div
                          key={result.id}
                          className={`p-3 rounded-lg hover:shadow-sm transition-all ${
                            isMyBlog 
                              ? 'bg-amber-50 border-2 border-amber-400 shadow-md' 
                              : 'bg-white border border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <div className="flex items-center space-x-2 mb-2 flex-wrap">
                            <Badge variant="default" className="bg-blue-500">
                              {result.rank}위
                            </Badge>
                            {isMyBlog && (
                              <Badge variant="default" className="bg-amber-500 flex items-center space-x-1">
                                <Star className="h-3 w-3" />
                                <span>대상 블로그</span>
                              </Badge>
                            )}
                            {result.section && (
                              <Badge variant="outline">{result.section}</Badge>
                            )}
                            <span className="text-xs text-gray-500">
                              {result.run.started_at ? formatRelativeTime(result.run.started_at) : 'N/A'}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 mb-1">
                            {result.title}
                          </h3>
                          <p className="text-sm text-gray-600 mb-2">{result.blog_name}</p>
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline flex items-center space-x-1"
                          >
                            <span>원문 보기</span>
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              )}
            </Card>
          ))
        ) : viewMode === 'dates' ? (
          /* 날짜별 뷰 */
          groupedByDate.map(({ date, results: dateResults, count }) => (
            <Card key={date}>
              <CardHeader 
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleRun(date as any)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Calendar className="h-5 w-5 text-green-600" />
                    <div>
                      <CardTitle className="text-lg">{date}</CardTitle>
                      <CardDescription className="mt-1">
                        <span className="text-xs">
                          {dateResults.length}개 결과
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">{count}</div>
                      <div className="text-xs text-gray-500">결과</div>
                    </div>
                    <Button variant="ghost" size="sm">
                      {expandedRuns.includes(date as any) ? (
                        <ChevronUp className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              {expandedRuns.includes(date as any) && (
                <CardContent>
                  <div className="space-y-2">
                    {dateResults.map((result: any) => {
                      const isMyBlog = isTargetBlog(result.url, result.run.keyword);
                      
                      return (
                        <div
                          key={result.id}
                          className={`p-3 rounded-lg hover:shadow-sm transition-all ${
                            isMyBlog 
                              ? 'bg-amber-50 border-2 border-amber-400 shadow-md' 
                              : 'bg-white border border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <div className="flex items-center space-x-2 mb-2 flex-wrap">
                            <Badge variant="default" className="bg-blue-500">
                              {result.rank}위
                            </Badge>
                            {isMyBlog && (
                              <Badge variant="default" className="bg-amber-500 flex items-center space-x-1">
                                <Star className="h-3 w-3" />
                                <span>대상 블로그</span>
                              </Badge>
                            )}
                            <Badge variant="secondary">{result.run.keyword}</Badge>
                            {result.section && (
                              <Badge variant="outline">{result.section}</Badge>
                            )}
                            <span className="text-xs text-gray-500">
                              {result.run.started_at ? formatRelativeTime(result.run.started_at) : 'N/A'}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 mb-1">
                            {result.title}
                          </h3>
                          <p className="text-sm text-gray-600 mb-2">{result.blog_name}</p>
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline flex items-center space-x-1"
                          >
                            <span>원문 보기</span>
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              )}
            </Card>
          ))
        ) : (
          /* 실행별 뷰 (기본) */
          groupedResults.map(({ run, results: runResults, count }) => (
            <Card key={run.id}>
              <CardHeader 
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleRun(run.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(run.status)}
                    <div>
                      <div className="flex items-center space-x-2">
                        <CardTitle className="text-lg">
                          {run.keyword || 'N/A'} → {run.blog_name || 'N/A'}
                        </CardTitle>
                        <Badge variant={getStatusBadgeVariant(run.status)}>
                          {(run.status === 'success' || run.status === 'completed') ? '완료' : (run.status === 'error' || run.status === 'failed') ? '실패' : run.status === 'running' ? '실행 중' : run.status}
                        </Badge>
                      </div>
                      <CardDescription className="mt-1">
                        <span className="text-xs">
                          실행 #{run.id} • {run.started_at ? formatRelativeTime(run.started_at) : 'N/A'}
                          {run.completed_at && ` • 완료: ${formatRelativeTime(run.completed_at)}`}
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{count}</div>
                      <div className="text-xs text-gray-500">결과</div>
                    </div>
                    <Button variant="ghost" size="sm">
                      {expandedRuns.includes(run.id) ? (
                        <ChevronUp className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </div>
                {run.error_message && !expandedRuns.includes(run.id) && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <strong>오류:</strong> {run.error_message.split('\n')[0]}
                  </div>
                )}
              </CardHeader>
              
              {expandedRuns.includes(run.id) && (
                <CardContent>
                  {run.error_message && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 whitespace-pre-wrap">
                      <strong>오류 상세:</strong><br />
                      {run.error_message}
                    </div>
                  )}
                  
                  {runResults.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>이 크롤링 실행에서 수집된 결과가 없습니다</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* 섹션별로 그룹화 */}
                      {(() => {
                        // 섹션별로 결과 그룹화
                        const sections = new Map<string, typeof runResults>();
                        runResults.forEach(result => {
                          // section이 있는 결과만 그룹화
                          if (result.section) {
                            const section = result.section;
                            
                            if (!sections.has(section)) {
                              sections.set(section, []);
                            }
                            sections.get(section)?.push(result);
                          }
                        });

                        // 섹션이 없으면 일반 목록으로 표시
                        if (sections.size === 0) {
                          return (
                            <div className="space-y-2">
                              {runResults.map((result) => {
                                const isMyBlog = isTargetBlog(result.url, result.keyword);
                                
                                return (
                                  <div
                                    key={result.id}
                                    className={`p-3 rounded-lg hover:shadow-sm transition-all ${
                                      isMyBlog 
                                        ? 'bg-amber-50 border-2 border-amber-400 shadow-md' 
                                        : 'bg-white border border-gray-200 hover:border-blue-300'
                                    }`}
                                  >
                                    <div className="flex items-center space-x-2 mb-2 flex-wrap">
                                      <Badge variant="default" className="bg-blue-500">
                                        {result.rank}위
                                      </Badge>
                                      {isMyBlog && (
                                        <Badge variant="default" className="bg-amber-500 flex items-center space-x-1">
                                          <Star className="h-3 w-3 fill-white" />
                                          <span>대상 블로그</span>
                                        </Badge>
                                      )}
                                      <h4 className={`font-medium flex-1 ${isMyBlog ? 'text-amber-900' : 'text-gray-900'}`}>
                                        {result.title}
                                      </h4>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-2">{result.snippet}</p>
                                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                                      <span>⏱️ {formatRelativeTime(result.created_at)}</span>
                                      <a 
                                        href={result.url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className={`flex items-center space-x-1 hover:underline font-medium ${
                                          isMyBlog ? 'text-amber-700' : 'text-blue-600'
                                        }`}
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <ExternalLink className="h-3 w-3" />
                                        <span>원본 보기</span>
                                      </a>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          );
                        }

                        return Array.from(sections.entries()).map(([sectionName, sectionResults]) => (
                          <div key={sectionName} className="border-l-4 border-purple-500 pl-4 bg-purple-50/30 p-3 rounded-r-lg">
                            <div className="flex items-center space-x-2 mb-3">
                              <Badge variant="outline" className="bg-purple-100 text-purple-800 border-purple-300 font-semibold">
                                📍 {sectionName}
                              </Badge>
                              <span className="text-sm font-medium text-purple-700">
                                {sectionResults.length}개 결과
                              </span>
                            </div>
                            
                            <div className="space-y-2">
                              {sectionResults.map((result, index) => {
                                const isMyBlog = isTargetBlog(result.url, result.keyword);
                                
                                return (
                                  <div
                                    key={result.id}
                                    className={`p-3 rounded-lg hover:shadow-sm transition-all ${
                                      isMyBlog 
                                        ? 'bg-amber-50 border-2 border-amber-400 shadow-md' 
                                        : 'bg-white border border-gray-200 hover:border-blue-300'
                                    }`}
                                  >
                                    <div className="flex items-center space-x-2 mb-2 flex-wrap">
                                      <Badge variant="default" className="bg-blue-500">
                                        {index + 1}위
                                      </Badge>
                                      <span className="text-xs text-gray-500">(전체 {result.rank}위)</span>
                                      {isMyBlog && (
                                        <Badge variant="default" className="bg-amber-500 flex items-center space-x-1">
                                          <Star className="h-3 w-3 fill-white" />
                                          <span>대상 블로그</span>
                                        </Badge>
                                      )}
                                      <h4 className={`font-medium flex-1 ${isMyBlog ? 'text-amber-900' : 'text-gray-900'}`}>
                                        {result.title}
                                      </h4>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-2">{result.snippet}</p>
                                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                                      <span>⏱️ {formatRelativeTime(result.created_at)}</span>
                                      <a 
                                        href={result.url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className={`flex items-center space-x-1 hover:underline font-medium ${
                                          isMyBlog ? 'text-amber-700' : 'text-blue-600'
                                        }`}
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <ExternalLink className="h-3 w-3" />
                                        <span>원본 보기</span>
                                      </a>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ));
                      })()}
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
};