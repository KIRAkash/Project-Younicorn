import React from 'react';
import { Sparkles, MessageSquare } from 'lucide-react';
import { useBeacon } from './beacon-context';
import { cn } from '@/utils';

export function BeaconButton() {
  const { isOpen, isMinimized, openBeacon, restoreBeacon } = useBeacon();

  // Don't show if fully open (not minimized)
  if (isOpen && !isMinimized) return null;

  // Show different state if minimized (session active)
  const isSessionActive = isMinimized;

  return (
    <button
      onClick={() => isSessionActive ? restoreBeacon() : openBeacon()}
      className={cn(
        "beacon-floating-button",
        "fixed bottom-6 right-6",
        "w-14 h-14",
        "bg-gradient-to-br from-purple-600 to-indigo-600",
        "hover:from-purple-700 hover:to-indigo-700",
        "text-white",
        "rounded-full",
        "shadow-lg hover:shadow-xl",
        "transition-all duration-300",
        "flex items-center justify-center",
        "z-40",
        "group",
        isSessionActive && "ring-4 ring-purple-400/50",
        "focus:outline-none focus:ring-4 focus:ring-purple-500/50"
      )}
      aria-label={isSessionActive ? "Restore Beacon Chat" : "Open Beacon Chat"}
      title={isSessionActive ? "Restore chat session" : "Chat with Beacon"}
    >
      {isSessionActive ? (
        <MessageSquare 
          size={24} 
          className="group-hover:scale-110 transition-transform" 
          strokeWidth={2.5}
        />
      ) : (
        <Sparkles 
          size={24} 
          className="group-hover:scale-110 transition-transform" 
          strokeWidth={2.5}
        />
      )}
      
      {/* Session active indicator */}
      {isSessionActive && (
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white shadow-lg" />
      )}
    </button>
  );
}
