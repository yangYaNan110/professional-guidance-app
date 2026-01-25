import React, { useState, useEffect } from 'react';
import './MajorDetail.css';

/**
 * 专业详情组件
 * 展示专业的完整信息
 */
const MajorDetail = ({ majorId, onBack }) => {
  const [major, setMajor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMajorDetail();
  }, [majorId]);

  const fetchMajorDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8004/api/v1/majors/${majorId}`);
      const data = await response.json();

      if (data.success) {
        setMajor(data.data);
      } else {
        setError('获取专业详情失败');
      }
    } catch (err) {
      setError('网络错误');
      console.error('获取专业详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderLoadingState = () => (
    <div className="major-detail loading">
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载专业详情中...</p>
      </div>
    </div>
  );

  const renderErrorState = () => (
    <div className="major-detail error">
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{error}</p>
        <div className="error-actions">
          <button onClick={fetchMajorDetail} className="retry-btn">
            重试
          </button>
          <button onClick={onBack} className="back-btn">
            返回列表
          </button>
        </div>
      </div>
    </div>
  );

  const renderMajorInfo = () => {
    if (!major) return null;

    return (
      <div className="major-detail">
        {/* 顶部导航 */}
        <div className="detail-header">
          <button onClick={onBack} className="back-btn">
            ← 返回专业列表
          </button>
          <div className="header-actions">
            <button className="favorite-btn">
              <span className="heart-icon">🤍</span>
              收藏专业
            </button>
            <a 
              href={major.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="source-link"
            >
              查看官方信息
            </a>
          </div>
        </div>

        {/* 专业基本信息 */}
        <section className="major-basic-info">
          <div className="major-title">
            <h1>{major.name}</h1>
            <div className="major-meta">
              <span className="major-code">{major.code}</span>
              {major.national_key_major && (
                <span className="national-badge">国家重点专业</span>
              )}
              <span className="category-badge">{major.category_name}</span>
            </div>
          </div>

          <div className="basic-stats">
            <div className="stat-item">
              <label>学制年限</label>
              <span>{major.study_period}年</span>
            </div>
            <div className="stat-item">
              <label>授予学位</label>
              <span>{major.degree_awarded}</span>
            </div>
            <div className="stat-item">
              <label>学科等级</label>
              <span>{major.discipline_level}</span>
            </div>
          </div>
        </section>

        {/* 专业介绍 */}
        <section className="major-description">
          <h2>专业介绍</h2>
          <div className="description-content">
            {major.description ? (
              <p>{major.description}</p>
            ) : (
              <p className="no-content">暂无专业介绍</p>
            )}
          </div>
        </section>

        {/* 培养目标 */}
        <section className="major-objective">
          <h2>培养目标</h2>
          <div className="objective-content">
            {major.training_objective ? (
              <p>{major.training_objective}</p>
            ) : (
              <p className="no-content">暂无培养目标信息</p>
            )}
          </div>
        </section>

        {/* 主干课程 */}
        <section className="major-courses">
          <h2>主干课程</h2>
          <div className="courses-content">
            {major.main_courses && major.main_courses.length > 0 ? (
              <div className="courses-grid">
                {major.main_courses.map((course, index) => (
                  <div key={index} className="course-item">
                    {course}
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-content">暂无课程信息</p>
            )}
          </div>
        </section>

        {/* 就业方向 */}
        <section className="major-employment">
          <h2>就业方向</h2>
          <div className="employment-content">
            {major.employment_direction ? (
              <div className="employment-tags">
                {major.employment_direction.split('、').map((direction, index) => (
                  <span key={index} className="employment-tag">
                    {direction.trim()}
                  </span>
                ))}
              </div>
            ) : (
              <p className="no-content">暂无就业方向信息</p>
            )}
          </div>
        </section>

        {/* 数据来源信息 */}
        <section className="source-info">
          <h3>数据来源</h3>
          <div className="source-details">
            <p>
              <strong>来源网站:</strong> {major.source_website}
            </p>
            <p>
              <strong>最后更新:</strong> {new Date(major.updated_at).toLocaleString()}
            </p>
            {major.source_url && (
              <a 
                href={major.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="original-source-link"
              >
                查看原始数据 →
              </a>
            )}
          </div>
        </section>
      </div>
    );
  };

  if (loading) {
    return renderLoadingState();
  }

  if (error) {
    return renderErrorState();
  }

  return renderMajorInfo();
};

export default MajorDetail;