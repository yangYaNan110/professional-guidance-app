// 大学推荐相关类型定义
export interface TierScoreData {
  tier_name: string;
  years: {
    year: number;
    min_score?: number;
    max_score?: number;
    avg_score?: number;
    admission_type?: string;
  }[];
}

export interface University {
  id: number;
  name: string;
  province: string;
  city?: string;
  level?: string;
  employment_rate?: number;
  website?: string;
  match_score?: number;
  match_reason?: string;
  tier_scores?: Record<string, TierScoreData>;
  available_tiers?: string[];
}

export interface UniversityGroup {
  type: string; // score_match, province_match, national_match
  name: string;
  count: number;
  description: string;
  universities: University[];
}

export interface RecommendationRequest {
  major: string;
  province?: string;
  score?: number;
  limit?: number;
}

export interface RecommendationResponse {
  success: boolean;
  scenario: string; // A, B, C
  total: number;
  groups: Record<string, UniversityGroup>;
}

export interface SearchFormData {
  major: string;
  province: string;
  score: string;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}