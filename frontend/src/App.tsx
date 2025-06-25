import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/spiritual-theme.css';
import SpiritualGuidanceInterface from './components/SpiritualGuidanceInterface';
import AuthenticationWrapper, { LoginButton } from './components/AuthenticationWrapper';
import LanguageSelector from './components/LanguageSelector';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { ABTestingProvider } from './contexts/ABTestingContext';

// App content component that uses language context
const AppContent: React.FC = () => {
  const { t } = useLanguage();

  return (
    <Router>
      <div className="App" style={{ minHeight: '100vh' }}>
        {/* Cultural header with Om symbol */}
        <header className="flex items-center justify-between p-4 bg-white/90 backdrop-blur-sm shadow-md">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🕉️</span>
            <h1 className="heading-3 mb-0 text-saffron-primary">विमर्श Vimarsh</h1>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <LoginButton />
          </div>
        </header>

        {/* Main content area */}
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<SpiritualGuidanceInterface />} />
            <Route path="/guidance" element={<SpiritualGuidanceInterface />} />
          </Routes>
        </main>

        {/* Cultural footer */}
        <footer className="mt-auto p-6 text-center bg-white/50 backdrop-blur-sm">
          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="text-lg">🪷</span>
            <p className="caption-text">
              {t('guidedByWisdom')}
            </p>
            <span className="text-lg">🪷</span>
          </div>
          <p className="caption-text text-neutral-500">
            {t('karmaQuote')}
          </p>
        </footer>
      </div>
    </Router>
  );
};

function App() {
  return (
    <LanguageProvider defaultLanguage="English">
      <AuthenticationWrapper>
        <AnalyticsProvider
          enableAnalytics={true}
          enableBehaviorTracking={true}
          anonymizeData={true}
          sessionTimeout={30}
          batchSize={10}
        >
          <ABTestingProvider>
            <AppContent />
          </ABTestingProvider>
        </AnalyticsProvider>
      </AuthenticationWrapper>
    </LanguageProvider>
  );
}

export default App;
