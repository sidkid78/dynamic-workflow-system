// components/chat/chat-input.tsx
'use client'

import { useState, FormEvent, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, Eraser } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  onClear: () => void;
  isLoading: boolean;
  placeholder?: string;
}

export default function ChatInput({ 
  onSend, 
  onClear, 
  isLoading, 
  placeholder = "Type your message..." 
}: ChatInputProps) {
  const [message, setMessage] = useState<string>('');
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (message.trim() && !isLoading) {
      onSend(message);
      setMessage('');
    }
  };
  
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Ctrl/Cmd + Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  return (
    <div className="p-4 border-t bg-white">
      <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
        <div className="relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={3}
            className="resize-none pr-12"
            disabled={isLoading}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!message.trim() || isLoading}
            className="absolute bottom-2 right-2"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
        
        <div className="flex justify-between items-center">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <Eraser className="h-3 w-3" /> 
            Clear Chat
          </Button>
          
          <span className="text-xs text-gray-500">
            Press <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">Ctrl</kbd> + 
            <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs ml-1">Enter</kbd> to send
          </span>
        </div>
      </form>
    </div>
  );
}