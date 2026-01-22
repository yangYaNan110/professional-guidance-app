import React, { useState } from 'react';
import Taro from '@tarojs/taro';
import { View, Text, Button, Input } from '@tarojs/components';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  emotion?: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好！我是您的专业选择助手 🎯\n\n我可以帮您：\n• 分析您的学科优势和兴趣\n• 推荐适合的大学专业方向\n• 解答专业选择相关问题\n\n请问有什么可以帮到您的？',
      emotion: 'friendly'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      const replies = [
        '我理解您的困惑。其实，每个人都有自己独特的优势，关键是找到与您兴趣和能力匹配的领域。',
        '您提到对某个领域感兴趣，这个专业发展前景很好。我们可以一起分析一下您的优势在哪里。',
        '这是一个很好的问题！让我为您分析一下当前的专业情况...'
      ];

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: replies[Math.floor(Math.random() * replies.length)],
        emotion: 'supportive'
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <View className='chat-container'>
      <View className='chat-header'>
        <Text className='title'>💬 智能助手对话</Text>
      </View>

      <View className='messages-list'>
        {messages.map((msg) => (
          <View
            key={msg.id}
            className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}
          >
            {msg.role === 'assistant' && (
              <View className='assistant-avatar'>
                <Text>🎯</Text>
              </View>
            )}
            <View className={`message-content ${msg.role === 'user' ? 'user-content' : ''}`}>
              <Text>{msg.content}</Text>
            </View>
          </View>
        ))}

        {isTyping && (
          <View className='message message-assistant'>
            <View className='assistant-avatar'>
              <Text>🎯</Text>
            </View>
            <View className='typing-indicator'>
              <View className='dot' />
              <View className='dot' />
              <View className='dot' />
            </View>
          </View>
        )}
      </View>

      <View className='input-area'>
        <Button
          className='voice-btn'
          onClick={() => Taro.showToast({ title: '语音功能开发中', icon: 'none' })}
        >
          🎤
        </Button>
        <Input
          className='message-input'
          value={input}
          onInput={(e) => setInput(e.detail.value)}
          onConfirm={handleSend}
          placeholder='输入您的问题或想法...'
        />
        <Button className='send-btn' onClick={handleSend}>
          发送
        </Button>
      </View>
    </View>
  );
};

export default ChatPage;
