import React from 'react';
import { MessageSquare } from 'lucide-react';
import { useBeacon, SectionContext } from './beacon-context';
import { cn } from '@/utils';

interface BeaconSubsectionIconProps {
  sectionId: string;
  sectionTitle: string;
  subsectionTitle: string;
  sectionType: 'team' | 'market' | 'product' | 'competition' | 'synthesis';
  sectionData?: any;
  className?: string;
}

export function BeaconSubsectionIcon({
  sectionId,
  sectionTitle,
  subsectionTitle,
  sectionType,
  sectionData,
  className
}: BeaconSubsectionIconProps) {
  const { openBeacon, addContext, isOpen } = useBeacon();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const context: SectionContext = {
      sectionId: `${sectionId}-${subsectionTitle.toLowerCase().replace(/\s+/g, '-')}`,
      sectionTitle,
      sectionType,
      sectionData,
      subsection: subsectionTitle
    };
    
    if (isOpen) {
      // If chat is already open, just add context
      addContext(context);
    } else {
      // If chat is closed, open it with context
      openBeacon(context);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        "beacon-subsection-icon",
        "inline-flex items-center justify-center",
        "w-5 h-5 ml-2",
        "text-purple-500 hover:text-purple-700",
        "dark:text-purple-400 dark:hover:text-purple-300",
        "transition-all duration-200",
        "hover:scale-110",
        "opacity-60 hover:opacity-100",
        "focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 rounded",
        className
      )}
      aria-label={`Add ${subsectionTitle} to chat context`}
      title={`Chat about ${subsectionTitle}`}
    >
      <MessageSquare size={16} strokeWidth={2} />
    </button>
  );
}
