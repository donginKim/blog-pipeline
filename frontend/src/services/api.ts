import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  User,
  UserCreate,
  UserUpdate,
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
  LoginRequest,
  LoginResponse,
  GeneratedPost,
} from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // API URL 설정
    // 항상 상대 경로 사용 (Nginx가 /api를 backend:8001로 프록시)
    const apiUrl = import.meta.env.VITE_API_URL;
    
    this.api = axios.create({
      // VITE_API_URL이 명시적으로 설정되지 않은 경우 상대 경로 사용
      baseURL: apiUrl || '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login', credentials);
    return response.data;
  }

  async register(userData: UserCreate): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  async updateUser(userData: UserUpdate): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put('/auth/me', userData);
    return response.data;
  }

  // Keyword endpoints
  async getKeywords(params?: { skip?: number; limit?: number; is_active?: boolean }): Promise<Keyword[]> {
    const response: AxiosResponse<Keyword[]> = await this.api.get('/keywords', { params });
    return response.data;
  }

  async createKeyword(data: KeywordCreate): Promise<Keyword> {
    const response: AxiosResponse<Keyword> = await this.api.post('/keywords', data);
    return response.data;
  }

  async updateKeyword(id: number, data: KeywordUpdate): Promise<Keyword> {
    const response: AxiosResponse<Keyword> = await this.api.put(`/keywords/${id}`, data);
    return response.data;
  }

  async deleteKeyword(id: number): Promise<void> {
    await this.api.delete(`/keywords/${id}`);
  }

  async uploadKeywordsExcel(file: File): Promise<{ message: string; success_count: number; error_count: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.api.post('/keywords/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Blog endpoints
  async getBlogs(params?: { skip?: number; limit?: number; is_active?: boolean }): Promise<Blog[]> {
    const response: AxiosResponse<Blog[]> = await this.api.get('/blogs', { params });
    return response.data;
  }

  async createBlog(data: BlogCreate): Promise<Blog> {
    const response: AxiosResponse<Blog> = await this.api.post('/blogs', data);
    return response.data;
  }

  async updateBlog(id: number, data: BlogUpdate): Promise<Blog> {
    const response: AxiosResponse<Blog> = await this.api.put(`/blogs/${id}`, data);
    return response.data;
  }

  async deleteBlog(id: number): Promise<void> {
    await this.api.delete(`/blogs/${id}`);
  }

  // Target endpoints
  async getTargets(params?: { skip?: number; limit?: number; keyword_id?: number; blog_id?: number; is_active?: boolean }): Promise<KeywordTarget[]> {
    const response: AxiosResponse<KeywordTarget[]> = await this.api.get('/targets', { params });
    return response.data;
  }

  async createTarget(data: KeywordTargetCreate): Promise<KeywordTarget> {
    const response: AxiosResponse<KeywordTarget> = await this.api.post('/targets', data);
    return response.data;
  }

  async updateTarget(id: number, data: KeywordTargetUpdate): Promise<KeywordTarget> {
    const response: AxiosResponse<KeywordTarget> = await this.api.put(`/targets/${id}`, data);
    return response.data;
  }

  async deleteTarget(id: number): Promise<void> {
    await this.api.delete(`/targets/${id}`);
  }

  // Crawling endpoints
  async triggerCrawl(data?: { keyword_id?: number; blog_id?: number; target_id?: number }): Promise<{ message: string; run_id?: number; run_ids?: number[] }> {
    const response = await this.api.post('/crawl/trigger', data || {});
    return response.data;
  }

  async getCrawlRuns(limit?: number): Promise<CrawlRun[]> {
    const response: AxiosResponse<CrawlRun[]> = await this.api.get('/crawl/runs', {
      params: { limit },
    });
    return response.data;
  }

  async getCrawlResults(params?: { keyword_id?: number; blog_id?: number; limit?: number }): Promise<CrawlResult[]> {
    const response: AxiosResponse<CrawlResult[]> = await this.api.get('/crawl/results', { params });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response: AxiosResponse<DashboardStats> = await this.api.get('/dashboard/stats');
    return response.data;
  }

  async getRecentActivity(limit?: number): Promise<RecentActivity[]> {
    const response: AxiosResponse<RecentActivity[]> = await this.api.get('/dashboard/recent-activity', {
      params: { limit },
    });
    return response.data;
  }

  // Settings endpoints
  async getNotificationSettings(): Promise<any> {
    const response = await this.api.get('/settings/notifications');
    return response.data;
  }

  async saveNotificationSettings(data: any): Promise<any> {
    const response = await this.api.post('/settings/notifications', data);
    return response.data;
  }

  async testNotification(): Promise<any> {
    const response = await this.api.post('/settings/notifications/test');
    return response.data;
  }

  async getScheduleSettings(): Promise<any> {
    const response = await this.api.get('/settings/schedule');
    return response.data;
  }

  async saveScheduleSettings(data: any): Promise<any> {
    const response = await this.api.post('/settings/schedule', data);
    return response.data;
  }

  async getAIBlogSettings(): Promise<any> {
    const response = await this.api.get('/settings/ai-blog');
    return response.data;
  }

  async saveAIBlogSettings(data: any): Promise<any> {
    const response = await this.api.post('/settings/ai-blog', data);
    return response.data;
  }

  // Generated Posts endpoints
  async getGeneratedPosts(params?: { skip?: number; limit?: number; status?: string }): Promise<GeneratedPost[]> {
    const response: AxiosResponse<GeneratedPost[]> = await this.api.get('/generated-posts', { params });
    return response.data;
  }

  async getGeneratedPost(id: number): Promise<GeneratedPost> {
    const response: AxiosResponse<GeneratedPost> = await this.api.get(`/generated-posts/${id}`);
    return response.data;
  }

  async preparePublishPost(id: number): Promise<{ message: string; dsl_file: string; html_file: string }> {
    const response = await this.api.post(`/generated-posts/${id}/prepare-publish`);
    return response.data;
  }

  async markPostPublished(id: number, data: { naver_post_id?: string; published_url?: string }): Promise<GeneratedPost> {
    const response: AxiosResponse<GeneratedPost> = await this.api.post(`/generated-posts/${id}/mark-published`, data);
    return response.data;
  }

  async deleteGeneratedPost(id: number): Promise<void> {
    await this.api.delete(`/generated-posts/${id}`);
  }
}

export const apiService = new ApiService();
