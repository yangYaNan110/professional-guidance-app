import React, { useState, useEffect } from 'react';
import './MajorList.css';

/**
 * 专业列表组件
 * 展示专业卡片列表，支持分页和搜索
 */
const MajorList = ({ selectedCategory, searchKeyword, onMajorClick }) => {
  const [majors, setMajors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 12,
    total: 0,
    totalPages: 0
  });

  useEffect(() => {
    fetchMajors(1);
  }, [selectedCategory, searchKeyword]);

  const fetchMajors = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pagination.pageSize.toString(),
      });

      if (selectedCategory) {
        params.append('category_id', selectedCategory.toString());
      }

      if (searchKeyword) {
        params.append('keyword', searchKeyword);
      }

      const response = await fetch(`http://localhost:8004/api/v1/majors?${params}`);
      const data = await response.json();

      if (data.success) {
        setMajors(page === 1 ? data.data : [...majors, ...data.data]);
        setPagination(data.pagination);
      } else {
        setError('获取专业列表失败');
      }
    } catch (err) {
      setError('网络错误');
      console.error('获取专业列表失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (pagination.page < pagination.totalPages && !loading) {
      fetchMajors(pagination.page + 1);
    }
  };

  const handleMajorCardClick = (major) => {
    if (onMajorClick) {
      onMajorClick(major);
    }
  };

  const renderLoadingState = () => (
    <div className="major-list loading">
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载专业列表中...</p>
      </div>
    </div>
  );

  const renderErrorState = () => (
    <div className="major-list error">
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{error}</p>
        <button onClick={() => fetchMajors(1)} className="retry-btn">
          重试
        </button>
      </div>
    </div>
  );

  const renderEmptyState = () => (
    <div className="major-list empty">
      <div className="empty-container">
        <div className="empty-icon">📚</div>
        <h3>暂无专业数据</h3>
        <p>请尝试调整筛选条件或搜索关键词</p>
      </div>
    </div>
  );

  const renderMajorCard = (major) => (
    <div 
      key={major.id} 
      className="major-card"
      onClick={() => handleMajorCardClick(major)}
    >
      <div className="major-header">
        <h3 className="major-name">{major.name}</h3>
        <span className="major-code">{major.code}</span>
      </div>
      
      <div className="major-category">
        <span className="category-badge">{major.category_name}</span>
        {major.national_key_major && (
          <span className="national-badge">国家重点专业</span>
        )}
      </div>
      
      <div className="major-description">
        {major.description ? (
          <p>{major.description.length > 120 
            ? `${major.description.substring(0, 120)}...` 
            : major.description}
          </p>
        ) : (
          <p className="no-description">暂无专业介绍</p>
        )}
      </div>
      
      <div className="major-footer">
        <div className="study-info">
          <span className="period">学制{major.study_period}年</span>
          <span className="degree">{major.degree_awarded}</span>
        </div>
        <button className="detail-btn">查看详情</button>
      </div>
    </div>
  );

  if (loading && majors.length === 0) {
    return renderLoadingState();
  }

  if (error && majors.length === 0) {
    return renderErrorState();
  }

  if (!loading && majors.length === 0) {
    return renderEmptyState();
  }

  return (
    <div className="major-list">
      <div className="list-header">
        <h2>专业列表</h2>
        <span className="result-count">
          共找到 {pagination.total} 个专业
        </span>
      </div>

      <div className="majors-grid">
        {majors.map(renderMajorCard)}
      </div>

      {loading && majors.length > 0 && (
        <div className="loading-more">
          <div className="loading-spinner"></div>
          <span>加载更多...</span>
        </div>
      )}

      {!loading && pagination.page < pagination.totalPages && (
        <div className="load-more-container">
          <button 
            className="load-more-btn" 
            onClick={handleLoadMore}
          >
            加载更多 ({pagination.page}/{pagination.totalPages})
          </button>
        </div>
      )}
    </div>
  );
};

export default MajorList;