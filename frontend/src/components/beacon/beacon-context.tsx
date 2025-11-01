import React, { createContext, useContext, useState, useCallback } from 'react';

export interface SectionContext {
  sectionId: string;
  sectionTitle: string;
  sectionType: 'team' | 'market' | 'product' | 'competition' | 'synthesis' | 'risks' | 'opportunities';
  sectionData: any;
  subsection?: string;  // Specific subsection like 'Market Dynamics'
}

interface BeaconContextType {
  isOpen: boolean;
  isMinimized: boolean;
  contextItems: SectionContext[];  // Multiple context items
  openBeacon: (context?: SectionContext) => void;
  closeBeacon: () => void;
  minimizeBeacon: () => void;
  restoreBeacon: () => void;
  addContext: (context: SectionContext) => void;
  removeContext: (sectionId: string) => void;
  clearAllContext: () => void;
}

const BeaconContext = createContext<BeaconContextType | undefined>(undefined);

export function BeaconProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [contextItems, setContextItems] = useState<SectionContext[]>([]);

  const openBeacon = useCallback((context?: SectionContext) => {
    setIsOpen(true);
    setIsMinimized(false);
    if (context) {
      // Add context if not already present
      setContextItems(prev => {
        const exists = prev.some(item => item.sectionId === context.sectionId);
        return exists ? prev : [...prev, context];
      });
    }
  }, []);

  const closeBeacon = useCallback(() => {
    setIsOpen(false);
    setIsMinimized(false);
  }, []);

  const minimizeBeacon = useCallback(() => {
    setIsMinimized(true);
  }, []);

  const restoreBeacon = useCallback(() => {
    setIsOpen(true);
    setIsMinimized(false);
  }, []);

  const addContext = useCallback((context: SectionContext) => {
    setContextItems(prev => {
      const exists = prev.some(item => item.sectionId === context.sectionId);
      return exists ? prev : [...prev, context];
    });
  }, []);

  const removeContext = useCallback((sectionId: string) => {
    setContextItems(prev => prev.filter(item => item.sectionId !== sectionId));
  }, []);

  const clearAllContext = useCallback(() => {
    setContextItems([]);
  }, []);

  return (
    <BeaconContext.Provider
      value={{
        isOpen,
        isMinimized,
        contextItems,
        openBeacon,
        closeBeacon,
        minimizeBeacon,
        restoreBeacon,
        addContext,
        removeContext,
        clearAllContext,
      }}
    >
      {children}
    </BeaconContext.Provider>
  );
}

export function useBeacon() {
  const context = useContext(BeaconContext);
  if (context === undefined) {
    throw new Error('useBeacon must be used within a BeaconProvider');
  }
  return context;
}
