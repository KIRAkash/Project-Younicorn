import React, { useState, useEffect, useMemo, useRef } from 'react';
import { X, Send, Loader2, Minus, CheckCircle, AlertCircle } from 'lucide-react';
import { useBeacon } from './beacon-context';
import { BeaconContextTag } from './beacon-context-tag';
import { cn } from '@/utils';
import { beaconApi, type BeaconToolCall } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { auth } from '@/config/firebase';
import ReactMarkdown from 'react-markdown';

interface BeaconChatProps {
  startupId: string;
  analysisData?: any;
  startupData?: any;
}

interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  toolCalls?: BeaconToolCall[];
  context?: string; // Context that was selected when message was sent
}

export function BeaconChat({ startupId, analysisData, startupData }: BeaconChatProps) {
  const { isOpen, isMinimized, closeBeacon, minimizeBeacon, contextItems, removeContext, clearAllContext } = useBeacon();
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Generate unique session ID - regenerate when user closes the chat
  const [sessionId, setSessionId] = useState(() => {
    const userId = auth.currentUser?.uid || 'anonymous';
    const timestamp = Date.now();
    return `${userId}_${startupId}_${timestamp}`;
  });

  // Function to generate new session ID
  const generateNewSessionId = () => {
    const userId = auth.currentUser?.uid || 'anonymous';
    const timestamp = Date.now();
    return `${userId}_${startupId}_${timestamp}`;
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  // Reset messages when modal closes (to start fresh on next open)
  useEffect(() => {
    if (!isOpen) {
      setMessages([]);
      setStreamingMessage('');
    }
  }, [isOpen]);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0 && isOpen) {
      // Use template literals (backticks) for the multi-line string
      const welcomeMessageContent = `Hi! I'm **Beacon** 🤖, your AI investment assistant. I am here to help you with your queries related to the startup analysis.

You can ask me to:
* **Answer questions** about the analysis (e.g., "What are the team's strengths?")
* **Add a question** for the founders ✍️ (e.g., "Add a question: What is their customer acquisition cost?")
* **Log a private note** 📝 (e.g., "Add a note: The team seems strong...")
* **Update the startup's status** 📊 (e.g., "Update status to 'On Watch'...")
* **Trigger a re-analysis** 🔄 with a new focus.

What would you like to do first?`;

      const welcomeMessage: Message = {
        id: 'agent-1',
        role: 'agent',
        content: welcomeMessageContent,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Capture context before clearing
    const contextLabel = contextItems.length > 0 
      ? contextItems[0].subsection || contextItems[0].sectionTitle
      : undefined;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      context: contextLabel // Store context with message
    };

    const messageText = inputValue;
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setStreamingMessage('');

    try {
      // Stream response from Beacon API
      let fullResponse = '';
      
      // Get selected section from context if available (send empty string if none)
      const selectedSection = contextLabel || "";
      
      for await (const chunk of beaconApi.chatStream({
        startup_id: startupId,
        message: messageText,
        session_id: sessionId,  // Firestore automatically handles conversation history
        selected_section: selectedSection  // Pass selected section context (empty string if none)
      })) {
        fullResponse += chunk;
        setStreamingMessage(fullResponse);
      }

      // Add complete agent response
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        role: 'agent',
        content: fullResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, agentMessage]);
      setStreamingMessage('');

      // Clear context after successful message send
      clearAllContext();
    } catch (error: any) {
      console.error('Error calling Beacon API:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `agent-${Date.now()}`,
        role: 'agent',
        content: `I apologize, but I encountered an error: ${error.message}. Please try again or contact support if the issue persists.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setStreamingMessage('');

      toast({
        title: 'Error',
        description: 'Failed to communicate with Beacon. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen || isMinimized) return null;

  return (
    <>
      {/* Glassmorphism Backdrop */}
      <div
        className={cn(
          "fixed inset-0 z-40",
          "bg-black/20 backdrop-blur-sm",
          "animate-in fade-in duration-300"
        )}
        onClick={minimizeBeacon}
      />

      {/* Centered Modal */}
      <div
        className={cn(
          "beacon-chat-modal",
          "fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2",
          "w-[90vw] max-w-6xl h-[80vh] max-h-[700px]",
          "bg-white/95 dark:bg-gray-900/95",
          "backdrop-blur-xl",
          "border border-gray-200 dark:border-gray-700",
          "rounded-3xl shadow-2xl",
          "flex flex-col",
          "z-50",
          "animate-in zoom-in-95 duration-300"
        )}
      >
      {/* Header */}
      <div className="beacon-header flex-shrink-0 bg-gradient-to-r from-purple-600 to-indigo-600 p-6 rounded-t-3xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <span className="text-2xl">🔮</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                Younicorn Beacon
              </h2>
              <p className="text-sm text-purple-100 mt-0.5">
                Your AI Investment Assistant
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={minimizeBeacon}
              className="p-2 rounded-xl hover:bg-white/20 transition-colors text-white"
              aria-label="Minimize Beacon"
              title="Minimize (keeps session alive)"
            >
              <Minus size={20} />
            </button>
            <button
              onClick={() => {
                // Generate new session ID for next conversation
                setSessionId(generateNewSessionId());
                closeBeacon();
              }}
              className="p-2.5 rounded-full bg-gradient-to-br from-purple-500 to-rose-500 hover:from-purple-600 hover:to-rose-600 transition-all duration-200 text-white shadow-lg hover:shadow-xl"
              aria-label="Close Beacon"
              title="Close session and start fresh"
            >
              <X size={18} strokeWidth={2.5} />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="beacon-messages flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "message",
              message.role === 'user' && "flex justify-end",
              message.role === 'system' && "flex justify-center"
            )}
          >
            {message.role === 'system' ? (
              <div className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 px-4 py-2 rounded-full shadow-sm border border-gray-200 dark:border-gray-700">
                {message.content}
              </div>
            ) : (
              <div className="max-w-[85%] space-y-2">
                <div
                  className={cn(
                    "rounded-3xl px-5 py-3 shadow-sm",
                    message.role === 'user'
                      ? "bg-gradient-to-br from-purple-600 to-indigo-600 text-white"
                      : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700"
                  )}
                >
                  {message.role === 'user' ? (
                    <div className="space-y-2">
                      <p className="text-[15px] leading-relaxed whitespace-pre-wrap font-['Inter',_'system-ui',_sans-serif] text-white">{message.content}</p>
                      {message.context && (
                        <div className="flex items-center gap-1.5 text-xs text-white/70 bg-white/10 px-2.5 py-1 rounded-full w-fit">
                          <span className="text-[10px]">📍</span>
                          <span>{message.context}</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-[15px] leading-relaxed font-['Inter',_'system-ui',_sans-serif] prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                          li: ({ children }) => <li className="ml-2">{children}</li>,
                          strong: ({ children }) => <strong className="font-semibold text-purple-700 dark:text-purple-300">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          code: ({ children }) => <code className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>,
                          pre: ({ children }) => <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg overflow-x-auto mb-2">{children}</pre>,
                          h1: ({ children }) => <h1 className="text-xl font-bold mb-2 text-purple-700 dark:text-purple-300">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-purple-700 dark:text-purple-300">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-base font-semibold mb-1 text-purple-700 dark:text-purple-300">{children}</h3>,
                          blockquote: ({ children }) => <blockquote className="border-l-4 border-purple-500 pl-3 italic my-2">{children}</blockquote>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}
                  <span className="text-xs opacity-70 mt-2 block">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                {/* Tool Execution Results */}
                {message.toolCalls && message.toolCalls.length > 0 && (
                  <div className="space-y-2 ml-4">
                    {message.toolCalls.map((toolCall, idx) => (
                      <div
                        key={idx}
                        className={cn(
                          "flex items-start gap-2 px-3 py-2 rounded-xl text-sm",
                          toolCall.result.success
                            ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200"
                            : "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200"
                        )}
                      >
                        {toolCall.result.success ? (
                          <CheckCircle size={16} className="flex-shrink-0 mt-0.5" />
                        ) : (
                          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className="font-medium capitalize">{toolCall.tool.replace('_', ' ')}</p>
                          <p className="text-xs opacity-80 mt-0.5">
                            {toolCall.result.message || toolCall.result.error}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Streaming message */}
        {streamingMessage && (
          <div className="max-w-[85%] space-y-2">
            <div className="rounded-3xl px-5 py-3 shadow-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700">
              <div className="text-[15px] leading-relaxed font-['Inter',_'system-ui',_sans-serif] prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="ml-2">{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-purple-700 dark:text-purple-300">{children}</strong>,
                    em: ({ children }) => <em className="italic">{children}</em>,
                    code: ({ children }) => <code className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>,
                    pre: ({ children }) => <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg overflow-x-auto mb-2">{children}</pre>,
                    h1: ({ children }) => <h1 className="text-xl font-bold mb-2 text-purple-700 dark:text-purple-300">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-purple-700 dark:text-purple-300">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-base font-semibold mb-1 text-purple-700 dark:text-purple-300">{children}</h3>,
                    blockquote: ({ children }) => <blockquote className="border-l-4 border-purple-500 pl-3 italic my-2">{children}</blockquote>,
                  }}
                >
                  {streamingMessage}
                </ReactMarkdown>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <Loader2 size={14} className="animate-spin text-purple-600" />
                <span className="text-xs opacity-70">Streaming...</span>
              </div>
            </div>
          </div>
        )}

        {isLoading && !streamingMessage && (
          <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 px-4 py-3 rounded-3xl shadow-sm border border-gray-200 dark:border-gray-700 max-w-[85%]">
            <Loader2 size={18} className="animate-spin text-purple-600" />
            <span className="text-sm font-medium">Beacon is thinking...</span>
          </div>
        )}
        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="beacon-input flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-800 rounded-b-3xl">
        {/* Context Chips */}
        {contextItems.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {contextItems.map((context) => (
              <div
                key={context.sectionId}
                className={cn(
                  "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm",
                  "bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30",
                  "border border-purple-300 dark:border-purple-600",
                  "text-purple-700 dark:text-purple-300 font-medium shadow-sm"
                )}
              >
                <span className="font-medium">
                  {context.subsection || context.sectionTitle}
                </span>
                <button
                  onClick={() => removeContext(context.sectionId)}
                  className="hover:bg-purple-200 dark:hover:bg-purple-800 rounded-full p-1 transition-colors"
                  aria-label="Remove context"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
            {contextItems.length > 1 && (
              <button
                onClick={clearAllContext}
                className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 underline"
              >
                Clear all
              </button>
            )}
          </div>
        )}

        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className={cn(
              "flex-1 px-4 py-3 rounded-2xl",
              "bg-gray-50 dark:bg-gray-900",
              "border-2 border-gray-200 dark:border-gray-700",
              "text-gray-900 dark:text-white",
              "placeholder-gray-400 dark:placeholder-gray-500",
              "focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20",
              "text-[15px] font-['Inter',_'system-ui',_sans-serif]",
              "transition-all duration-200"
            )}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className={cn(
              "px-5 py-3 rounded-2xl",
              "bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700",
              "text-white font-medium shadow-lg hover:shadow-xl",
              "transition-all duration-200",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none",
              "focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            )}
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
      </div>
    </>
  );
}
