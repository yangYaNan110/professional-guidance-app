// 大学推荐相关类型定义
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