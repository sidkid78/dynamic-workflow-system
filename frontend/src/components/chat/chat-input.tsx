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
    <div className="p-4 border-t bg-background dark:border-slate-800 dark:bg-slate-950/80">
      <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
        <div className="relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={3}
            className="pr-24 resize-none dark:bg-slate-900/70 dark:border-slate-700 dark:placeholder:text-slate-400"
            disabled={isLoading}
          />
          <div className="absolute bottom-2 right-2 flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={onClear}
              disabled={isLoading}
              className="text-muted-foreground hover:text-foreground dark:hover:text-slate-300"
            >
              <Eraser className="h-4 w-4" />
            </Button>
            <Button
              type="submit"
              size="icon"
              disabled={!message.trim() || isLoading}
              className="text-white dark:text-slate-50 dark:bg-primary/90 dark:hover:bg-primary"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
        <div className="text-xs text-muted-foreground text-right dark:text-slate-400">
          Press <kbd className="px-1 py-0.5 bg-muted rounded dark:bg-slate-800 dark:text-slate-300">Ctrl</kbd> + <kbd className="px-1 py-0.5 bg-muted rounded dark:bg-slate-800 dark:text-slate-300">Enter</kbd> to send
        </div>
      </form>
    </div>
  );
}