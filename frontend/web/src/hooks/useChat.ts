import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message, Conversation } from '../types';
import { chatApi } from '../services/api';

interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isTyping: boolean;
  
  // Actions
  setConversations: (conversations: Conversation[]) => void;
  addConversation: (conversation: Conversation) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setTyping: (typing: boolean) => void;
  sendMessage: (userId: string, content: string) => Promise<void>;
  loadConversations: (userId: string) => Promise<void>;
  loadMessages: (conversationId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      currentConversation: null,
      messages: [],
      isTyping: false,

      setConversations: (conversations) => set({ conversations }),
      
      addConversation: (conversation) =>
        set((state) => ({
          conversations: [conversation, ...state.conversations]
        })),
      
      setCurrentConversation: (conversation) => set({ currentConversation: conversation }),
      
      setMessages: (messages) => set({ messages }),
      
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message]
        })),
      
      setTyping: (typing) => set({ isTyping: typing }),

      sendMessage: async (userId, content) => {
        const { currentConversation } = get();
        set({ isTyping: true });

        try {
          const response = await chatApi.sendMessage({
            user_id: userId,
            message,
            conversation_id: currentConversation?.id,
          });

          // 添加AI回复
          get().addMessage({
            id: response.reply.id,
            role: 'assistant',
            content: response.reply.content,
            emotion: response.reply.emotion,
            created_at: response.reply.created_at,
          });
        } finally {
          set({ isTyping: false });
        }
      },

      loadConversations: async (userId) => {
        try {
          const conversations = await chatApi.getConversations();
          set({ conversations });
        } catch (error) {
          console.error('加载对话列表失败:', error);
        }
      },

      loadMessages: async (conversationId) => {
        try {
          const messages = await chatApi.getMessages(conversationId);
          set({ messages });
        } catch (error) {
          console.error('加载消息失败:', error);
        }
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        currentConversation: state.currentConversation,
      }),
    }
  )
);
