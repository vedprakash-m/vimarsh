// Language Context and Management System
// Provides global language state for the entire Vimarsh application

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Supported languages in Vimarsh
export type Language = 'English' | 'Hindi';
export type LanguageCode = 'en' | 'hi';

// Language configuration
export const languageConfig = {
  English: {
    code: 'en' as LanguageCode,
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
    direction: 'ltr' as 'ltr' | 'rtl',
    voiceCode: 'en-US',
    scriptureLanguage: 'English',
    culturalGreeting: 'Namaste'
  },
  Hindi: {
    code: 'hi' as LanguageCode,
    name: 'Hindi',
    nativeName: 'हिन्दी',
    flag: '🇮🇳',
    direction: 'ltr' as 'ltr' | 'rtl',
    voiceCode: 'hi-IN',
    scriptureLanguage: 'Sanskrit-Hindi',
    culturalGreeting: 'नमस्ते'
  }
} as const;

// Translations for UI elements
export const translations = {
  English: {
    // Authentication
    signIn: 'Sign In',
    signOut: 'Sign Out',
    greeting: 'Namaste',
    welcome: 'Welcome to Vimarsh',
    welcomeMessage: 'Connect with the divine wisdom of ancient scriptures. Please sign in to begin your spiritual journey.',
    
    // Navigation and UI
    spiritualGuidance: 'Spiritual Guidance',
    voiceInput: 'Voice Input',
    textInput: 'Text Input',
    send: 'Send',
    clear: 'Clear',
    listening: 'Listening...',
    processing: 'Processing your question...',
    
    // Voice Interface
    startListening: 'Start Voice Input',
    stopListening: 'Stop Listening',
    playResponse: 'Play Response',
    pauseResponse: 'Pause Response',
    voiceNotSupported: 'Voice recognition not supported in this browser',
    
    // Chat and Responses
    askQuestion: 'Ask your spiritual question...',
    citations: 'Sources',
    relatedVerses: 'Related Verses',
    moreFromThisSource: 'More from this source',
    
    // Spiritual Content
    bhagavadGita: 'Bhagavad Gita',
    mahabharata: 'Mahabharata',
    srimadBhagavatam: 'Srimad Bhagavatam',
    chapter: 'Chapter',
    verse: 'Verse',
    
    // Features
    conversationHistory: 'Conversation History',
    searchHistory: 'Search History',
    exportChat: 'Export Conversation',
    clearHistory: 'Clear History',
    
    // New Conversation History Features
    newConversation: 'New Conversation',
    new: 'New',
    searchConversations: 'Search conversations...',
    sessions: 'sessions',
    messages: 'messages',
    exportTxt: 'Export Text',
    exportJson: 'Export JSON',
    exporting: 'Exporting',
    noSearchResults: 'No conversations found',
    tryDifferentSearch: 'Try a different search term',
    noConversations: 'No conversations yet',
    startFirstConversation: 'Start your first spiritual conversation',
    exportSession: 'Export this conversation',
    deleteSession: 'Delete conversation',
    confirmDelete: 'Confirm Delete',
    deleteSessionWarning: 'This conversation will be permanently deleted. This action cannot be undone.',
    cancel: 'Cancel',
    delete: 'Delete',
    today: 'Today',
    yesterday: 'Yesterday',
    daysAgo: 'days ago',
    recentConversations: 'Recent Conversations',
    
    // Conversation Archive Features
    conversationArchive: 'Conversation Archive',
    advancedSearch: 'Advanced Search',
    language: 'Language',
    allLanguages: 'All Languages',
    dateRange: 'Date Range',
    allTime: 'All Time',
    thisWeek: 'This Week',
    thisMonth: 'This Month',
    thisYear: 'This Year',
    minimumMessages: 'Minimum Messages',
    conversationsFound: 'conversations found',
    selected: 'selected',
    selectAll: 'Select All',
    clearSelection: 'Clear Selection',
    exportSelected: 'Export Selected',
    matchingMessages: 'matching messages',
    you: 'You',
    lordKrishna: 'Lord Krishna',
    moreMatches: 'more matches',
    
    // Errors and States
    errorOccurred: 'An error occurred. Please try again.',
    networkError: 'Network connection issue. Please check your internet.',
    loadingWisdom: 'Loading divine wisdom...',
    noInternet: 'No internet connection detected.',
    
    // Footer and Legal
    guidedByWisdom: 'Guided by ancient wisdom, powered by modern technology',
    karmaQuote: 'You have the right to perform action, but not to the fruits of action',
    
    // Language Switching
    switchToHindi: 'Switch to Hindi',
    switchToEnglish: 'Switch to English',
    languageChanged: 'Language changed to English',
    
    // Responsive Design Features
    welcomeToVimarsh: 'Welcome to Vimarsh',
    pleaseSignIn: 'Please sign in to continue',
    hideHistory: 'Hide conversation history',
    showHistory: 'Show conversation history',
    hideArchive: 'Hide conversation archive',
    showArchive: 'Show conversation archive',
    startConversation: 'Start your spiritual journey by asking a question',
    lordKrishnaIsTyping: 'Lord Krishna is responding...',
    sending: 'Sending...',
    
    // Accessibility
    skipToMainContent: 'Skip to main content',
    spiritualGuidanceApp: 'Spiritual Guidance Application',
    conversationControls: 'Conversation controls',
    welcomeHeading: 'Welcome section',
    conversationMessages: 'Conversation messages',
    yourMessage: 'Your message',
    lordKrishnaMessage: 'Lord Krishna\'s message',
    lordKrishnaResponse: 'Lord Krishna\'s response',
    
    // Notification Settings
    notificationSettings: 'Notification Settings',
    enableNotifications: 'Enable Notifications',
    disableNotifications: 'Disable Notifications',
    notificationsDescription: 'Receive daily spiritual wisdom and meditation reminders',
    notificationPermissionDenied: 'Notification permission was denied. Please enable in browser settings.',
    notificationError: 'Failed to enable notifications. Please try again.',
    notificationsNotSupported: 'Notifications Not Supported',
    notificationsSupportDescription: 'Your browser doesn\'t support push notifications.',
    enabled: 'Enabled',
    disabled: 'Disabled',
    enable: 'Enable',
    enabling: 'Enabling...',
    close: 'Close',
    notificationTypes: 'Notification Types',
    dailyWisdom: 'Daily Wisdom',
    meditationReminders: 'Meditation Reminders',
    spiritualQuotes: 'Spiritual Quotes',
    teachings: 'Teachings',
    timingSettings: 'Timing Settings',
    preferredTime: 'Preferred Time',
    frequency: 'Frequency',
    daily: 'Daily',
    everyOtherDay: 'Every Other Day',
    weekly: 'Weekly',
    notificationLanguage: 'Notification Language',
    english: 'English',
    hindi: 'Hindi',
    testNotification: 'Test Notification',
    testNotificationDescription: 'Send a test notification to verify settings',
    sendTest: 'Send Test',
    testNotificationFailed: 'Failed to send test notification'
  },
  
  Hindi: {
    // Authentication
    signIn: 'साइन इन करें',
    signOut: 'साइन आउट',
    greeting: 'नमस्ते',
    welcome: 'विमर्श में आपका स्वागत है',
    welcomeMessage: 'प्राचीन शास्त्रों की दिव्य बुद्धि से जुड़ें। अपनी आध्यात्मिक यात्रा शुरू करने के लिए कृपया साइन इन करें।',
    
    // Navigation and UI
    spiritualGuidance: 'आध्यात्मिक मार्गदर्शन',
    voiceInput: 'आवाज़ इनपुट',
    textInput: 'टेक्स्ट इनपुट',
    send: 'भेजें',
    clear: 'साफ़ करें',
    listening: 'सुन रहे हैं...',
    processing: 'आपके प्रश्न पर विचार कर रहे हैं...',
    
    // Responsive Design Features
    welcomeToVimarsh: 'विमर्श में आपका स्वागत है',
    pleaseSignIn: 'जारी रखने के लिए कृपया साइन इन करें',
    hideHistory: 'वार्तालाप इतिहास छुपाएं',
    showHistory: 'वार्तालाप इतिहास दिखाएं',
    hideArchive: 'वार्तालाप संग्रह छुपाएं',
    showArchive: 'वार्तालाप संग्रह दिखाएं',
    startConversation: 'प्रश्न पूछकर अपनी आध्यात्मिक यात्रा शुरू करें',
    lordKrishnaIsTyping: 'भगवान कृष्ण उत्तर दे रहे हैं...',
    sending: 'भेज रहे हैं...',
    
    // Accessibility
    skipToMainContent: 'मुख्य सामग्री पर जाएं',
    spiritualGuidanceApp: 'आध्यात्मिक मार्गदर्शन अनुप्रयोग',
    conversationControls: 'वार्तालाप नियंत्रण',
    welcomeHeading: 'स्वागत अनुभाग',
    conversationMessages: 'वार्तालाप संदेश',
    yourMessage: 'आपका संदेश',
    lordKrishnaMessage: 'भगवान कृष्ण का संदेश',
    lordKrishnaResponse: 'भगवान कृष्ण का उत्तर',
    
    // Notification Settings
    notificationSettings: 'सूचना सेटिंग्स',
    enableNotifications: 'सूचनाएं चालू करें',
    disableNotifications: 'सूचनाएं बंद करें',
    notificationsDescription: 'दैनिक आध्यात्मिक ज्ञान और ध्यान अनुस्मारक प्राप्त करें',
    notificationPermissionDenied: 'सूचना अनुमति अस्वीकार कर दी गई। कृपया ब्राउज़र सेटिंग्स में चालू करें।',
    notificationError: 'सूचनाएं चालू करने में विफल। कृपया पुनः प्रयास करें।',
    notificationsNotSupported: 'सूचनाएं समर्थित नहीं',
    notificationsSupportDescription: 'आपका ब्राउज़र पुश सूचनाओं का समर्थन नहीं करता।',
    enabled: 'चालू',
    disabled: 'बंद',
    enable: 'चालू करें',
    enabling: 'चालू कर रहे हैं...',
    close: 'बंद करें',
    notificationTypes: 'सूचना प्रकार',
    dailyWisdom: 'दैनिक ज्ञान',
    meditationReminders: 'ध्यान अनुस्मारक',
    spiritualQuotes: 'आध्यात्मिक उद्धरण',
    teachings: 'शिक्षाएं',
    timingSettings: 'समय सेटिंग्स',
    preferredTime: 'पसंदीदा समय',
    frequency: 'आवृत्ति',
    daily: 'दैनिक',
    everyOtherDay: 'हर दूसरे दिन',
    weekly: 'साप्ताहिक',
    notificationLanguage: 'सूचना भाषा',
    english: 'अंग्रेजी',
    hindi: 'हिंदी',
    testNotification: 'परीक्षण सूचना',
    testNotificationDescription: 'सेटिंग्स सत्यापित करने के लिए परीक्षण सूचना भेजें',
    sendTest: 'परीक्षण भेजें',
    testNotificationFailed: 'परीक्षण सूचना भेजने में विफल',
    
    // Voice Interface
    startListening: 'आवाज़ सुनना शुरू करें',
    stopListening: 'आवाज़ सुनना बंद करें',
    playResponse: 'उत्तर सुनें',
    pauseResponse: 'रोकें',
    voiceNotSupported: 'इस ब्राउज़र में आवाज़ पहचान समर्थित नहीं है',
    
    // Chat and Responses
    askQuestion: 'अपना आध्यात्मिक प्रश्न पूछें...',
    citations: 'स्रोत',
    relatedVerses: 'संबंधित श्लोक',
    moreFromThisSource: 'इस स्रोत से और',
    
    // Spiritual Content
    bhagavadGita: 'भगवद्गीता',
    mahabharata: 'महाभारत',
    srimadBhagavatam: 'श्रीमद्भागवतम्',
    chapter: 'अध्याय',
    verse: 'श्लोक',
    
    // Features
    conversationHistory: 'बातचीत का इतिहास',
    searchHistory: 'खोज इतिहास',
    exportChat: 'बातचीत निर्यात करें',
    clearHistory: 'इतिहास साफ़ करें',
    
    // New Conversation History Features
    newConversation: 'नया वार्तालाप',
    new: 'नया',
    searchConversations: 'वार्तालाप खोजें...',
    sessions: 'सत्र',
    messages: 'संदेश',
    exportTxt: 'पाठ निर्यात करें',
    exportJson: 'JSON निर्यात करें',
    exporting: 'निर्यात कर रहे हैं',
    noSearchResults: 'कोई वार्तालाप नहीं मिला',
    tryDifferentSearch: 'अलग खोज शब्द आज़माएं',
    noConversations: 'अभी तक कोई वार्तालाप नहीं',
    startFirstConversation: 'अपना पहला आध्यात्मिक वार्तालाप शुरू करें',
    exportSession: 'इस वार्तालाप को निर्यात करें',
    deleteSession: 'वार्तालाप हटाएं',
    confirmDelete: 'हटाने की पुष्टि करें',
    deleteSessionWarning: 'यह वार्तालाप स्थायी रूप से हटा दिया जाएगा। यह क्रिया पूर्ववत नहीं की जा सकती।',
    cancel: 'रद्द करें',
    delete: 'हटाएं',
    today: 'आज',
    yesterday: 'कल',
    daysAgo: 'दिन पहले',
    recentConversations: 'हाल की बातचीत',
    
    // Conversation Archive Features
    conversationArchive: 'बातचीत संग्रह',
    advancedSearch: 'उन्नत खोज',
    language: 'भाषा',
    allLanguages: 'सभी भाषाएँ',
    dateRange: 'दिनांक सीमा',
    allTime: 'सभी समय',
    thisWeek: 'इस सप्ताह',
    thisMonth: 'इस महीने',
    thisYear: 'इस वर्ष',
    minimumMessages: 'न्यूनतम संदेश',
    conversationsFound: 'बातचीत मिली',
    selected: 'चुना गया',
    selectAll: 'सभी चुनें',
    clearSelection: 'चयन साफ़ करें',
    exportSelected: 'चयनित निर्यात करें',
    matchingMessages: 'मेल खाते संदेश',
    you: 'आप',
    lordKrishna: 'भगवान कृष्ण',
    moreMatches: 'और मैच',
    
    // Errors and States
    errorOccurred: 'एक त्रुटि हुई। कृपया पुनः प्रयास करें।',
    networkError: 'नेटवर्क कनेक्शन की समस्या। कृपया अपना इंटरनेट जांचें।',
    loadingWisdom: 'दिव्य ज्ञान लोड कर रहे हैं...',
    noInternet: 'इंटरनेट कनेक्शन नहीं मिला।',
    
    // Footer and Legal
    guidedByWisdom: 'प्राचीन ज्ञान द्वारा निर्देशित, आधुनिक तकनीक द्वारा संचालित',
    karmaQuote: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
    
    // Language Switching
    switchToHindi: 'हिन्दी में बदलें',
    switchToEnglish: 'अंग्रेजी में बदलें',
    languageChanged: 'भाषा हिन्दी में बदल गई'
  }
} as const;

