// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Suppress act() warnings for tests - React 18 compatibility
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOMTestUtils.act is deprecated') ||
       args[0].includes('Warning: An update to') ||
       args[0].includes('was not wrapped in act'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Mock IntersectionObserver
(global as any).IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock ResizeObserver
(global as any).ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock MSAL and crypto for testing environment
global.crypto = {
  getRandomValues: (arr: any) => {
    for (let i = 0; i < arr.length; i++) {
      arr[i] = Math.floor(Math.random() * 256);
    }
    return arr;
  },
  subtle: {
    digest: jest.fn(),
    importKey: jest.fn(),
    sign: jest.fn(),
    verify: jest.fn()
  } as any
} as any;

// Mock TextEncoder/TextDecoder for Node.js test environment
if (typeof TextEncoder === 'undefined') {
  global.TextEncoder = require('util').TextEncoder;
}
if (typeof TextDecoder === 'undefined') {
  global.TextDecoder = require('util').TextDecoder;
}

// Mock Web Speech API
(global as any).SpeechRecognition = class MockSpeechRecognition {
  continuous = false;
  interimResults = false;
  lang = 'en-US';
  
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
  start = jest.fn();
  stop = jest.fn();
  abort = jest.fn();
};

(global as any).webkitSpeechRecognition = (global as any).SpeechRecognition;

// Mock SpeechSynthesis API
(global as any).speechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  getVoices: jest.fn(() => []),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

(global as any).SpeechSynthesisUtterance = class MockSpeechSynthesisUtterance {
  text = '';
  lang = 'en-US';
  voice = null;
  volume = 1;
  rate = 1;
  pitch = 1;
  
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
};

// Mock MSAL dependencies
jest.mock('@azure/msal-browser', () => ({
  PublicClientApplication: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(undefined),
    loginPopup: jest.fn().mockResolvedValue({ account: { username: 'test@test.com' } }),
    logout: jest.fn().mockResolvedValue(undefined),
    getAllAccounts: jest.fn().mockReturnValue([]),
    getAccountByUsername: jest.fn().mockReturnValue(null),
    acquireTokenSilent: jest.fn().mockResolvedValue({ accessToken: 'mock-token' }),
    addEventCallback: jest.fn(),
    removeEventCallback: jest.fn()
  })),
  LogLevel: {
    Error: 0,
    Warning: 1,
    Info: 2,
    Verbose: 3,
    Trace: 4
  },
  EventType: {
    LOGIN_SUCCESS: 'msal:loginSuccess',
    LOGIN_FAILURE: 'msal:loginFailure',
    LOGOUT_SUCCESS: 'msal:logoutSuccess'
  },
  InteractionType: {
    POPUP: 'popup',
    REDIRECT: 'redirect'
  }
}));

// Mock MSAL React context
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn(() => ({
    instance: {
      initialize: jest.fn().mockResolvedValue(undefined),
      loginPopup: jest.fn().mockResolvedValue({ account: { username: 'test@test.com' } }),
      logout: jest.fn().mockResolvedValue(undefined),
      getAllAccounts: jest.fn().mockReturnValue([]),
      getAccountByUsername: jest.fn().mockReturnValue(null),
      acquireTokenSilent: jest.fn().mockResolvedValue({ accessToken: 'mock-token' }),
      addEventCallback: jest.fn(),
      removeEventCallback: jest.fn()
    },
    accounts: [],
    inProgress: 'None'
  })),
  useAccount: jest.fn(() => null),
  useIsAuthenticated: jest.fn(() => false),
  MsalProvider: ({ children }: { children: React.ReactNode }) => children,
  AuthenticatedTemplate: ({ children }: { children: React.ReactNode }) => null,
  UnauthenticatedTemplate: ({ children }: { children: React.ReactNode }) => children
}));
