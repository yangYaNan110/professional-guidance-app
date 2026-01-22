#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-summary Skill - 视频摘要生成

功能：
1. 分析视频内容，提取关键知识点
2. 生成视频摘要文本
3. 生成时间戳标记
4. 生成剪辑脚本
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class VideoSummary:
    """视频摘要"""
    title: str
    summary: str
    key_points: List[str] = field(default_factory=list)
    timestamps: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    duration: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ClipScript:
    """剪辑脚本"""
    clips: List[Dict[str, Any]] = field(default_factory=list)
    total_duration: int = 0
    output_duration: int = 0


class VideoSummarizer:
    """视频摘要生成器"""
    
    def __init__(self):
        pass
    
    def summarize(
        self,
        video_info: Dict[str, Any],
        transcript: Optional[str] = None,
        output_duration: int = 300
    ) -> VideoSummary:
        """生成视频摘要"""
        title = video_info.get("title", "")
        description = video_info.get("description", "")
        duration = video_info.get("duration", 0)
        
        key_points = self._extract_key_points(transcript or description)
        summary = self._generate_summary(title, key_points, description)
        timestamps = self._extract_timestamps(transcript or description, duration)
        topics = self._extract_topics(title, description)
        
        return VideoSummary(
            title=title,
            summary=summary,
            key_points=key_points,
            timestamps=timestamps,
            topics=topics,
            duration=duration
        )
    
    def generate_clip_script(
        self,
        summary: VideoSummary,
        transcript: str,
        output_duration: int = 180
    ) -> ClipScript:
        """生成剪辑脚本"""
        original_duration = summary.duration
        keep_ratio = output_duration / original_duration if original_duration > 0 else 0.5
        
        clips = []
        total_duration = 0
        
        intro_duration = min(30, int(60 * keep_ratio))
        clips.append({
            "start": 0,
            "end": intro_duration,
            "content": "开场介绍",
            "label": "开场"
        })
        total_duration += intro_duration
        
        for i, point in enumerate(summary.key_points[:5]):
            if total_duration >= output_duration:
                break
            
            point_duration = min(40, int(60 * keep_ratio))
            start_time = int((i + 1) * original_duration / (len(summary.key_points[:5]) + 2))
            end_time = min(start_time + point_duration, original_duration)
            
            clips.append({
                "start": start_time,
                "end": end_time,
                "content": point,
                "label": f"知识点 {i + 1}"
            })
            total_duration += (end_time - start_time)
        
        return ClipScript(
            clips=clips,
            total_duration=total_duration,
            output_duration=output_duration
        )
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        key_points = []
        
        sentences = re.split(r'[。！？\n]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            if len(sentence) < 20:
                continue
            
            keywords = ["是", "指", "包括", "主要", "核心", "特点", "作用", "意义", "发展"]
            if any(kw in sentence for kw in keywords):
                key_points.append(sentence)
        
        key_points = list(dict.fromkeys(key_points))
        return key_points[:10]
    
    def _generate_summary(
        self,
        title: str,
        key_points: List[str],
        description: str
    ) -> str:
        """生成摘要"""
        parts = []
        
        parts.append(f"本视频介绍了{title}。")
        
        if key_points:
            summary_points = key_points[:3]
            parts.append("主要内容：")
            for point in summary_points:
                sentence = point[:100] + "..." if len(point) > 100 else point
                parts.append(f"- {sentence}")
        
        return "\n".join(parts)
    
    def _extract_timestamps(self, text: str, duration: int) -> List[Dict[str, Any]]:
        """提取时间戳"""
        timestamps = []
        
        time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
        matches = re.findall(time_pattern, text)
        
        total_length = len(text)
        
        for i, match in enumerate(matches[:10]):
            pos = text.find(match)
            if pos >= 0:
                ratio = pos / total_length if total_length > 0 else 0
                time_sec = int(ratio * duration)
                
                timestamps.append({
                    "time": time_sec,
                    "label": f"章节 {i + 1}"
                })
        
        if not timestamps or timestamps[0].get("time", 0) > 0:
            timestamps.insert(0, {
                "time": 0,
                "label": "开场"
            })
        
        return timestamps
    
    def _extract_topics(self, title: str, description: str) -> List[str]:
        """提取主题"""
        topics = []
        
        title_words = re.findall(r'[\u4e00-\u9fff]{2,}', title)
        topics.extend(title_words[:5])
        
        desc_words = re.findall(r'[\u4e00-\u9fff]{2,}', description)
        topics.extend([w for w in desc_words if w not in topics][:10])
        
        return list(set(topics))[:10]


def generate_video_summary(
    video_info: Dict[str, Any],
    transcript: Optional[str] = None,
    output_duration: int = 300
) -> VideoSummary:
    """生成视频摘要"""
    summarizer = VideoSummarizer()
    return summarizer.summarize(video_info, transcript, output_duration)


def generate_clip_script(
    summary: VideoSummary,
    transcript: str,
    output_duration: int = 180
) -> ClipScript:
    """生成剪辑脚本"""
    summarizer = VideoSummarizer()
    return summarizer.generate_clip_script(summary, transcript, output_duration)


if __name__ == "__main__":
    video_info = {
        "title": "社会学专业介绍",
        "description": "本视频介绍了社会学专业的起源、发展、现状和就业前景...",
        "duration": 600
    }
    
    transcript = """
    大家好，今天我们来介绍社会学专业。
    社会学起源于19世纪中叶，孔德、涂尔干等学者开始系统研究社会现象。
    社会学的研究对象包括社会关系、社会结构、社会变迁等。
    核心课程包括社会学概论、社会研究方法、社会心理学等。
    毕业生可以在政府机关、企事业单位、社会组织等从事相关工作。
    总结一下，社会学是一门研究社会现象的重要学科。
    """
    
    summary = generate_video_summary(video_info, transcript)
    
    print(f"标题: {summary.title}")
    print(f"\n摘要:\n{summary.summary}")
    print(f"\n关键点: {len(summary.key_points)}个")
