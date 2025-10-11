import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '@/services/api';
import {
  Keyword,
  KeywordCreate,
  KeywordUpdate,
  Blog,
  BlogCreate,
  BlogUpdate,
  KeywordTarget,
  KeywordTargetCreate,
  KeywordTargetUpdate,
  CrawlResult,
  CrawlRun,
  DashboardStats,
  RecentActivity,
} from '@/types';
import toast from 'react-hot-toast';

// Keywords hooks
export const useKeywords = (params?: { skip?: number; limit?: number; is_active?: boolean }) => {
  return useQuery(['keywords', params], () => apiService.getKeywords(params));
};

export const useKeyword = (id: number) => {
  return useQuery(['keyword', id], () => apiService.getKeyword(id), {
    enabled: !!id,
  });
};

export const useCreateKeyword = () => {
  const queryClient = useQueryClient();
  
  return useMutation((data: KeywordCreate) => apiService.createKeyword(data), {
    onSuccess: () => {
      queryClient.invalidateQueries(['keywords']);
      toast.success('키워드가 생성되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '키워드 생성에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useUpdateKeyword = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ id, data }: { id: number; data: KeywordUpdate }) => apiService.updateKeyword(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries(['keywords']);
        queryClient.invalidateQueries(['keyword', id]);
        toast.success('키워드가 업데이트되었습니다.');
      },
      onError: (error: any) => {
        const message = error.response?.data?.detail || '키워드 업데이트에 실패했습니다.';
        toast.error(message);
      },
    }
  );
};

