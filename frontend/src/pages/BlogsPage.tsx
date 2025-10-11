import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { useBlogs, useCreateBlog, useUpdateBlog, useDeleteBlog } from '@/hooks/useApi';
import { formatDate } from '@/utils';
import { Plus, Edit, Trash2, Search, Globe } from 'lucide-react';

export const BlogsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingBlog, setEditingBlog] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    url_pattern: '',
    description: '',
  });
  const [searchTerm, setSearchTerm] = useState('');

  const { data: blogs, isLoading } = useBlogs();
  const createBlog = useCreateBlog();
  const updateBlog = useUpdateBlog();
  const deleteBlog = useDeleteBlog();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingBlog) {
      await updateBlog.mutateAsync({
        id: editingBlog,
        data: formData,
      });
      setEditingBlog(null);
    } else {
      await createBlog.mutateAsync(formData);
    }
    
    setFormData({ name: '', url_pattern: '', description: '' });
    setShowForm(false);
  };

  const handleEdit = (blog: any) => {
    setFormData({
      name: blog.name,
      url_pattern: blog.url_pattern,
      description: blog.description || '',
    });
    setEditingBlog(blog.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('정말로 이 블로그를 삭제하시겠습니까?')) {
      await deleteBlog.mutateAsync(id);
    }
  };

  const filteredBlogs = blogs?.filter(blog =>
    blog.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    blog.url_pattern.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (blog.description && blog.description.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">블로그 관리</h1>
          <p className="text-gray-600">모니터링할 블로그를 관리하세요</p>
        </div>
        <Button
          onClick={() => {
            setShowForm(true);
            setEditingBlog(null);
            setFormData({ name: '', url_pattern: '', description: '' });
          }}
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>블로그 추가</span>
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="블로그 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Add/Edit Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingBlog ? '블로그 수정' : '블로그 추가'}</CardTitle>
            <CardDescription>
              {editingBlog ? '블로그 정보를 수정하세요' : '새로운 블로그를 추가하세요'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="블로그 이름"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="블로그 이름을 입력하세요"
                required
              />
              <Input
                label="URL 패턴"
                value={formData.url_pattern}
                onChange={(e) => setFormData(prev => ({ ...prev, url_pattern: e.target.value }))}
                placeholder="https://blog.naver.com/myid"
                required
              />
              <Input
                label="설명 (선택사항)"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="블로그에 대한 설명을 입력하세요"
              />
              <div className="flex space-x-2">
                <Button
                  type="submit"
                  loading={createBlog.isLoading || updateBlog.isLoading}
                >
                  {editingBlog ? '수정' : '추가'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowForm(false);
                    setEditingBlog(null);
                    setFormData({ name: '', url_pattern: '', description: '' });
                  }}
                >
                  취소
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Blogs List */}
      <Card>
        <CardHeader>
          <CardTitle>블로그 목록</CardTitle>
          <CardDescription>
            총 {filteredBlogs.length}개의 블로그가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredBlogs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchTerm ? '검색 결과가 없습니다' : '등록된 블로그가 없습니다'}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredBlogs.map((blog) => (
                <div
                  key={blog.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <Globe className="h-5 w-5 text-gray-500" />
                      <h3 className="font-medium text-gray-900">{blog.name}</h3>
                      <Badge variant={blog.is_active ? 'success' : 'secondary'}>
                        {blog.is_active ? '활성' : '비활성'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-1 font-mono">{blog.url_pattern}</p>
                    {blog.description && (
                      <p className="text-sm text-gray-600 mt-1">{blog.description}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      생성일: {formatDate(blog.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(blog)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(blog.id)}
                      loading={deleteBlog.isLoading}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

