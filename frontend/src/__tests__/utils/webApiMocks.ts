// Comprehensive Web API mocks for testing

// MediaDevices mock
export const mockMediaDevices = {
  enumerateDevices: jest.fn().mockResolvedValue([
    {
      deviceId: 'default',
      kind: 'audioinput',
      label: 'Default Microphone',
      groupId: 'group1'
    },
    {
      deviceId: 'mic2',
      kind: 'audioinput', 
      label: 'External Microphone',
      groupId: 'group2'
    }
  ]),
  getUserMedia: jest.fn().mockResolvedValue({
    getTracks: () => [
      {
        kind: 'audio',
        stop: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn()
      }
    ],
    getAudioTracks: () => [
      {
        kind: 'audio',
        stop: jest.fn()
      }
    ]
  }),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

// AudioContext mock
export const mockAudioContext = {
  createAnalyser: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    fftSize: 2048,
    frequencyBinCount: 1024,
    getByteFrequencyData: jest.fn(),
    getByteTimeDomainData: jest.fn()
  })),
  createMediaStreamSource: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn()
  })),
  close: jest.fn(),
  state: 'running',
  sampleRate: 44100
};

// Navigator permissions mock
export const mockPermissions = {
  query: jest.fn().mockResolvedValue({
    state: 'granted',
    addEventListener: jest.fn(),
    removeEventListener: jest.fn()
  })
};

// Setup function to apply all mocks
export const setupWebApiMocks = () => {
  // Navigator mocks
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: mockMediaDevices,
    writable: true,
    configurable: true
  });
  
  Object.defineProperty(global.navigator, 'permissions', {
    value: mockPermissions,
    writable: true,
    configurable: true
  });
  
  Object.defineProperty(global.navigator, 'vibrate', {
    value: jest.fn(),
    writable: true,
    configurable: true
  });
  
  // AudioContext mock
  (global as any).AudioContext = jest.fn(() => mockAudioContext);
  (global as any).webkitAudioContext = jest.fn(() => mockAudioContext);
  
  // Window event listeners
  const originalAddEventListener = window.addEventListener;
  window.addEventListener = jest.fn((event, handler) => {
    if (event === 'deviceorientation') {
      // Simulate device orientation event
      setTimeout(() => {
        if (typeof handler === 'function') {
          handler({
            alpha: 0,
            beta: 0,
            gamma: 0,
            absolute: false
          } as DeviceOrientationEvent);
        }
      }, 100);
    }
    return originalAddEventListener.call(window, event, handler);
  });
};

// Cleanup function
export const cleanupWebApiMocks = () => {
  jest.restoreAllMocks();
};
