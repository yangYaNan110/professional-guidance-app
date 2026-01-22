import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface VideoItem {
  bvid: string;
  title: string;
  description: string;
  cover: string;
  duration: number;
  author: string;
  view_count: number;
  pubdate: number;
  url: string;
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

const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp * 1000);
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

const VideoSection: React.FC<VideoSectionProps> = ({ majorName }) => {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<VideoItem | null>(null);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${VIDEO_SERVICE_URL}/api/v1/video/professional/${encodeURIComponent(majorName)}`);
        
        if (!response.ok) {
          throw new Error('获取视频失败');
        }
        
        const data = await response.json();
        setVideos(data.videos || []);
      } catch (err) {
        console.error('获取视频失败:', err);
        setError('视频功能暂时不可用');
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [majorName]);

  if (loading) {
    return (
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span>🎬</span> 相关视频
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-40 mb-3"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">🎬 {error}</p>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">🎬 暂无相关视频</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <span>🎬</span> 相关视频
        <span className="text-sm font-normal text-gray-500 dark:text-gray-400">({videos.length}个视频)</span>
      </h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {videos.map((video, index) => (
          <motion.div
            key={video.bvid}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => setSelectedVideo(video)}
          >
            <div className="relative">
              <img
                src={video.cover}
                alt={video.title}
                className="w-full h-40 object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/320x180?text=Video';
                }}
              />
              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                {formatDuration(video.duration)}
              </div>
              <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black/30">
                <div className="w-12 h-12 bg-white/90 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-gray-800 ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="p-3">
              <h4 className="font-medium text-gray-900 dark:text-white text-sm line-clamp-2 mb-2">
                {video.title}
              </h4>
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
                  </svg>
                  {formatViewCount(video.view_count)}
                </span>
                <span>{video.author}</span>
                <span>{formatDate(video.pubdate)}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* 视频详情弹窗 */}
      {selectedVideo && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedVideo(null)}>
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden w-full max-w-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-white">视频详情</h3>
              <button
                onClick={() => setSelectedVideo(null)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-4">
              <div className="relative bg-black rounded-lg overflow-hidden mb-4" style={{ paddingTop: '56.25%' }}>
                <iframe
                  src={`//player.bilibili.com/player.html?bvid=${selectedVideo.bvid}&page=1&high_quality=1`}
                  className="absolute inset-0 w-full h-full"
                  allowFullScreen
                  scrolling="no"
                />
              </div>
              
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">{selectedVideo.title}</h4>
              
              <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
                  </svg>
                  {formatViewCount(selectedVideo.view_count)}播放
                </span>
                <span>{selectedVideo.author}</span>
                <span>{formatDuration(selectedVideo.duration)}</span>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
                {selectedVideo.description}
              </p>
              
              <a
                href={selectedVideo.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm font-medium"
              >
                在B站观看完整视频
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default VideoSection;
