// components/chat/message-list.tsx
'use client'

import { useRef, useEffect } from 'react';
import { Message } from '@/types';
import MessageItem from './message-item';
import { Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when messages change or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);
  
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-500">
          <div className="h-16 w-16 rounded-full bg-purple-100 flex items-center justify-center mb-4">
            <Bot className="h-8 w-8 text-purple-500" />
          </div>
          <h3 className="text-lg font-medium mb-2">Dynamic Workflow System</h3>
          <p className="max-w-md">
            Ask a question or provide a task. The system will automatically select
            the most appropriate workflow pattern and execute it using specialized agents.
          </p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex items-center space-x-2 p-4 bg-white rounded-lg mb-4 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-purple-200" />
              <div className="flex-1">
                <div className="h-4 w-24 bg-purple-100 rounded mb-2" />
                <div className="space-y-2">
                  <div className="h-3 bg-gray-100 rounded w-full" />
                  <div className="h-3 bg-gray-100 rounded w-5/6" />
                  <div className="h-3 bg-gray-100 rounded w-3/4" />
                </div>
              </div>
            </div>
          )}
          
          {/* Element to scroll to */}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
}