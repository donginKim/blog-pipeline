import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
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
  ResultFilter,
  DashboardStats,
  RecentActivity,
  LoginRequest,
  LoginResponse,
} from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // 환경 변수에서 API URL 가져오기 (없으면 localhost)
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    
    this.api = axios.create({
      baseURL: `${apiUrl}/api`,
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
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login', {
      username: credentials.username,
      password: credentials.password,
    });
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
    const response: AxiosResponse<Keyword[]> = await this.api.get('/keywords/', { params });
    return response.data;
  }

  async createKeyword(keywordData: KeywordCreate): Promise<Keyword> {
    const response: AxiosResponse<Keyword> = await this.api.post('/keywords/', keywordData);
    return response.data;
  }

  async getKeyword(id: number): Promise<Keyword> {
    const response: AxiosResponse<Keyword> = await this.api.get(`/keywords/${id}`);
    return response.data;
  }

  async updateKeyword(id: number, keywordData: KeywordUpdate): Promise<Keyword> {
    const response: AxiosResponse<Keyword> = await this.api.put(`/keywords/${id}`, keywordData);
    return response.data;
  }

  async deleteKeyword(id: number): Promise<void> {
    await this.api.delete(`/keywords/${id}`);
  }

  // Blog endpoints
  async getBlogs(params?: { skip?: number; limit?: number; is_active?: boolean }): Promise<Blog[]> {
    const response: AxiosResponse<Blog[]> = await this.api.get('/blogs/', { params });
    return response.data;
  }

  async createBlog(blogData: BlogCreate): Promise<Blog> {
    const response: AxiosResponse<Blog> = await this.api.post('/blogs/', blogData);
    return response.data;
  }

  async getBlog(id: number): Promise<Blog> {
    const response: AxiosResponse<Blog> = await this.api.get(`/blogs/${id}`);
    return response.data;
  }

  async updateBlog(id: number, blogData: BlogUpdate): Promise<Blog> {
    const response: AxiosResponse<Blog> = await this.api.put(`/blogs/${id}`, blogData);
    return response.data;
  }

  async deleteBlog(id: number): Promise<void> {
    await this.api.delete(`/blogs/${id}`);
  }

  // Target endpoints
  async getTargets(params?: {
    skip?: number;
    limit?: number;
    keyword_id?: number;
    blog_id?: number;
    is_active?: boolean;
  }): Promise<KeywordTarget[]> {
    const response: AxiosResponse<KeywordTarget[]> = await this.api.get('/targets/', { params });
    return response.data;
  }

  async createTarget(targetData: KeywordTargetCreate): Promise<KeywordTarget> {
    const response: AxiosResponse<KeywordTarget> = await this.api.post('/targets/', targetData);
    return response.data;
  }

  async getTarget(id: number): Promise<KeywordTarget> {
    const response: AxiosResponse<KeywordTarget> = await this.api.get(`/targets/${id}`);
    return response.data;
  }

  async updateTarget(id: number, targetData: KeywordTargetUpdate): Promise<KeywordTarget> {
    const response: AxiosResponse<KeywordTarget> = await this.api.put(`/targets/${id}`, targetData);
    return response.data;
  }

  async deleteTarget(id: number): Promise<void> {
    await this.api.delete(`/targets/${id}`);
  }

  async triggerCrawlForTarget(id: number): Promise<{ message: string; run_id?: number }> {
    const response: AxiosResponse<{ message: string; run_id?: number }> = await this.api.post('/crawl/trigger', {
      target_id: id
    });
    return response.data;
  }

  // Result endpoints
  async getResults(params?: {
    keyword_id?: number;
    blog_id?: number;
    found?: boolean;
    run_date_from?: string;
    run_date_to?: string;
    skip?: number;
    limit?: number;
  }): Promise<CrawlResult[]> {
    const response: AxiosResponse<CrawlResult[]> = await this.api.get('/results/', { params });
    return response.data;
  }

  async getResultStats(params?: {
    keyword_id?: number;
    blog_id?: number;
    run_date_from?: string;
    run_date_to?: string;
  }): Promise<{
    total_count: number;
    found_count: number;
    not_found_count: number;
    found_percentage: number;
    average_occurrences: number;
  }> {
    const response = await this.api.get('/results/stats', { params });
    return response.data;
  }

  async getCrawlRuns(params?: { skip?: number; limit?: number }): Promise<CrawlRun[]> {
    const response: AxiosResponse<CrawlRun[]> = await this.api.get('/results/runs', { params });
    return response.data;
  }

  async getCrawlRun(id: number): Promise<CrawlRun> {
    const response: AxiosResponse<CrawlRun> = await this.api.get(`/results/runs/${id}`);
    return response.data;
  }

  async getRunResults(runId: number, params?: { skip?: number; limit?: number }): Promise<CrawlResult[]> {
    const response: AxiosResponse<CrawlResult[]> = await this.api.get(`/results/runs/${runId}/results`, { params });
    return response.data;
  }

  async triggerFullCrawl(): Promise<{ message: string; task_id: string }> {
    const response = await this.api.post('/results/trigger-crawl');
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

  // Keywords endpoints
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
    
    const response: AxiosResponse<{ message: string; success_count: number; error_count: number; errors: string[] }> = await this.api.post('/keywords/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Crawling endpoints
  async triggerCrawl(data: { keyword_id?: number; blog_id?: number; target_id?: number }): Promise<{ message: string; run_id?: number; run_ids?: number[] }> {
    const response: AxiosResponse<{ message: string; run_id?: number; run_ids?: number[] }> = await this.api.post('/crawl/trigger', data);
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

  // Blogs endpoints
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

  // Targets endpoints
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
}

export const apiService = new ApiService();
