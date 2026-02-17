import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAdmin } from './AdminProviderContext';
import { usePersonality } from './PersonalityContext';

interface AppLoadingContextType {
  isInitializing: boolean;
  adminReady: boolean;
  personalitiesReady: boolean;
  allReady: boolean;
}

const AppLoadingContext = createContext<AppLoadingContextType | undefined>(undefined);

export const useAppLoading = () => {
  const context = useContext(AppLoadingContext);
  if (context === undefined) {
    throw new Error('useAppLoading must be used within an AppLoadingProvider');
  }
  return context;
};

interface AppLoadingProviderProps {
  children: ReactNode;
}

export const AppLoadingProvider: React.FC<AppLoadingProviderProps> = ({ children }) => {
  const { user: adminUser, loading: adminLoading } = useAdmin();
  const { availablePersonalities, personalityLoading } = usePersonality();
  
  const [isInitializing, setIsInitializing] = useState(true);

  // Track readiness state
  // Admin is considered ready if not loading (regardless of whether user is admin)
  // This prevents blocking the app for non-admin users
  const adminReady = !adminLoading;
  const personalitiesReady = !personalityLoading && availablePersonalities.length > 0;
  const allReady = adminReady && personalitiesReady;

  useEffect(() => {
    if (allReady && isInitializing) {
      if (process.env.NODE_ENV === 'development') {
        console.log('🎉 AppLoading: All contexts ready, app fully initialized');
      }
      setIsInitializing(false);
    }
  }, [allReady, isInitializing]);

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 AppLoading status:', {
        adminLoading,
        personalityLoading,
        adminReady,
        personalitiesReady,
        allReady,
        isInitializing
      });
    }
  }, [adminLoading, personalityLoading, adminReady, personalitiesReady, allReady, isInitializing]);

  const value: AppLoadingContextType = {
    isInitializing,
    adminReady,
    personalitiesReady,
    allReady
  };

  return (
    <AppLoadingContext.Provider value={value}>
      {children}
    </AppLoadingContext.Provider>
  );
};