export const useDeleteKeyword = () => {
  const queryClient = useQueryClient();
  
  return useMutation((id: number) => apiService.deleteKeyword(id), {
    onSuccess: () => {
      queryClient.invalidateQueries(['keywords']);
      toast.success('키워드가 삭제되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '키워드 삭제에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useUploadKeywordsExcel = () => {
  const queryClient = useQueryClient();
  
  return useMutation((file: File) => apiService.uploadKeywordsExcel(file), {
    onSuccess: (data) => {
      queryClient.invalidateQueries(['keywords']);
      if (data.error_count > 0) {
        toast.success(`키워드 업로드 완료: 성공 ${data.success_count}개, 실패 ${data.error_count}개`);
        if (data.errors.length > 0) {
          console.warn('업로드 오류:', data.errors);
        }
      } else {
        toast.success(`키워드 ${data.success_count}개가 성공적으로 업로드되었습니다.`);
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '엑셀 파일 업로드에 실패했습니다.';
      toast.error(message);
    },
  });
};

// Blogs hooks
export const useBlogs = (params?: { skip?: number; limit?: number; is_active?: boolean }) => {
  return useQuery(['blogs', params], () => apiService.getBlogs(params));
};

export const useBlog = (id: number) => {
  return useQuery(['blog', id], () => apiService.getBlog(id), {
    enabled: !!id,
  });
};

export const useCreateBlog = () => {
  const queryClient = useQueryClient();
  
  return useMutation((data: BlogCreate) => apiService.createBlog(data), {
    onSuccess: () => {
      queryClient.invalidateQueries(['blogs']);
      toast.success('블로그가 생성되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '블로그 생성에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useUpdateBlog = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ id, data }: { id: number; data: BlogUpdate }) => apiService.updateBlog(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries(['blogs']);
        queryClient.invalidateQueries(['blog', id]);
        toast.success('블로그가 업데이트되었습니다.');
      },
      onError: (error: any) => {
        const message = error.response?.data?.detail || '블로그 업데이트에 실패했습니다.';
        toast.error(message);
      },
    }
  );
};

export const useDeleteBlog = () => {
  const queryClient = useQueryClient();
  
  return useMutation((id: number) => apiService.deleteBlog(id), {
    onSuccess: () => {
      queryClient.invalidateQueries(['blogs']);
      toast.success('블로그가 삭제되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '블로그 삭제에 실패했습니다.';
      toast.error(message);
    },
  });
};

// Targets hooks
export const useTargets = (params?: {
  skip?: number;
  limit?: number;
  keyword_id?: number;
  blog_id?: number;
  is_active?: boolean;
}) => {
  return useQuery(['targets', params], () => apiService.getTargets(params));
};

export const useTarget = (id: number) => {
  return useQuery(['target', id], () => apiService.getTarget(id), {
    enabled: !!id,
  });
};

export const useCreateTarget = () => {
  const queryClient = useQueryClient();
  
  return useMutation((data: KeywordTargetCreate) => apiService.createTarget(data), {
    onSuccess: () => {
      queryClient.invalidateQueries(['targets']);
      toast.success('타겟이 생성되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '타겟 생성에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useUpdateTarget = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ id, data }: { id: number; data: KeywordTargetUpdate }) => apiService.updateTarget(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries(['targets']);
        queryClient.invalidateQueries(['target', id]);
        toast.success('타겟이 업데이트되었습니다.');
      },
      onError: (error: any) => {
        const message = error.response?.data?.detail || '타겟 업데이트에 실패했습니다.';
        toast.error(message);
      },
    }
  );
};

export const useDeleteTarget = () => {
  const queryClient = useQueryClient();
  
  return useMutation((id: number) => apiService.deleteTarget(id), {
    onSuccess: () => {
      queryClient.invalidateQueries(['targets']);
      toast.success('타겟이 삭제되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '타겟 삭제에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useTriggerCrawlForTarget = () => {
  const queryClient = useQueryClient();
  
  return useMutation((id: number) => apiService.triggerCrawlForTarget(id), {
    onSuccess: (data) => {
      queryClient.invalidateQueries(['crawlRuns']);
      queryClient.invalidateQueries(['recentActivity']);
      queryClient.invalidateQueries(['crawlResults']);
      toast.success(data.message || '크롤링 작업이 시작되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '크롤링 시작에 실패했습니다.';
      toast.error(message);
    },
  });
};

// Results hooks
export const useResults = (params?: {
  keyword_id?: number;
  blog_id?: number;
  found?: boolean;
  run_date_from?: string;
  run_date_to?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery(['results', params], () => apiService.getResults(params));
};

export const useResultStats = (params?: {
  keyword_id?: number;
  blog_id?: number;
  run_date_from?: string;
  run_date_to?: string;
}) => {
  return useQuery(['resultStats', params], () => apiService.getResultStats(params));
};

export const useCrawlRuns = (limit?: number) => {
  return useQuery(['crawlRuns', limit], () => apiService.getCrawlRuns(limit), {
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

export const useCrawlRun = (id: number) => {
  return useQuery(['crawlRun', id], () => apiService.getCrawlRun(id), {
    enabled: !!id,
  });
};

export const useRunResults = (runId: number, params?: { skip?: number; limit?: number }) => {
  return useQuery(['runResults', runId, params], () => apiService.getRunResults(runId, params), {
    enabled: !!runId,
  });
};

export const useTriggerFullCrawl = () => {
  const queryClient = useQueryClient();
  
  return useMutation(() => apiService.triggerFullCrawl(), {
    onSuccess: () => {
      queryClient.invalidateQueries(['crawlRuns']);
      queryClient.invalidateQueries(['results']);
      toast.success('전체 크롤링 작업이 시작되었습니다.');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '크롤링 시작에 실패했습니다.';
      toast.error(message);
    },
  });
};

// Dashboard hooks
export const useDashboardStats = () => {
  return useQuery(['dashboardStats'], () => apiService.getDashboardStats(), {
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export const useRecentActivity = (limit?: number) => {
  return useQuery(['recentActivity', limit], () => apiService.getRecentActivity(limit), {
    refetchInterval: 10000, // Refetch every 10 seconds
  });
};

// Crawling hooks
export const useTriggerCrawl = () => {
  const queryClient = useQueryClient();
  
  return useMutation((data: { keyword_id?: number; blog_id?: number; target_id?: number }) => apiService.triggerCrawl(data), {
    onSuccess: (data) => {
      queryClient.invalidateQueries(['crawlRuns']);
      queryClient.invalidateQueries(['recentActivity']);
      toast.success(data.message);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || '크롤링 시작에 실패했습니다.';
      toast.error(message);
    },
  });
};

export const useCrawlResults = (params?: { keyword_id?: number; blog_id?: number; limit?: number }) => {
  return useQuery(['crawlResults', params], () => apiService.getCrawlResults(params), {
    refetchInterval: 10000, // Refetch every 10 seconds
  });
};
