import React from 'react';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  matchScore?: number;
  onViewDetail?: (job: Job) => void;
  onSave?: (job: Job) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  matchScore,
  onViewDetail,
  onSave,
}) => {
  const formatSalary = (min?: number, max?: number) => {
    if (min && max) {
      if (min === max) return `${(min / 1000).toFixed(0)}K/月`;
      return `${(min / 1000).toFixed(0)}K-${(max / 1000).toFixed(0)}K/月`;
    }
    if (min) return `${(min / 1000).toFixed(0)}K+/月`;
    if (max) return `~${(max / 1000).toFixed(0)}K/月`;
    return '面议';
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-xl font-semibold text-gray-900">
              {job.title}
            </h3>
            {matchScore !== undefined && (
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-medium">
                匹配度 {matchScore}%
              </span>
            )}
          </div>
          
          <p className="text-gray-600 mb-2">
            {job.company} · {job.location}
          </p>
          
          <p className="text-primary-600 font-medium mb-3">
            {formatSalary(job.salary_min, job.salary_max)}
          </p>
          
          <div className="flex flex-wrap gap-2 mb-3">
            {job.skills.slice(0, 5).map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 5 && (
              <span className="px-3 py-1 bg-gray-100 text-gray-500 rounded-full text-sm">
                +{job.skills.length - 5}
              </span>
            )}
          </div>
          
          <div className="flex items-center text-sm text-gray-500 space-x-4">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              {job.industry}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {new Date(job.crawled_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        
        <div className="ml-4 flex flex-col space-y-2">
          <button
            onClick={() => onViewDetail?.(job)}
            className="btn-primary text-sm"
          >
            查看详情
          </button>
          <button
            onClick={() => onSave?.(job)}
            className="btn-secondary text-sm"
          >
            收藏
          </button>
        </div>
      </div>
    </div>
  );
};

interface JobListProps {
  jobs: Job[];
  onViewDetail?: (job: Job) => void;
  onSave?: (job: Job) => void;
  loading?: boolean;
}

export const JobList: React.FC<JobListProps> = ({
  jobs,
  onViewDetail,
  onSave,
  loading,
}) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-3" />
              <div className="flex space-x-2">
                <div className="h-6 bg-gray-200 rounded w-20" />
                <div className="h-6 bg-gray-200 rounded w-20" />
                <div className="h-6 bg-gray-200 rounded w-20" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">
          没有找到相关职位
        </h3>
        <p className="text-gray-500">
          试试调整搜索条件或扩大搜索范围
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          onViewDetail={onViewDetail}
          onSave={onSave}
        />
      ))}
    </div>
  );
};
