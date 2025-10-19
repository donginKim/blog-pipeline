import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useTargets, useCreateTarget, useUpdateTarget, useDeleteTarget, useTriggerCrawlForTarget, useKeywords, useBlogs } from '@/hooks/useApi';
import { formatDate } from '@/utils';
import { Plus, Edit, Trash2, Play, Target, Link, Unlink, CheckSquare, Square } from 'lucide-react';

export const TargetsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [editingTarget, setEditingTarget] = useState<number | null>(null);
  const [selectedTargets, setSelectedTargets] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    keyword_id: 0,
    blog_id: 0,
  });
  const [bulkFormData, setBulkFormData] = useState({
    blog_id: 0,
    keyword_ids: [] as number[],
  });

  const { data: targets, isLoading } = useTargets();
  const { data: keywords } = useKeywords();
  const { data: blogs } = useBlogs();
  const createTarget = useCreateTarget();
  const updateTarget = useUpdateTarget();
  const deleteTarget = useDeleteTarget();
  const triggerTargetCrawl = useTriggerCrawlForTarget();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingTarget) {
      await updateTarget.mutateAsync({
        id: editingTarget,
        data: { is_active: true },
      });
      setEditingTarget(null);
    } else {
      await createTarget.mutateAsync(formData);
    }
    
    setFormData({ keyword_id: 0, blog_id: 0 });
    setShowForm(false);
  };

  const handleEdit = (target: any) => {
    setFormData({
      keyword_id: target.keyword_id,
      blog_id: target.blog_id,
    });
    setEditingTarget(target.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('정말로 이 타겟을 삭제하시겠습니까?')) {
      await deleteTarget.mutateAsync(id);
    }
  };

  const handleTriggerCrawl = async (id: number) => {
    await triggerTargetCrawl.mutateAsync(id);
  };

  const handleBulkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (bulkFormData.blog_id === 0 || bulkFormData.keyword_ids.length === 0) {
      alert('블로그와 키워드를 선택해주세요.');
      return;
    }

    try {
      // 선택된 키워드들에 대해 타겟 생성
      for (const keywordId of bulkFormData.keyword_ids) {
        await createTarget.mutateAsync({
          keyword_id: keywordId,
          blog_id: bulkFormData.blog_id,
        });
      }
      
      setBulkFormData({ blog_id: 0, keyword_ids: [] });
      setShowBulkForm(false);
    } catch (error) {
      console.error('일괄 연결 실패:', error);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedTargets.length === 0) {
      alert('삭제할 타겟을 선택해주세요.');
      return;
    }

    if (!window.confirm(`선택된 ${selectedTargets.length}개의 타겟을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      for (const targetId of selectedTargets) {
        await deleteTarget.mutateAsync(targetId);
      }
      setSelectedTargets([]);
    } catch (error) {
      console.error('일괄 삭제 실패:', error);
    }
  };

  const handleSelectTarget = (targetId: number) => {
    setSelectedTargets(prev => 
      prev.includes(targetId) 
        ? prev.filter(id => id !== targetId)
        : [...prev, targetId]
    );
  };

  const handleSelectAll = () => {
    if (selectedTargets.length === targets?.length) {
      setSelectedTargets([]);
    } else {
      setSelectedTargets(targets?.map(t => t.id) || []);
    }
  };

  const handleKeywordSelect = (keywordId: number) => {
    setBulkFormData(prev => ({
      ...prev,
      keyword_ids: prev.keyword_ids.includes(keywordId)
        ? prev.keyword_ids.filter(id => id !== keywordId)
        : [...prev.keyword_ids, keywordId]
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">타겟 관리</h1>
          <p className="text-gray-600">키워드와 블로그를 연결하여 모니터링 타겟을 관리하세요</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => {
              setShowBulkForm(true);
              setBulkFormData({ blog_id: 0, keyword_ids: [] });
            }}
            className="flex items-center space-x-2"
          >
            <Link className="h-4 w-4" />
            <span>일괄 연결</span>
          </Button>
          <Button
            variant="outline"
            onClick={handleBulkDelete}
            disabled={selectedTargets.length === 0}
            className="flex items-center space-x-2"
          >
            <Unlink className="h-4 w-4" />
            <span>일괄 삭제 ({selectedTargets.length})</span>
          </Button>
          <Button
            onClick={() => {
              setShowForm(true);
              setEditingTarget(null);
              setFormData({ keyword_id: 0, blog_id: 0 });
            }}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>타겟 추가</span>
          </Button>
        </div>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingTarget ? '타겟 수정' : '타겟 추가'}</CardTitle>
            <CardDescription>
              {editingTarget ? '타겟 정보를 수정하세요' : '새로운 타겟을 추가하세요'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">키워드</label>
                <select
                  value={formData.keyword_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, keyword_id: parseInt(e.target.value) }))}
                  className="input"
                  required
                >
                  <option value={0}>키워드를 선택하세요</option>
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
                  value={formData.blog_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, blog_id: parseInt(e.target.value) }))}
                  className="input"
                  required
                >
                  <option value={0}>블로그를 선택하세요</option>
                  {blogs?.map((blog) => (
                    <option key={blog.id} value={blog.id}>
                      {blog.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex space-x-2">
                <Button
                  type="submit"
                  loading={createTarget.isLoading || updateTarget.isLoading}
                  disabled={formData.keyword_id === 0 || formData.blog_id === 0}
                >
                  {editingTarget ? '수정' : '추가'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowForm(false);
                    setEditingTarget(null);
                    setFormData({ keyword_id: 0, blog_id: 0 });
                  }}
                >
                  취소
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Bulk Connect Form */}
      {showBulkForm && (
        <Card>
          <CardHeader>
            <CardTitle>일괄 연결</CardTitle>
            <CardDescription>
              하나의 블로그를 여러 키워드에 연결합니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleBulkSubmit} className="space-y-4">
              <div>
                <label className="label">블로그</label>
                <select
                  value={bulkFormData.blog_id}
                  onChange={(e) => setBulkFormData(prev => ({ ...prev, blog_id: parseInt(e.target.value) }))}
                  className="input"
                  required
                >
                  <option value={0}>블로그를 선택하세요</option>
                  {blogs?.map((blog) => (
                    <option key={blog.id} value={blog.id}>
                      {blog.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="label">연결할 키워드들</label>
                <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto border rounded p-2">
                  {keywords?.map((keyword) => (
                    <label key={keyword.id} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={bulkFormData.keyword_ids.includes(keyword.id)}
                        onChange={() => handleKeywordSelect(keyword.id)}
                        className="rounded"
                      />
                      <span className="text-sm">{keyword.keyword}</span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  선택된 키워드: {bulkFormData.keyword_ids.length}개
                </p>
              </div>
              
              <div className="flex space-x-2">
                <Button
                  type="submit"
                  loading={createTarget.isLoading}
                  disabled={bulkFormData.blog_id === 0 || bulkFormData.keyword_ids.length === 0}
                >
                  일괄 연결
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowBulkForm(false);
                    setBulkFormData({ blog_id: 0, keyword_ids: [] });
                  }}
                >
                  취소
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Targets List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>타겟 목록</CardTitle>
              <CardDescription>
                총 {targets?.length || 0}개의 타겟이 있습니다
                {selectedTargets.length > 0 && (
                  <span className="ml-2 text-blue-600">
                    ({selectedTargets.length}개 선택됨)
                  </span>
                )}
              </CardDescription>
            </div>
            {targets && targets.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
                className="flex items-center space-x-2"
              >
                {selectedTargets.length === targets.length ? (
                  <CheckSquare className="h-4 w-4" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
                <span>전체 선택</span>
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : !targets || targets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              등록된 타겟이 없습니다
            </div>
          ) : (
            <div className="space-y-3">
              {targets.map((target) => (
                <div
                  key={target.id}
                  className={`flex items-center justify-between p-4 rounded-lg transition-colors ${
                    selectedTargets.includes(target.id) 
                      ? 'bg-blue-50 border border-blue-200' 
                      : 'bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={selectedTargets.includes(target.id)}
                      onChange={() => handleSelectTarget(target.id)}
                      className="rounded"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <Target className="h-5 w-5 text-gray-500" />
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{target.keyword}</Badge>
                          <span className="text-gray-400">→</span>
                          <Badge variant="outline">{target.blog_name}</Badge>
                        </div>
                        <Badge variant={target.is_active ? 'success' : 'secondary'}>
                          {target.is_active ? '활성' : '비활성'}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        생성일: {formatDate(target.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTriggerCrawl(target.id)}
                      disabled={triggerTargetCrawl.isLoading}
                      className="hover:bg-green-50"
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(target)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(target.id)}
                      loading={deleteTarget.isLoading}
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
