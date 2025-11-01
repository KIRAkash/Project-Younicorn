import React from 'react';
import { Sparkles } from 'lucide-react';
import { useBeacon, SectionContext } from './beacon-context';
import { cn } from '@/utils';

interface BeaconSectionIconProps {
  sectionId: string;
  sectionTitle: string;
  sectionType: 'team' | 'market' | 'product' | 'competition' | 'synthesis' | 'risks' | 'opportunities';
  sectionData: any;
  className?: string;
}

export function BeaconSectionIcon({
  sectionId,
  sectionTitle,
  sectionType,
  sectionData,
  className
}: BeaconSectionIconProps) {
  const { openBeacon } = useBeacon();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const context: SectionContext = {
      sectionId,
      sectionTitle,
      sectionType,
      sectionData
    };
    
    openBeacon(context);
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        "beacon-section-icon",
        "inline-flex items-center justify-center",
        "w-5 h-5 ml-2",
        "text-purple-500 hover:text-purple-600 dark:text-purple-400 dark:hover:text-purple-300",
        "transition-all duration-200",
        "hover:scale-110",
        "focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2",
        "rounded-full",
        "group",
        className
      )}
      aria-label={`Chat with Beacon about ${sectionTitle}`}
      title={`Chat with Beacon about ${sectionTitle}`}
    >
      <Sparkles 
        size={16} 
        className="animate-pulse group-hover:animate-none" 
        strokeWidth={2.5}
      />
    </button>
  );
}
