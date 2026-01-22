import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface HotItem {
  title: string;
  description: string;
  cover?: string;
  duration?: number;
  author?: string;
  view_count: number;
  pub_date: string;
  url: string;
  source: string;
  is_video: boolean;
  event_type?: string;
}

interface VideoSectionProps {
  majorName: string;
}

const VIDEO_SERVICE_URL = 'http://localhost:8007';

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatViewCount = (count: number): string => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`;
  }
  return count.toString();
};

const getEventTypeIcon = (type: string): string => {
  const icons: Record<string, string> = {
    "技术突破": "🚀",
    "行业动态": "📈",
    "政策变化": "📋",
    "重要会议": "🎤",
    "社会事件": "🔥",
    "视频内容": "🎬",
    "新闻资讯": "📰"
  };
  return icons[type] || "📌";
};

const getEventTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    "技术突破": "from-blue-50 to-indigo-50 border-blue-200",
    "行业动态": "from-green-50 to-emerald-50 border-green-200",
    "政策变化": "from-purple-50 to-violet-50 border-purple-200",
    "重要会议": "from-orange-50 to-amber-50 border-orange-200",
    "社会事件": "from-red-50 to-rose-50 border-red-200",
    "视频内容": "from-pink-50 to-rose-50 border-pink-200",
    "新闻资讯": "from-cyan-50 to-sky-50 border-cyan-200"
  };
  return colors[type] || "from-gray-50 to-gray-100 border-gray-200";
};

const VideoSection: React.FC<VideoSectionProps> = ({ majorName }) => {
  const [introVideo, setIntroVideo] = useState<HotItem | null>(null);
  const [hotEvents, setHotEvents] = useState<HotItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);

  // 阻止滚轮事件冒泡
  const handleWheel = (e: React.WheelEvent) => {
    if (isPaused) {
      e.preventDefault();
      e.stopPropagation();
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${VIDEO_SERVICE_URL}/api/v1/video/professional-with-events/${encodeURIComponent(majorName)}`);
        
        if (!response.ok) {
          throw new Error('获取数据失败');
        }
        
        const data = await response.json();
        setIntroVideo(data.hot_video);
        setHotEvents(data.hot_events || []);
      } catch (err) {
        console.error('获取数据失败:', err);
        setError('数据加载失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [majorName]);

  // 自动滚动热点事件（垂直无缝滚动）
  useEffect(() => {
    if (hotEvents.length <= 3 || !scrollRef.current || isPaused) {
      return;
    }

    const scrollContainer = scrollRef.current;
    
    // 清除之前的动画
    scrollContainer.style.animation = 'none';
    
    // 计算总高度：每个item约85px + 12px间距
    const itemHeight = 85;
    const gap = 12;
    const singleItemHeight = itemHeight + gap;
    const totalHeight = hotEvents.length * singleItemHeight;
    
    // 计算滚动时间：总高度 / 速度
    const scrollDuration = totalHeight / 30; // 速度调整为每秒30px
    
    // 使用CSS动画实现无缝滚动
    scrollContainer.style.animation = `scrollUp ${scrollDuration}s linear infinite`;
    
    return () => {
      scrollContainer.style.animation = 'none';
    };
  }, [hotEvents.length, isPaused]);

  if (loading) {
    return (
      <div className="mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-200 dark:bg-gray-700 rounded-xl h-80"></div>
          <div className="bg-gray-200 dark:bg-gray-700 rounded-xl h-80"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">加载失败</p>
      </div>
    );
  }

  // 固定高度（刚好显示3条热点）
  const MODULE_HEIGHT = "320px";

  return (
    <div className="mt-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 模块一：视频讲解模块 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 shadow-sm flex flex-col"
          style={{ height: MODULE_HEIGHT }}
        >
          {/* 标题 */}
          <div className="flex-shrink-0 flex items-center gap-2 px-5 py-4 border-b border-gray-100 dark:border-gray-700">
            <span className="text-lg">🎬</span>
            <h3 className="font-semibold text-gray-900 dark:text-white">视频讲解</h3>
            <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
              专业解读
            </span>
          </div>
          
          {/* 视频内容 */}
          {introVideo ? (
            <div className="flex-1 flex flex-col p-5 overflow-hidden">
              <div 
                className="relative cursor-pointer group flex-shrink-0 rounded-lg overflow-hidden"
                onClick={() => introVideo.is_video && setShowPlayer(true)}
              >
                {introVideo.cover ? (
                  <img
                    src={introVideo.cover}
                    alt={introVideo.title}
                    className="w-full h-32 object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = 'https://via.placeholder.com/640x360?text=Video';
                    }}
                  />
                ) : (
                  <div className="w-full h-32 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900/30 dark:to-purple-900/30 flex items-center justify-center">
                    <span className="text-4xl">🎬</span>
                  </div>
                )}
                
                {/* 遮罩 */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"></div>
                
                {/* 播放按钮 */}
                {introVideo.is_video && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/10 opacity-0 group-hover:opacity-100 transition-all duration-300">
                    <motion.div 
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                      className="w-12 h-12 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg"
                    >
                      <svg className="w-6 h-6 text-gray-700 ml-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </motion.div>
                  </div>
                )}
                
                {/* 时长 */}
                {introVideo.is_video && introVideo.duration && (
                  <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-sm text-white text-xs px-2 py-1 rounded font-medium">
                    {formatDuration(introVideo.duration)}
                  </div>
                )}
                
                {/* 平台标签 */}
                <div className="absolute top-2 left-2 bg-pink-500 text-white text-xs px-2 py-1 rounded-md font-medium flex items-center gap-1">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.813 4.653h2.334c.63 0 1.143.513 1.143 1.143v12.375c0 .63-.513 1.143-1.143 1.143H4.653c-.63 0-1.143-.513-1.143-1.143V5.796c0-.63.513-1.143 1.143-1.143h2.334c.315 0 .62.13.843.358l4.394 4.415c.228.228.538.358.843.358h.002c.305 0 .615-.13.843-.358l4.394-4.415c.223-.228.528-.358.843-.358z"/>
                  </svg>
                  {introVideo.source}
                </div>
              </div>
              
              {/* 视频信息 */}
              <div className="flex-1 flex flex-col justify-between mt-3 overflow-hidden">
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white text-sm leading-snug line-clamp-2 mb-2">
                    {introVideo.title}
                  </h4>
                  
                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
                      </svg>
                      {formatViewCount(introVideo.view_count)}
                    </span>
                    {introVideo.author && <span className="text-gray-400">{introVideo.author}</span>}
                  </div>
                </div>
                
                <a
                  href={introVideo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 inline-flex items-center gap-1 text-xs text-pink-500 hover:text-pink-600 font-medium mt-2"
                >
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                  查看完整视频
                </a>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <span className="text-3xl mb-2 block">🎬</span>
            </div>
          )}
        </motion.div>

        {/* 模块二：热点资讯模块 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 shadow-sm flex flex-col"
          style={{ height: MODULE_HEIGHT }}
        >
          {/* 标题 */}
          <div className="flex-shrink-0 flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-lg">🔥</span>
              <h3 className="font-semibold text-gray-900 dark:text-white">热点资讯</h3>
              <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                {hotEvents.length}条
              </span>
            </div>
          </div>
          
          {/* 热点列表 - 固定高度，超出滚动 */}
          <div 
            ref={scrollRef}
            className={`flex-1 p-4 ${isPaused ? 'overflow-hidden' : 'overflow-hidden'}`}
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
            onWheel={(e) => {
              if (isPaused) {
                e.preventDefault();
                e.stopPropagation();
              }
            }}
          >
            <div className={`scroll-content ${isPaused ? 'paused' : ''}`}>
              {hotEvents.length > 0 ? (
                hotEvents.map((event, index) => (
                  <motion.a
                    key={`first-${index}`}
                    href={event.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer hover:shadow-md transition-all duration-300 group block mb-3 bg-gradient-to-r ${getEventTypeColor(event.event_type || '新闻资讯')} dark:from-gray-800 dark:to-gray-700 dark:border-gray-600`}
                  >
                    {/* 图标 */}
                    <div className="flex-shrink-0 w-10 h-10 bg-white rounded-lg flex items-center justify-center text-xl shadow-sm dark:bg-gray-700">
                      {event.is_video ? '🎬' : getEventTypeIcon(event.event_type || '新闻资讯')}
                    </div>
                    
                    {/* 内容 */}
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-gray-900 dark:text-white text-sm mb-1.5 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {event.title}
                      </h5>
                      <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                          </svg>
                          {event.source}
                        </span>
                        <span>•</span>
                        <span>{event.pub_date}</span>
                        {event.view_count > 0 && (
                          <>
                            <span>•</span>
                            <span>{formatViewCount(event.view_count)}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* 箭头 */}
                    <div className="flex-shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                      </svg>
                    </div>
                  </motion.a>
                ))
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <span className="text-4xl mb-2 block">📰</span>
                    <p className="text-sm text-gray-500 dark:text-gray-400">暂无热点资讯</p>
                  </div>
                </div>
              )}
              
              {/* 复制一份热点事件，实现无缝滚动 */}
              {hotEvents.length > 0 && hotEvents.map((event, index) => (
                <motion.a
                  key={`second-${index}`}
                  href={event.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer hover:shadow-md transition-all duration-300 group block mb-3 bg-gradient-to-r ${getEventTypeColor(event.event_type || '新闻资讯')} dark:from-gray-800 dark:to-gray-700 dark:border-gray-600`}
                >
                  <div className="flex-shrink-0 w-10 h-10 bg-white rounded-lg flex items-center justify-center text-xl shadow-sm dark:bg-gray-700">
                    {event.is_video ? '🎬' : getEventTypeIcon(event.event_type || '新闻资讯')}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h5 className="font-medium text-gray-900 dark:text-white text-sm mb-1.5 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                      {event.title}
                    </h5>
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                        {event.source}
                      </span>
                      <span>•</span>
                      <span>{event.pub_date}</span>
                      {event.view_count > 0 && (
                        <>
                          <span>•</span>
                          <span>{formatViewCount(event.view_count)}</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                    </svg>
                  </div>
                </motion.a>
              ))}
            </div>
          </div>
          
          {/* 底部来源 */}
          <div className="flex-shrink-0 p-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
            <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
              数据来源：B站、微博、今日头条、腾讯新闻 • 点击查看原文
            </p>
          </div>
        </motion.div>
      </div>

      {/* CSS动画样式 */}
      <style>{`
        .scroll-content {
          display: flex;
          flex-direction: column;
          animation: scrollUp 60s linear infinite;
        }
        
        .scroll-content.paused {
          animation-play-state: paused;
        }
        
        @keyframes scrollUp {
          0% {
            transform: translateY(0);
          }
          100% {
            transform: translateY(-50%);
          }
        }
      `}</style>

      {/* 视频播放弹窗 */}
      {showPlayer && introVideo && introVideo.is_video && (
        <div 
          className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
          onClick={() => setShowPlayer(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="relative w-full max-w-5xl bg-black rounded-lg overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative" style={{ paddingTop: '56.25%' }}>
              <iframe
                src={`//player.bilibili.com/player.html?bvid=${introVideo.url.split('/').pop()}&page=1&high_quality=1&danmaku=0`}
                className="absolute inset-0 w-full h-full"
                allowFullScreen
                scrolling="no"
              />
            </div>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowPlayer(false)}
              className="absolute top-3 right-3 w-10 h-10 bg-black/50 hover:bg-black/70 backdrop-blur-sm rounded-full flex items-center justify-center text-white"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
            
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 pt-12">
              <h4 className="text-white font-medium">{introVideo.title}</h4>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default VideoSection;
