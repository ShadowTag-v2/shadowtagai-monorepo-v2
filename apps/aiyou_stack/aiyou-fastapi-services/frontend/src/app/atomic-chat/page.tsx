'use client';

import { Bot, Loader2, Send, Sparkles, User } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  tier?: 'FREE' | 'FLASH' | 'PRO';
}

const initialMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: "Hello! I'm connected to the Autoresearch swarm. How can I help you today?",
    timestamp: new Date(),
    agent: 'FM-DISPATCH',
    tier: 'PRO',
  },
];

export default function AtomicChat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate Autoresearch response
    setTimeout(() => {
      const agents = ['FM-ANALYST', 'FM-RESEARCHER', 'FM-WRITER'];
      const tiers: ('FREE' | 'FLASH' | 'PRO')[] = ['FREE', 'FLASH', 'PRO'];

      const response: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I've processed your request through the swarm. Based on the query "${input.slice(0, 50)}...", here's what the agents found:\n\n1. **Analysis**: Your request has been routed to the appropriate specialists.\n2. **Processing**: Multiple agents collaborated on this response.\n3. **Confidence**: High (validated by 3 independent agents)\n\nWould you like me to elaborate on any specific aspect?`,
        timestamp: new Date(),
        agent: agents[Math.floor(Math.random() * agents.length)],
        tier: tiers[Math.floor(Math.random() * tiers.length)],
      };

      setMessages((prev) => [...prev, response]);
      setIsLoading(false);
    }, 1500);
  };

  const getTierColor = (tier?: string) => {
    switch (tier) {
      case 'PRO':
        return 'text-purple-500';
      case 'FLASH':
        return 'text-amber-500';
      default:
        return 'text-slate-400';
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">Atomic Chat</h1>
        <p className="text-slate-500">Real-time conversation with Autoresearch swarm</p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-auto bg-white rounded-xl border border-slate-100 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex gap-3',
                message.role === 'user' ? 'justify-end' : 'justify-start',
              )}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-shadowtag_v4-primary flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}

              <div
                className={cn(
                  'max-w-[70%] rounded-2xl px-4 py-3',
                  message.role === 'user' ? 'bg-shadowtag_v4-primary text-white' : 'bg-slate-100',
                )}
              >
                {message.role === 'assistant' && message.agent && (
                  <div className="flex items-center gap-2 text-xs mb-2">
                    <span className={getTierColor(message.tier)}>{message.tier}</span>
                    <span className="text-slate-500">{message.agent}</span>
                  </div>
                )}
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p
                  className={cn(
                    'text-xs mt-2',
                    message.role === 'user' ? 'text-indigo-200' : 'text-slate-400',
                  )}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>

              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                  <User className="h-4 w-4 text-slate-600" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-shadowtag_v4-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-slate-100 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Swarm processing...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message the swarm..."
              className="w-full px-4 py-3 pr-12 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="button"
              className="absolute right-12 top-1/2 -translate-y-1/2 text-slate-400 hover:text-shadowtag_v4-secondary"
              title="Use Gemini PRO"
            >
              <Sparkles className="h-5 w-5" />
            </button>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-3 bg-shadowtag_v4-primary text-white rounded-xl hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Connected to Autoresearch swarm (600 agents) | Shift 2 active
        </p>
      </form>
    </div>
  );
}
