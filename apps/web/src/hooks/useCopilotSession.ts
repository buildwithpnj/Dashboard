import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { api } from '@/lib/api';

export interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
  suggested_action?: {
    action_name: string;
    payload: any;
  };
}

export function useCopilotSession() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    setIsSending(true);
    
    // Optimistic user message
    const userMsg: CopilotMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);

    try {
      const data = await api<any>('/api/copilot/chat?query=' + encodeURIComponent(text), {
        method: 'POST',
        body: {
          current_route: pathname || '/',
          visible_module_hints: [],
          selected_entity_id: null,
          workflow_state: null
        }
      });

      const assistantMsg: CopilotMessage = {
        role: 'assistant',
        content: data.reply,
        suggested_action: data.suggested_action
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
    } finally {
      setIsSending(false);
    }
  };

  return {
    isOpen,
    setIsOpen,
    messages,
    sendMessage,
    isSending
  };
}
