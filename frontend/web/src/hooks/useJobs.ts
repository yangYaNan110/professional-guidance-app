import { useState, useEffect, useCallback } from 'react';
import { jobApi, analyticsApi } from '../services/api';
import { Job, Recommendation, SalaryTrend } from '../types';

interface JobState {
  jobs: Job[];
  recommendations: Recommendation[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  salaryTrend: SalaryTrend | null;
  industryComparison: { labels: string[]; data: number[] } | null;
  skillDemand: { labels: string[]; data: number[] } | null;
  
  loadJobs: (params?: { industry?: string; location?: string; page?: number }) => Promise<void>;
  loadRecommendations: (userId: string, limit?: number) => Promise<void>;
  loadAnalytics: () => Promise<void>;
  setPage: (page: number) => void;
}

export function useJobs(): JobState {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [salaryTrend, setSalaryTrend] = useState<SalaryTrend | null>(null);
  const [industryComparison, setIndustryComparison] = useState<{ labels: string[]; data: number[] } | null>(null);
  const [skillDemand, setSkillDemand] = useState<{ labels: string[]; data: number[] } | null>(null);

  const loadJobs = useCallback(async (params?: { industry?: string; location?: string; page?: number }) => {
    setIsLoading(true);
    try {
      const response = await jobApi.getJobs({
        ...params,
        page: params?.page || page,
        page_size: pageSize,
      });
      // 假设返回的是分页响应
      setJobs(Array.isArray(response) ? response : (response as { items?: Job[] })?.items || []);
    } catch (error) {
      console.error('加载职位失败:', error);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize]);

  const loadRecommendations = useCallback(async (userId: string, limit?: number) => {
    try {
      const response = await jobApi.getRecommendations(userId, limit);
      const data = response as { recommendations?: Recommendation[] };
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('加载推荐失败:', error);
    }
  }, []);

  const loadAnalytics = useCallback(async () => {
    try {
      const [trendData, industryData, skillData] = await Promise.all([
        analyticsApi.getSalaryTrend(),
        analyticsApi.getIndustryComparison(),
        analyticsApi.getSkillDemand(),
      ]);

      setSalaryTrend(trendData as SalaryTrend);
      setIndustryComparison(industryData as { labels: string[]; data: number[] });
      setSkillDemand(skillData as { labels: string[]; data: number[] });
    } catch (error) {
      console.error('加载分析数据失败:', error);
    }
  }, []);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  return {
    jobs,
    recommendations,
    total,
    page,
    pageSize,
    isLoading,
    salaryTrend,
    industryComparison,
    skillDemand,
    loadJobs,
    loadRecommendations,
    loadAnalytics,
    setPage,
  };
}
