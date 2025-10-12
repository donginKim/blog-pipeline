// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// User types
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  password?: string;
}

// Keyword types
export interface Keyword {
  id: number;
  keyword: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KeywordCreate {
  keyword: string;
  description?: string;
}

export interface KeywordUpdate {
  keyword?: string;
  description?: string;
  is_active?: boolean;
}

// Blog types
export interface Blog {
  id: number;
  name: string;
  url_pattern: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlogCreate {
  name: string;
  url_pattern: string;
  description?: string;
}

export interface BlogUpdate {
  name?: string;
  url_pattern?: string;
  description?: string;
  is_active?: boolean;
}

// Target types
export interface KeywordTarget {
  id: number;
  keyword_id: number;
  blog_id: number;
  keyword?: string;
  blog_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KeywordTargetCreate {
  keyword_id: number;
  blog_id: number;
}

export interface KeywordTargetUpdate {
  is_active?: boolean;
}

// Crawl Run types
export interface CrawlRun {
  id: number;
  keyword?: string;
  blog_name?: string;
  started_at: string;
  finished_at?: string;
  completed_at?: string;
  created_at?: string;
  status: 'running' | 'completed' | 'failed' | 'success' | 'error';
  total_keywords: number;
  success_count: number;
  fail_count: number;
  error_message?: string;
}

// Crawl Result types
export interface CrawlResult {
  id: number;
  crawl_run_id: number;
  keyword: string;
  blog_name: string;
  rank: number;
  title: string;
  url: string;
  snippet: string;
  section?: string;
  created_at: string;
}

export interface ResultFilter {
  keyword_id?: number;
  blog_id?: number;
  found?: boolean;
  run_date_from?: string;
  run_date_to?: string;
  limit?: number;
  offset?: number;
}

// Dashboard types
export interface DashboardStats {
  total_keywords: number;
  total_blogs: number;
  total_targets: number;
  active_targets?: number;
  total_results: number;
  recent_runs: CrawlRun[];
  recent_results: CrawlResult[];
}

export interface RecentActivity {
  type: string;
  id: number;
  keyword?: string;
  blog_name?: string;
  timestamp: string;
  created_at?: string;
  status?: string;
  total_keywords?: number;
  success_count?: number;
  fail_count?: number;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

// Chart data types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface PerformanceData {
  date: string;
  total_results: number;
  found_count: number;
  found_percentage: number;
  avg_occurrences: number;
}

// Form types
export interface FormErrors {
  [key: string]: string | undefined;
}

// API Error types
export interface ApiError {
  detail: string;
  status_code: number;
  message?: string;
}

// Generated Post types
export interface GeneratedPost {
  id: number;
  keyword_id: number;
  keyword?: string;
  target_id?: number;
  title: string;
  content: string;
  summary: string;
  tags: string[];
  status: 'draft' | 'ready' | 'published';
  naver_post_id?: string;
  published_url?: string;
  created_at: string;
  updated_at: string;
  published_at?: string;
}
