import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  skills: string[];
  industry: string;
  matchScore: number;
}

const JobsPage: React.FC = () => {
  const [jobs] = useState<Job[]>([
    {
      id: '1',
      title: '高级Python开发工程师',
      company: '某科技公司',
      location: '北京',
      salary: '20K-35K/月',
      skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
      industry: '互联网',
      matchScore: 95
    },
    {
      id: '2',
      title: 'AI算法工程师',
      company: 'AI实验室',
      location: '上海',
      salary: '25K-40K/月',
      skills: ['Python', 'TensorFlow', 'NLP', 'PyTorch'],
      industry: '人工智能',
      matchScore: 88
    },
    {
      id: '3',
      title: '全栈开发工程师',
      company: '创业公司',
      location: '深圳',
      salary: '18K-30K/月',
      skills: ['React', 'Node.js', 'MongoDB', 'TypeScript'],
      industry: '互联网',
      matchScore: 82
    },
    {
      id: '4',
      title: '数据工程师',
      company: '大数据公司',
      location: '杭州',
      salary: '22K-35K/月',
      skills: ['Python', 'Spark', 'Hive', 'Kafka'],
      industry: '大数据',
      matchScore: 79
    }
  ]);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">📋 职位推荐</h1>
        <div className="flex space-x-4">
          <select className="input w-40">
            <option>全部行业</option>
            <option>互联网</option>
            <option>人工智能</option>
            <option>金融</option>
          </select>
          <select className="input w-40">
            <option>最新发布</option>
            <option>薪资高到低</option>
            <option>匹配度</option>
          </select>
        </div>
      </div>

      <div className="grid gap-4">
        {jobs.map((job, index) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-xl font-semibold">{job.title}</h3>
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                    匹配度 {job.matchScore}%
                  </span>
                </div>
                <p className="text-gray-600 mb-2">{job.company} · {job.location}</p>
                <p className="text-primary-600 font-medium mb-3">{job.salary}</p>
                <div className="flex flex-wrap gap-2">
                  {job.skills.map(skill => (
                    <span
                      key={skill}
                      className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div className="ml-4">
                <button className="btn-primary">查看详情</button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <button className="btn-secondary">加载更多职位</button>
      </div>
    </div>
  );
};

export default JobsPage;
