/**
 * 爬虫数据模块API调用
 * 日期: 2026-01-23
 */

import type {
  Major,
  MajorListResponse,
  MajorMarketData,
  MajorMarketDataListResponse,
  University,
  UniversityListResponse,
  AdmissionScore,
  AdmissionScoreListResponse,
  IndustryTrend,
  IndustryTrendListResponse,
  VideoContent,
  VideoContentListResponse,
  CrawlHistory,
  CrawlHistoryListResponse,
  CrawlQuota,
  CrawlQuotaListResponse,
  MajorQueryParams,
  MarketDataQueryParams,
  UniversityQueryParams,
  AdmissionScoreQueryParams,
  IndustryTrendQueryParams,
  VideoQueryParams,
  CrawlHistoryQueryParams
} from '../types/crawler';

// API基础地址
const API_BASE = 'http://localhost:8004';

// =====================================================
// 学科分类API
// =====================================================

export async function getCategories(parentId?: number): Promise<{ data: any[]; total: number }> {
  const params = new URLSearchParams();
  if (parentId !== undefined) {
    params.append('parent_id', parentId.toString());
  }
  const query = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/categories${query}`);
  if (!response.ok) {
    throw new Error('获取学科分类失败');
  }
  return response.json();
}

export async function getCategoryById(categoryId: number): Promise<any> {
  const response = await fetch(`${API_BASE}/api/v1/data/categories/${categoryId}`);
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error('获取学科分类详情失败');
  }
  return response.json();
}

// =====================================================
// 专业API
// =====================================================

export async function getMajors(params: MajorQueryParams = {}): Promise<MajorListResponse> {
  const queryParams = new URLSearchParams();
  if (params.category_id !== undefined) {
    queryParams.append('category_id', params.category_id.toString());
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/majors${query}`);
  if (!response.ok) {
    throw new Error('获取专业列表失败');
  }
  return response.json();
}

export async function getMajorById(majorId: number): Promise<Major | null> {
  const response = await fetch(`${API_BASE}/api/v1/data/majors/${majorId}`);
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error('获取专业详情失败');
  }
  return response.json();
}

// =====================================================
// 专业行情数据API
// =====================================================

export async function getMarketData(params: MarketDataQueryParams = {}): Promise<MajorMarketDataListResponse> {
  const queryParams = new URLSearchParams();
  if (params.category !== undefined) {
    queryParams.append('category', params.category);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/market-data${query}`);
  if (!response.ok) {
    throw new Error('获取专业行情数据失败');
  }
  return response.json();
}

// =====================================================
// 大学API
// =====================================================

export async function getUniversities(params: UniversityQueryParams = {}): Promise<UniversityListResponse> {
  const queryParams = new URLSearchParams();
  if (params.province !== undefined) {
    queryParams.append('province', params.province);
  }
  if (params.level !== undefined) {
    queryParams.append('level', params.level);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/universities${query}`);
  if (!response.ok) {
    throw new Error('获取大学列表失败');
  }
  return response.json();
}

export async function getUniversityById(universityId: number): Promise<University | null> {
  const response = await fetch(`${API_BASE}/api/v1/data/universities/${universityId}`);
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error('获取大学详情失败');
  }
  return response.json();
}

// =====================================================
// 录取分数API
// =====================================================

export async function getAdmissionScores(params: AdmissionScoreQueryParams = {}): Promise<AdmissionScoreListResponse> {
  const queryParams = new URLSearchParams();
  if (params.university_id !== undefined) {
    queryParams.append('university_id', params.university_id.toString());
  }
  if (params.major_id !== undefined) {
    queryParams.append('major_id', params.major_id.toString());
  }
  if (params.province !== undefined) {
    queryParams.append('province', params.province);
  }
  if (params.year !== undefined) {
    queryParams.append('year', params.year.toString());
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/admission-scores${query}`);
  if (!response.ok) {
    throw new Error('获取录取分数失败');
  }
  return response.json();
}

// =====================================================
// 行业趋势API
// =====================================================

export async function getIndustryTrends(params: IndustryTrendQueryParams = {}): Promise<IndustryTrendListResponse> {
  const queryParams = new URLSearchParams();
  if (params.industry_name !== undefined) {
    queryParams.append('industry_name', params.industry_name);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/industry-trends${query}`);
  if (!response.ok) {
    throw new Error('获取行业趋势失败');
  }
  return response.json();
}

