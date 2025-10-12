import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FileText, Eye, Trash2, Upload, Check, Copy } from 'lucide-react';
import toast from 'react-hot-toast';

interface GeneratedPost {
  id: number;
  keyword_id: number;
  crawl_run_id: number;
  title: string;
  content: string;
  summary: string | null;
  tags: string | null;
  status: string;
  created_at: string;
  published_at: string | null;
}

export const GeneratedPostsPage: React.FC = () => {
  const [posts, setPosts] = useState<GeneratedPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPost, setSelectedPost] = useState<GeneratedPost | null>(null);
  const [showModal, setShowModal] = useState(false);

  // 생성된 글 목록 조회
  const fetchPosts = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8001/api/generated-posts?limit=100', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPosts(data);
      } else {
        toast.error('글 목록을 불러오는데 실패했습니다.');
      }
    } catch (error) {
      toast.error('서버 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchPosts();
  }, []);

  // 글 상세 보기
  const handleViewPost = (post: GeneratedPost) => {
    setSelectedPost(post);
    setShowModal(true);
  };

  // DSL 콘텐츠 복사
  const handleCopyDSL = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('DSL 콘텐츠가 클립보드에 복사되었습니다!');
  };

  // 발행 준비
  const handlePreparePublish = async (postId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8001/api/generated-posts/${postId}/prepare-publish`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        await response.json();
        toast.success('발행 준비 완료! DSL 콘텐츠를 확인하세요.');
        
        // 상세 정보 모달 표시
        const post = posts.find(p => p.id === postId);
        if (post) {
          setSelectedPost(post);
          setShowModal(true);
        }
        
        fetchPosts(); // 목록 새로고침
      } else {
        toast.error('발행 준비에 실패했습니다.');
      }
    } catch (error) {
      toast.error('서버 오류가 발생했습니다.');
    }
  };

  // 발행 완료 표시
  const handleMarkPublished = async (postId: number) => {
    const blogUrl = prompt('발행된 블로그 URL을 입력하세요 (선택사항):');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8001/api/generated-posts/${postId}/mark-published`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ blog_url: blogUrl || null })
      });

      if (response.ok) {
        toast.success('발행 완료로 표시되었습니다!');
        fetchPosts(); // 목록 새로고침
      } else {
        toast.error('표시 변경에 실패했습니다.');
      }
    } catch (error) {
      toast.error('서버 오류가 발생했습니다.');
    }
  };

  // 글 삭제
  const handleDelete = async (postId: number) => {
    if (!confirm('정말로 이 글을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8001/api/generated-posts/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        toast.success('글이 삭제되었습니다.');
        fetchPosts(); // 목록 새로고침
      } else {
        toast.error('삭제에 실패했습니다.');
      }
    } catch (error) {
      toast.error('서버 오류가 발생했습니다.');
    }
  };

  // 상태 뱃지
  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; variant: any; icon: React.ReactNode }> = {
      'generated': { label: '생성됨', variant: 'secondary', icon: <FileText className="h-3 w-3" /> },
      'ready_to_publish': { label: '발행 준비', variant: 'default', icon: <Upload className="h-3 w-3" /> },
      'published': { label: '발행됨', variant: 'default', icon: <Check className="h-3 w-3" /> },
      'failed': { label: '실패', variant: 'destructive', icon: null },
    };

    const config = statusConfig[status] || { label: status, variant: 'outline', icon: null };

    return (
      <Badge variant={config.variant} className="flex items-center space-x-1">
        {config.icon}
        <span>{config.label}</span>
      </Badge>
    );
  };

  // DSL 태그 제거 (미리보기용)
  const cleanDSLTags = (text: string) => {
    return text
      .replace(/\[title\](.*?)\[\/title\]/g, '$1')
      .replace(/\[bold\](.*?)\[\/bold\]/g, '$1')
      .replace(/\[underline\](.*?)\[\/underline\]/g, '$1')
      .replace(/\[italic\](.*?)\[\/italic\]/g, '$1')
      .replace(/\[separator=.*?\]\[\/separator\]/g, '')
      .replace(/\[quote=(.*?)\]/g, '$1')
      .replace(/\[align=.*?\](.*?)\[\/align\]/g, '$1')
      .replace(/\[img=.*?\]\[\/img\]/g, '')
      .trim();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">생성된 블로그 글</h1>
          <p className="text-gray-600">AI가 자동으로 생성한 블로그 글을 관리하세요</p>
        </div>
        <Button onClick={fetchPosts} variant="outline">
          새로고침
        </Button>
      </div>

      {/* 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">총 생성</p>
                <p className="text-2xl font-bold text-gray-900">{posts.length}</p>
              </div>
              <FileText className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">발행 대기</p>
                <p className="text-2xl font-bold text-blue-600">
                  {posts.filter(p => p.status === 'generated' || p.status === 'ready_to_publish').length}
                </p>
              </div>
              <Upload className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">발행 완료</p>
                <p className="text-2xl font-bold text-green-600">
                  {posts.filter(p => p.status === 'published').length}
                </p>
              </div>
              <Check className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">실패</p>
                <p className="text-2xl font-bold text-red-600">
                  {posts.filter(p => p.status === 'failed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 글 목록 */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : posts.length === 0 ? (
          <Card>
            <CardContent className="p-8">
              <div className="text-center text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>생성된 블로그 글이 없습니다</p>
                <p className="text-sm mt-2">크롤링 시 타겟 블로그가 없으면 자동으로 생성됩니다</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          posts.map((post) => (
            <Card key={post.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {getStatusBadge(post.status)}
                      <Badge variant="outline">ID: {post.id}</Badge>
                    </div>
                    <CardTitle className="text-lg">
                      {cleanDSLTags(post.title)}
                    </CardTitle>
                    {post.summary && (
                      <CardDescription className="mt-2">
                        {post.summary}
                      </CardDescription>
                    )}
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>생성: {new Date(post.created_at).toLocaleString('ko-KR')}</span>
                      {post.published_at && (
                        <span>발행: {new Date(post.published_at).toLocaleString('ko-KR')}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewPost(post)}
                      className="flex items-center space-x-1"
                    >
                      <Eye className="h-4 w-4" />
                      <span>보기</span>
                    </Button>
                    
                    {post.status === 'generated' && (
                      <Button
                        size="sm"
                        onClick={() => handlePreparePublish(post.id)}
                        className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-700"
                      >
                        <Upload className="h-4 w-4" />
                        <span>발행 준비</span>
                      </Button>
                    )}
                    
                    {post.status === 'ready_to_publish' && (
                      <Button
                        size="sm"
                        onClick={() => handleMarkPublished(post.id)}
                        className="flex items-center space-x-1 bg-green-600 hover:bg-green-700"
                      >
                        <Check className="h-4 w-4" />
                        <span>발행 완료</span>
                      </Button>
                    )}
                    
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(post.id)}
                      className="flex items-center space-x-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))
        )}
      </div>

      {/* 상세 보기 모달 */}
      {showModal && selectedPost && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold">
                {cleanDSLTags(selectedPost.title)}
              </h2>
              <Button variant="ghost" onClick={() => setShowModal(false)}>
                ✕
              </Button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* 메타 정보 */}
              <div className="flex items-center space-x-4">
                {getStatusBadge(selectedPost.status)}
                <span className="text-sm text-gray-500">
                  생성: {new Date(selectedPost.created_at).toLocaleString('ko-KR')}
                </span>
              </div>

              {/* 요약 */}
              {selectedPost.summary && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">📋 요약</h3>
                  <p className="text-blue-800">{selectedPost.summary}</p>
                </div>
              )}

              {/* 태그 */}
              {selectedPost.tags && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">🏷️ 태그</h3>
                  <div className="flex flex-wrap gap-2">
                    {JSON.parse(selectedPost.tags).map((tag: string, index: number) => (
                      <Badge key={index} variant="outline">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* DSL 원본 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">📝 DSL 원본 (네이버 블로그용)</h3>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopyDSL(selectedPost.content)}
                    className="flex items-center space-x-1"
                  >
                    <Copy className="h-4 w-4" />
                    <span>복사</span>
                  </Button>
                </div>
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg font-mono text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {selectedPost.content}
                </div>
              </div>

              {/* 미리보기 */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">👁️ 미리보기 (태그 제거)</h3>
                <div className="p-4 bg-white border border-gray-200 rounded-lg whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {cleanDSLTags(selectedPost.content)}
                </div>
              </div>

              {/* 발행 가이드 */}
              {selectedPost.status !== 'published' && (
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <h3 className="font-semibold text-purple-900 mb-2">📖 네이버 블로그 발행 방법</h3>
                  <ol className="text-sm text-purple-800 space-y-2 list-decimal list-inside">
                    <li><strong>네이버 블로그 접속</strong>: blog.naver.com</li>
                    <li><strong>글쓰기 클릭</strong>: 우측 상단 "글쓰기" 버튼</li>
                    <li><strong>제목 입력</strong>: 위의 제목 복사</li>
                    <li><strong>본문 입력</strong>: 
                      <ul className="ml-6 mt-1 space-y-1">
                        <li>• DSL 원본 복사 (복사 버튼 클릭)</li>
                        <li>• 스마트에디터에 붙여넣기</li>
                        <li>• DSL 태그가 자동으로 서식 적용됨</li>
                      </ul>
                    </li>
                    <li><strong>태그 추가</strong>: 하단의 태그 입력</li>
                    <li><strong>발행</strong>: "발행하기" 버튼 클릭</li>
                    <li><strong>완료 표시</strong>: 이 페이지에서 "발행 완료" 버튼 클릭</li>
                  </ol>
                </div>
              )}

              {/* 액션 버튼 */}
              <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => handleCopyDSL(selectedPost.content)}
                  className="flex items-center space-x-2"
                >
                  <Copy className="h-4 w-4" />
                  <span>DSL 복사</span>
                </Button>
                
                {selectedPost.status === 'ready_to_publish' && (
                  <Button
                    onClick={() => handleMarkPublished(selectedPost.id)}
                    className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
                  >
                    <Check className="h-4 w-4" />
                    <span>발행 완료</span>
                  </Button>
                )}
                
                <Button variant="ghost" onClick={() => setShowModal(false)}>
                  닫기
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

