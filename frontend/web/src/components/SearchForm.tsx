// 搜索表单组件
import React, { useState, useEffect } from 'react';
import { UniversityAPI } from '../services/universityAPI';

interface SearchFormData {
  major: string;
  province: string;
  score: string;
}

interface SearchFormProps {
  onSearch: (data: { major: string; province?: string; score?: number }) => void;
  initialData?: Partial<SearchFormData>;
}

const SearchForm: React.FC<SearchFormProps> = ({ 
  onSearch, 
  initialData = {} 
}) => {
  const [formData, setFormData] = useState<SearchFormData>({
    major: initialData.major || '',
    province: initialData.province || '',
    score: initialData.score || ''
  });

  const [majors, setMajors] = useState<string[]>([]);
  const [provinces, setProvinces] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // 加载热门专业和省份
  useEffect(() => {
    const loadData = async () => {
      try {
        const [majorsData, provincesData] = await Promise.all([
          UniversityAPI.getPopularMajors(),
          UniversityAPI.getProvinces()
        ]);
        setMajors(majorsData);
        setProvinces(provincesData);
      } catch (error) {
        console.error('加载选项数据失败:', error);
      }
    };
    
    loadData();
  }, []);

  const handleInputChange = (field: keyof SearchFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 验证必填字段
    if (!formData.major.trim()) {
      alert('请输入专业名称');
      return;
    }

    // 构建搜索参数
    const searchParams: { major: string; province?: string; score?: number } = {
      major: formData.major.trim()
    };

    if (formData.province) {
      searchParams.province = formData.province;
    }

    if (formData.score) {
      const scoreNum = parseInt(formData.score);
      if (isNaN(scoreNum) || scoreNum < 400 || scoreNum > 750) {
        alert('分数应在400-750之间');
        return;
      }
      searchParams.score = scoreNum;
    }

    onSearch(searchParams);
  };

  const handleReset = () => {
    setFormData({
      major: '',
      province: '',
      score: ''
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        🎯 智能大学推荐
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 专业选择 */}
        <div>
          <label htmlFor="major" className="block text-sm font-medium text-gray-700 mb-2">
            专业名称 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="text"
              id="major"
              list="majors"
              value={formData.major}
              onChange={(e) => handleInputChange('major', e.target.value)}
              placeholder="请输入专业名称，如：人工智能、计算机科学与技术"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400"
              required
            />
            <datalist id="majors">
              {majors.map(major => (
                <option key={major} value={major} />
              ))}
            </datalist>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 省份选择 */}
          <div>
            <label htmlFor="province" className="block text-sm font-medium text-gray-700 mb-2">
              目标省份
            </label>
            <select
              id="province"
              value={formData.province}
              onChange={(e) => handleInputChange('province', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            >
              <option value="">请选择省份</option>
              {provinces.map(province => (
                <option key={province} value={province}>{province}</option>
              ))}
            </select>
          </div>

          {/* 预估分数 */}
          <div>
            <label htmlFor="score" className="block text-sm font-medium text-gray-700 mb-2">
              预估分数
            </label>
            <input
              type="number"
              id="score"
              value={formData.score}
              onChange={(e) => handleInputChange('score', e.target.value)}
              placeholder="请输入预估分数，如：620"
              min={400}
              max={750}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400"
            />
            <p className="mt-1 text-xs text-gray-500">
              分数范围：400-750分
            </p>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? '推荐中...' : '获取推荐'}
          </button>
          
          <button
            type="button"
            onClick={handleReset}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
          >
            重置
          </button>
        </div>
      </form>

      {/* 使用提示 */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">💡 使用提示</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• <strong>场景A</strong>：填写专业+省份+分数，获取精确推荐</li>
          <li>• <strong>场景B</strong>：填写专业+省份，获取同省优质推荐</li>
          <li>• <strong>场景C</strong>：只填写专业，获取全国推荐</li>
          <li>• 信息越完整，推荐越精准</li>
        </ul>
      </div>
    </div>
  );
};

export default SearchForm;