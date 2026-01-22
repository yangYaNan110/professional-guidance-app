import React from 'react';
import { Message } from '../../types';

interface VoiceInputProps {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onTranscript?: (transcript: string) => void;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({
  isRecording,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <button
      onClick={isRecording ? onStopRecording : onStartRecording}
      className={`
        p-3 rounded-full transition-all duration-300
        ${isRecording
          ? 'bg-red-500 text-white animate-pulse'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }
      `}
      aria-label={isRecording ? '停止录音' : '开始录音'}
    >
      <svg
        className="w-6 h-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        {isRecording ? (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        ) : (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        )}
      </svg>
    </button>
  );
};

interface VoiceOutputProps {
  audioUrl?: string;
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
  text: string;
}

export const VoiceOutput: React.FC<VoiceOutputProps> = ({
  audioUrl,
  isPlaying,
  onPlay,
  onPause,
  text,
}) => {
  if (!audioUrl) return null;

  return (
    <button
      onClick={isPlaying ? onPause : onPlay}
      className={`
        p-2 rounded-full transition-colors
        ${isPlaying
          ? 'bg-primary-100 text-primary-600'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }
      `}
      aria-label={isPlaying ? '暂停播放' : '播放语音'}
      title={text}
    >
      <svg
        className="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        {isPlaying ? (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
        ) : (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
        )}
      </svg>
    </button>
  );
};

interface MessageBubbleProps {
  message: Message;
  isOwn: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isOwn,
}) => {
  const emotionEmojis: Record<string, string> = {
    friendly: '😊',
    supportive: '🤝',
    anxious: '💭',
    confused: '🤔',
    frustrated: '💪',
    confident: '🌟',
  };

  return (
    <div
      className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`
          max-w-[70%] p-4 rounded-2xl
          ${isOwn
            ? 'bg-primary-500 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-800 rounded-bl-md'
          }
        `}
      >
        {!isOwn && (
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-2">🎯</span>
            <span className="font-medium text-primary-600">就业助手</span>
            {message.emotion && (
              <span className="ml-2 text-sm">
                {emotionEmojis[message.emotion] || ''}
              </span>
            )}
          </div>
        )}
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div
          className={`text-xs mt-2 ${
            isOwn ? 'text-primary-100' : 'text-gray-400'
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

interface TypingIndicatorProps {
  visible: boolean;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ visible }) => {
  if (!visible) return null;

  return (
    <div className="flex justify-start">
      <div className="bg-gray-100 p-4 rounded-2xl rounded-bl-md">
        <div className="flex space-x-1">
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
};
