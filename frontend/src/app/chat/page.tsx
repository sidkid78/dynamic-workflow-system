// app/chat/page.tsx
'use client';

import { useChat } from '@/hooks/use-chat';
import MessageList from '@/components/chat/message-list';
import ChatInput from '@/components/chat/chat-input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export default function ChatPage() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  
  return (
    <div className="flex flex-col h-screen bg-background dark:bg-background">
      <header className="border-b dark:border-gray-800 bg-background p-4">
        <h1 className="text-xl font-bold text-foreground dark:text-gray-100">
          Dynamic Workflow System
        </h1>
        <p className="text-sm text-muted-foreground dark:text-gray-400">
          Automatically selects the optimal workflow pattern for each query
        </p>
      </header>
      
      <div className="flex-1 flex flex-col overflow-hidden bg-background dark:bg-gray-900/50">
        {error && (
          <Alert variant="destructive" className="m-4 dark:border-red-900/50 dark:bg-red-900/20">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}
        
        <MessageList messages={messages} isLoading={isLoading} />
        
        <ChatInput 
          onSend={sendMessage} 
          onClear={clearChat}
          isLoading={isLoading}
          placeholder="Ask a question or provide a task..."
        />
      </div>
    </div>
  );
}