// =====================================================
// 视频内容API
// =====================================================

export async function getVideos(params: VideoQueryParams = {}): Promise<VideoContentListResponse> {
  const queryParams = new URLSearchParams();
  if (params.platform !== undefined) {
    queryParams.append('platform', params.platform);
  }
  if (params.related_major !== undefined) {
    queryParams.append('related_major', params.related_major);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/videos${query}`);
  if (!response.ok) {
    throw new Error('获取视频内容失败');
  }
  return response.json();
}

// =====================================================
// 爬取历史API
// =====================================================

export async function getCrawlHistory(params: CrawlHistoryQueryParams = {}): Promise<CrawlHistoryListResponse> {
  const queryParams = new URLSearchParams();
  if (params.task_type !== undefined) {
    queryParams.append('task_type', params.task_type);
  }
  if (params.status !== undefined) {
    queryParams.append('status', params.status);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/crawl-history${query}`);
  if (!response.ok) {
    throw new Error('获取爬取历史失败');
  }
  return response.json();
}

// =====================================================
// 爬取配额API
// =====================================================

export async function getCrawlQuotas(): Promise<CrawlQuotaListResponse> {
  const response = await fetch(`${API_BASE}/api/v1/data/crawl-quotas`);
  if (!response.ok) {
    throw new Error('获取爬取配额失败');
  }
  return response.json();
}

// =====================================================
// 热点资讯API
// =====================================================

export async function getHotNews(params: HotNewsQueryParams = {}): Promise<HotNewsListResponse> {
  const queryParams = new URLSearchParams();
  if (params.category !== undefined) {
    queryParams.append('category', params.category);
  }
  if (params.related_major !== undefined) {
    queryParams.append('related_major', params.related_major);
  }
  if (params.source !== undefined) {
    queryParams.append('source', params.source);
  }
  if (params.page !== undefined) {
    queryParams.append('page', params.page.toString());
  }
  if (params.page_size !== undefined) {
    queryParams.append('page_size', params.page_size.toString());
  }
  if (params.order_by !== undefined) {
    queryParams.append('order_by', params.order_by);
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
  const response = await fetch(`${API_BASE}/api/v1/data/hot-news${query}`);
  if (!response.ok) {
    throw new Error('获取热点资讯失败');
  }
  return response.json();
}

export async function getHotNewsTrending(limit: number = 20): Promise<HotNewsListResponse> {
  const response = await fetch(`${API_BASE}/api/v1/data/hot-news/trending?limit=${limit}`);
  if (!response.ok) {
    throw new Error('获取热门资讯失败');
  }
  return response.json();
}

export async function getHotNewsRecent(hours: number = 24, limit: number = 20): Promise<HotNewsListResponse> {
  const response = await fetch(`${API_BASE}/api/v1/data/hot-news/recent?hours=${hours}&limit=${limit}`);
  if (!response.ok) {
    throw new Error('获取最近资讯失败');
  }
  return response.json();
}

export async function getHotNewsByMajor(major: string, limit: number = 10): Promise<HotNewsListResponse> {
  const response = await fetch(`${API_BASE}/api/v1/data/hot-news/by-major/${encodeURIComponent(major)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('获取专业资讯失败');
  }
  return response.json();
}

export async function getHotNewsByCategory(category: string, limit: number = 10): Promise<HotNewsListResponse> {
  const response = await fetch(`${API_BASE}/api/v1/data/hot-news/by-category/${encodeURIComponent(category)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('获取分类资讯失败');
  }
  return response.json();
}
