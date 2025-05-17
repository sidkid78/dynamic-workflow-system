import { useState, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message, ChatSession, QueryRequest, WorkflowResponse } from '@/types';
import { processQuery } from '@/lib/api';

const STORAGE_KEY = 'dynamic-workflow-chat';
const MAX_MESSAGES_TO_STORE = 50; // Store the last 50 messages

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  // Define initializeNewSession first
  const initializeNewSession = useCallback(() => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    setMessages([]);
  }, []);

  // Initialize session or load existing one
  useEffect(() => {
    const storedSession = localStorage.getItem(STORAGE_KEY);
    if (storedSession) {
      try {
        const session: ChatSession = JSON.parse(storedSession);
        setMessages(session.messages);
        setSessionId(session.id);
      } catch (e) {
        console.error('Failed to parse stored session:', e);
        initializeNewSession();
      }
    } else {
      initializeNewSession();
    }
  }, [initializeNewSession]);

  // Save session when messages change
  useEffect(() => {
    if (sessionId && messages.length > 0) {
      const messagesToStore = messages.slice(-MAX_MESSAGES_TO_STORE);
      const session: ChatSession = {
        id: sessionId,
        messages: messagesToStore, // Only store recent messages
        created_at: messagesToStore[0]?.timestamp || Date.now(),
        updated_at: Date.now(),
      };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
      } catch (e) {
        console.error('Failed to save session to localStorage:', e);
        // Optionally, notify the user or try to clear some older, less critical storage
        if (e instanceof DOMException && (e.name === 'QuotaExceededError' || e.name === 'NS_ERROR_DOM_QUOTA_REACHED')) {
          // Attempt to clear the storage if quota is exceeded to prevent future errors
          // This is a drastic measure and means the user loses their persisted chat history.
          // Consider a more nuanced approach if retaining some history is critical.
          // For now, we'll log and the user might need to clear manually or we implement a clear button.
          console.warn('LocalStorage quota exceeded. Consider clearing storage or reducing data size.');
          // localStorage.removeItem(STORAGE_KEY); // Example: Uncomment to clear if it happens again
        }
      }
    }
  }, [messages, sessionId]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const request: QueryRequest = {
        query: content,
        session_id: sessionId,
      };

      const response: WorkflowResponse = await processQuery(request);

      // Add assistant message
      const assistantMessage: Message = {
        id: uuidv4(),
        content: response.final_response,
        role: 'assistant',
        timestamp: Date.now(),
        workflow_info: response.workflow_info,
        intermediate_steps: response.intermediate_steps,
        processing_time: response.processing_time
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'An unknown error occurred');
      console.error('Error sending message:', e);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const clearChat = useCallback(() => {
    initializeNewSession();
  }, [initializeNewSession]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
}