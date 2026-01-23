/**
 * 爬虫数据模块类型定义
 * 日期: 2026-01-23
 */

// =====================================================
// 枚举类型
// =====================================================

export enum UniversityLevel {
  C985 = "985",
  C211 = "211",
  DOUBLE_FIRST_CLASS = "双一流",
  PROVINCIAL_KEY = "省属重点",
  ORDINARY = "普通"
}

export enum UniversityType {
  COMPREHENSIVE = "综合",
  SCIENCE_ENGINEERING = "理工",
  NORMAL = "师范",
  MEDICAL = "医药",
  AGRICULTURE = "农林",
  FINANCE = "财经",
  LAW = "政法",
  LANGUAGE = "语言",
  ART = "艺术",
  SPORTS = "体育",
  ETHNIC = "民族"
}

export enum AdmissionBatch {
  FIRST_BATCH = "本科一批",
  SECOND_BATCH = "本科二批",
  ADVANCE_BATCH = "本科提前批",
  SPECIAL_BATCH = "专科批"
}

export enum CrawlStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  PARTIALLY_COMPLETED = "partially_completed"
}

export enum CrawlTaskType {
  MAJOR = "major",
  UNIVERSITY = "university",
  VIDEO = "video",
  TREND = "trend"
}

export enum VideoPlatform {
  BILIBILI = "B站",
  YOUTUBE = "YouTube"
}

// =====================================================
// 接口定义
// =====================================================

export interface MajorCategory {
  id: number;
  code: string;
  name: string;
  parent_id: number | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Major {
  id: number;
  name: string;
  category_id: number;
  category_name: string | null;
  description: string | null;
  core_courses: string[];
  employment_rate: number | null;
  avg_salary: string | null;
  heat_index: number | null;
  created_at: string;
  updated_at: string;
}

export interface MajorMarketData {
  id: number;
  title: string;
  major_name: string | null;
  category: string | null;
  source_url: string | null;
  source_website: string | null;
  employment_rate: number | null;
  avg_salary: string | null;
  admission_score: number | null;
  heat_index: number | null;
  trend_data: Record<string, unknown> | null;
  description: string | null;
  courses: string[];
  career_prospects: string | null;
  crawled_at: string;
  updated_at: string;
  created_at: string;
}

export interface University {
  id: number;
  name: string;
  level: UniversityLevel | null;
  province: string;
  city: string | null;
  employment_rate: number | null;
  type: UniversityType | null;
  location: string | null;
  founded_year: number | null;
  website: string | null;
  major_strengths: string[];
  created_at: string;
  updated_at: string;
}

export interface AdmissionScore {
  id: number;
  university_id: number;
  university_name: string | null;
  major_id: number | null;
  major_name: string | null;
  year: number;
  min_score: number;
  max_score: number | null;
  avg_score: number | null;
  province: string;
  batch: AdmissionBatch | null;
  enrollment_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface IndustryTrend {
  id: number;
  industry_name: string;
  trend_data: Record<string, unknown>;
  policy_change: string | null;
  salary_change: string | null;
  source: string | null;
  source_url: string | null;
  publish_time: string | null;
  heat_index: number | null;
  crawled_at: string;
  created_at: string;
  updated_at: string;
}

export interface VideoContent {
  id: number;
  title: string;
  description: string | null;
  url: string;
  cover_url: string | null;
  duration: number | null;
  view_count: number;
  author: string | null;
  publish_time: string | null;
  platform: VideoPlatform;
  related_major: string | null;
  keywords: string[];
  heat_index: number | null;
  crawled_at: string;
  created_at: string;
  updated_at: string;
}

export interface CrawlHistory {
  id: number;
  task_id: string;
  task_type: CrawlTaskType;
  start_time: string | null;
  end_time: string | null;
  status: CrawlStatus;
  crawled_count: number;
  success_count: number;
  failed_count: number;
  error_message: string | null;
  created_at: string;
}

export interface CrawlQuota {
  id: number;
  category: string;
  quota: number;
  priority: number;
  used_count: number;
  last_reset_time: string | null;
  updated_at: string;
}

// =====================================================
// 响应类型
// =====================================================

export interface MajorListResponse {
  data: Major[];
  total: number;
  page: number;
  page_size: number;
}

export interface MajorMarketDataListResponse {
  data: MajorMarketData[];
  total: number;
  page: number;
  page_size: number;
}

export interface UniversityListResponse {
  data: University[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdmissionScoreListResponse {
  data: AdmissionScore[];
  total: number;
  page: number;
  page_size: number;
}

export interface IndustryTrendListResponse {
  data: IndustryTrend[];
  total: number;
  page: number;
  page_size: number;
}

export interface VideoContentListResponse {
  data: VideoContent[];
  total: number;
  page: number;
  page_size: number;
}

export interface CrawlHistoryListResponse {
  data: CrawlHistory[];
  total: number;
  page: number;
  page_size: number;
}

export interface CrawlQuotaListResponse {
  data: CrawlQuota[];
  total: number;
}

// =====================================================
// 查询参数类型
// =====================================================

export interface MajorQueryParams {
  category_id?: number;
  page?: number;
  page_size?: number;
}

export interface MarketDataQueryParams {
  category?: string;
  page?: number;
  page_size?: number;
}

export interface UniversityQueryParams {
  province?: string;
  level?: string;
  page?: number;
  page_size?: number;
}

export interface AdmissionScoreQueryParams {
  university_id?: number;
  major_id?: number;
  province?: string;
  year?: number;
  page?: number;
  page_size?: number;
}

export interface IndustryTrendQueryParams {
  industry_name?: string;
  page?: number;
  page_size?: number;
}

export interface VideoQueryParams {
  platform?: string;
  related_major?: string;
  page?: number;
  page_size?: number;
}

export interface CrawlHistoryQueryParams {
  task_type?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

// =====================================================
// 热点资讯类型
// =====================================================

export interface HotNews {
  id: number;
  title: string;
  summary?: string;
  source: string;
  source_url?: string;
  publish_time?: string;
  related_major?: string;
  category?: string;
  view_count: number;
  heat_index: number;
  crawled_at: string;
  created_at: string;
  updated_at?: string;
}

export interface HotNewsListResponse {
  data: HotNews[];
  total: number;
  page: number;
  page_size: number;
}

export interface HotNewsQueryParams {
  category?: string;
  related_major?: string;
  source?: string;
  page?: number;
  page_size?: number;
  order_by?: 'heat_index' | 'publish_time';
}
