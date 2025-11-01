import React from 'react';
import { X } from 'lucide-react';
import { cn } from '@/utils';

interface BeaconContextTagProps {
  sectionTitle: string;
  sectionType: 'team' | 'market' | 'product' | 'competition' | 'synthesis' | 'risks' | 'opportunities';
  onDismiss: () => void;
  className?: string;
}

const SECTION_ICONS: Record<string, string> = {
  team: '👥',
  market: '🎯',
  product: '🚀',
  competition: '⚔️',
  synthesis: '💎',
  risks: '⚠️',
  opportunities: '🌟'
};

const SECTION_COLORS: Record<string, string> = {
  team: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  market: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  product: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
  competition: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  synthesis: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300',
  risks: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  opportunities: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
};

export function BeaconContextTag({ 
  sectionTitle, 
  sectionType, 
  onDismiss,
  className 
}: BeaconContextTagProps) {
  return (
    <div
      className={cn(
        "beacon-context-tag",
        "inline-flex items-center gap-2",
        "px-3 py-1.5",
        "rounded-full",
        "text-sm font-medium",
        "border",
        SECTION_COLORS[sectionType] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
        className
      )}
    >
      <span className="context-icon text-base" aria-hidden="true">
        {SECTION_ICONS[sectionType] || '📄'}
      </span>
      <span className="context-title">{sectionTitle}</span>
      <button
        onClick={onDismiss}
        className={cn(
          "context-dismiss",
          "ml-1 -mr-1",
          "p-0.5",
          "rounded-full",
          "hover:bg-black/10 dark:hover:bg-white/10",
          "transition-colors",
          "focus:outline-none focus:ring-2 focus:ring-offset-1",
          "focus:ring-current"
        )}
        aria-label="Clear section context"
        title="Clear section context"
      >
        <X size={14} strokeWidth={2.5} />
      </button>
    </div>
  );
}