// Language context interface
interface LanguageContextType {
  currentLanguage: Language;
  currentLanguageConfig: typeof languageConfig[Language];
  translations: typeof translations[Language];
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
  t: (key: keyof typeof translations[Language]) => string;
  isRTL: boolean;
}

// Create language context
const LanguageContext = createContext<LanguageContextType | null>(null);

// Custom hook to use language context
export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language provider props
interface LanguageProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

// Language provider component
export const LanguageProvider: React.FC<LanguageProviderProps> = ({ 
  children, 
  defaultLanguage = 'English' 
}) => {
  const [currentLanguage, setCurrentLanguage] = useState<Language>(() => {
    // Try to get saved language from localStorage
    const saved = localStorage.getItem('vimarsh_language');
    if (saved && (saved === 'English' || saved === 'Hindi')) {
      return saved as Language;
    }
    
    // Try to detect user's browser language
    const browserLang = navigator.language;
    if (browserLang.startsWith('hi')) {
      return 'Hindi';
    }
    
    return defaultLanguage;
  });

  // Update document language and direction when language changes
  useEffect(() => {
    const config = languageConfig[currentLanguage];
    document.documentElement.lang = config.code;
    document.documentElement.dir = config.direction;
    
    // Save to localStorage
    localStorage.setItem('vimarsh_language', currentLanguage);
    
    // Update page title based on language
    document.title = currentLanguage === 'English' 
      ? 'Vimarsh - Spiritual AI Guidance'
      : 'विमर्श - आध्यात्मिक AI मार्गदर्शन';
      
    console.log(`🌍 Language changed to ${currentLanguage} (${config.code})`);
  }, [currentLanguage]);

  // Set language function
  const setLanguage = (language: Language) => {
    setCurrentLanguage(language);
  };

  // Toggle between English and Hindi
  const toggleLanguage = () => {
    setCurrentLanguage(prev => prev === 'English' ? 'Hindi' : 'English');
  };

  // Translation function
  const t = (key: keyof typeof translations[Language]): string => {
    return translations[currentLanguage][key] || key;
  };

  // Current language configuration
  const currentLanguageConfig = languageConfig[currentLanguage];
  const currentTranslations = translations[currentLanguage];
  const isRTL = currentLanguageConfig.direction === 'rtl';

  const contextValue: LanguageContextType = {
    currentLanguage,
    currentLanguageConfig,
    translations: currentTranslations,
    setLanguage,
    toggleLanguage,
    t,
    isRTL
  };

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
};

// Export language utilities
export const getLanguageCode = (language: Language): LanguageCode => {
  return languageConfig[language].code;
};

export const getLanguageFromCode = (code: LanguageCode): Language => {
  return code === 'hi' ? 'Hindi' : 'English';
};

export const getSupportedLanguages = (): Language[] => {
  return Object.keys(languageConfig) as Language[];
};

// Export for easy import
export default LanguageProvider;
