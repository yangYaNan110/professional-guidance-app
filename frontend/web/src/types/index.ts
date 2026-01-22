export interface User {
  id: string;
  email: string;
  nickname: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
}

export interface UserProfile {
  education?: string;
  major?: string;
  skills: string[];
  experience_years: number;
  expected_salary_min?: number;
  expected_salary_max?: number;
  preferred_locations: string[];
  preferred_industries: string[];
  career_goals?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  audio_url?: string;
  emotion?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_message?: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  salary_avg?: number;
  industry: string;
  skills: string[];
  source: string;
  crawled_at: string;
}

export interface Recommendation {
  job: Job;
  score: number;
  reason: string;
}

export interface SalaryTrend {
  labels: string[];
  data: number[];
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
  }[];
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
