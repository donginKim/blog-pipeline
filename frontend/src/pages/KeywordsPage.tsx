import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { useKeywords, useCreateKeyword, useUpdateKeyword, useDeleteKeyword, useUploadKeywordsExcel } from '@/hooks/useApi';
import { formatDate } from '@/utils';
import { Plus, Edit, Trash2, Search, Upload, Download } from 'lucide-react';

export const KeywordsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingKeyword, setEditingKeyword] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    keyword: '',
    description: '',
  });
  const [searchTerm, setSearchTerm] = useState('');

  const { data: keywords, isLoading } = useKeywords();
  const createKeyword = useCreateKeyword();
  const updateKeyword = useUpdateKeyword();
  const deleteKeyword = useDeleteKeyword();
  const uploadExcel = useUploadKeywordsExcel();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingKeyword) {
      await updateKeyword.mutateAsync({
        id: editingKeyword,
        data: formData,
      });
      setEditingKeyword(null);
    } else {
      await createKeyword.mutateAsync(formData);
    }
    
    setFormData({ keyword: '', description: '' });
    setShowForm(false);
  };

  const handleEdit = (keyword: any) => {
    setFormData({
      keyword: keyword.keyword,
      description: keyword.description || '',
    });
    setEditingKeyword(keyword.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('정말로 이 키워드를 삭제하시겠습니까?')) {
      await deleteKeyword.mutateAsync(id);
    }
  };

  const filteredKeywords = keywords?.filter(keyword =>
    keyword.keyword.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (keyword.description && keyword.description.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadExcel.mutate(file);
    }
    // 파일 입력 초기화
    event.target.value = '';
  };

  const downloadTemplate = () => {
    const csvContent = "keyword,description\n파이썬,Python 프로그래밍\n자바스크립트,JavaScript 개발\n리액트,React 프론트엔드";
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'keywords_template.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">키워드 관리</h1>
          <p className="text-gray-600">검색할 키워드를 관리하세요</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={downloadTemplate}
            className="flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>템플릿 다운로드</span>
          </Button>
          <div className="relative">
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileUpload}
              className="hidden"
              id="excel-upload"
            />
            <label htmlFor="excel-upload" className="cursor-pointer">
              <div className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 space-x-2">
                <Upload className="h-4 w-4" />
                <span>{uploadExcel.isLoading ? '업로드 중...' : '엑셀 업로드'}</span>
              </div>
            </label>
          </div>
          <Button
            onClick={() => {
              setShowForm(true);
              setEditingKeyword(null);
              setFormData({ keyword: '', description: '' });
            }}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>키워드 추가</span>
          </Button>
        </div>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="키워드 검색..."
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
            <CardTitle>{editingKeyword ? '키워드 수정' : '키워드 추가'}</CardTitle>
            <CardDescription>
              {editingKeyword ? '키워드 정보를 수정하세요' : '새로운 키워드를 추가하세요'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="키워드"
                value={formData.keyword}
                onChange={(e) => setFormData(prev => ({ ...prev, keyword: e.target.value }))}
                placeholder="검색할 키워드를 입력하세요"
                required
              />
              <Input
                label="설명 (선택사항)"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="키워드에 대한 설명을 입력하세요"
              />
              <div className="flex space-x-2">
                <Button
                  type="submit"
                  loading={createKeyword.isLoading || updateKeyword.isLoading}
                >
                  {editingKeyword ? '수정' : '추가'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowForm(false);
                    setEditingKeyword(null);
                    setFormData({ keyword: '', description: '' });
                  }}
                >
                  취소
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Keywords List */}
      <Card>
        <CardHeader>
          <CardTitle>키워드 목록</CardTitle>
          <CardDescription>
            총 {filteredKeywords.length}개의 키워드가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredKeywords.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchTerm ? '검색 결과가 없습니다' : '등록된 키워드가 없습니다'}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredKeywords.map((keyword) => (
                <div
                  key={keyword.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-medium text-gray-900">{keyword.keyword}</h3>
                      <Badge variant={keyword.is_active ? 'success' : 'secondary'}>
                        {keyword.is_active ? '활성' : '비활성'}
                      </Badge>
                    </div>
                    {keyword.description && (
                      <p className="text-sm text-gray-600 mt-1">{keyword.description}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      생성일: {formatDate(keyword.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(keyword)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(keyword.id)}
                      loading={deleteKeyword.isLoading}
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
