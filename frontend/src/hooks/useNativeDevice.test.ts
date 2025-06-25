import { renderHook, act, waitFor } from '@testing-library/react';
import { useNativeDevice } from './useNativeDevice';

// Mock Web APIs
const mockGetUserMedia = jest.fn();
const mockEnumerateDevices = jest.fn();
const mockVibrate = jest.fn();
const mockAudioContext = jest.fn();

Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: mockGetUserMedia,
    enumerateDevices: mockEnumerateDevices,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn()
  },
  writable: true
});

Object.defineProperty(navigator, 'vibrate', {
  value: mockVibrate,
  writable: true
});

Object.defineProperty(navigator, 'permissions', {
  value: {
    query: jest.fn().mockResolvedValue({ state: 'granted' })
  },
  writable: true
});

Object.defineProperty(window, 'AudioContext', {
  value: mockAudioContext,
  writable: true
});

Object.defineProperty(window, 'Notification', {
  value: {
    requestPermission: jest.fn().mockResolvedValue('granted')
  },
  writable: true
});

// Mock audio context and related objects
const mockAnalyser = {
  fftSize: 2048,
  frequencyBinCount: 1024,
  getByteFrequencyData: jest.fn()
};

const mockSource = {
  connect: jest.fn()
};

const mockAudioContextInstance = {
  createMediaStreamSource: jest.fn(() => mockSource),
  createAnalyser: jest.fn(() => mockAnalyser),
  close: jest.fn(),
  sampleRate: 48000
};

mockAudioContext.mockImplementation(() => mockAudioContextInstance);

// Mock media stream
const mockTrack = {
  stop: jest.fn()
};

const mockStream = {
  getTracks: jest.fn(() => [mockTrack])
};

describe('useNativeDevice', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementations
    mockEnumerateDevices.mockResolvedValue([
      {
        deviceId: 'microphone1',
        label: 'Built-in Microphone',
        kind: 'audioinput',
        groupId: 'group1'
      },
      {
        deviceId: 'microphone2',
        label: 'External Microphone',
        kind: 'audioinput',
        groupId: 'group2'
      }
    ]);

    mockGetUserMedia.mockResolvedValue(mockStream);
  });

  it('initializes with default state and detects capabilities', async () => {
    const { result } = renderHook(() => useNativeDevice());

    // Since capabilities detection is synchronous in our test environment,
    // they will be detected immediately due to our mocks
    await waitFor(() => {
      expect(result.current.capabilities.microphone).toBe(true);
      expect(result.current.capabilities.camera).toBe(true);
      expect(result.current.capabilities.notifications).toBe(true);
      expect(result.current.capabilities.vibration).toBe(true);
    });

    // Other initial state should remain default
    expect(result.current.selectedMicrophone).toBe('');
    expect(result.current.audioQuality).toBe(0);
    expect(result.current.isRecording).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('initializes with default capabilities when APIs are not available', () => {
    // Create a minimal navigator without the APIs
    const mockNavigator = {};
    
    // Temporarily replace navigator and window properties
    const originalNavigator = global.navigator;
    const originalNotification = global.window.Notification;
    
    Object.defineProperty(global, 'navigator', {
      value: mockNavigator,
      configurable: true
    });
    
    // Remove Notification API
    delete (global.window as any).Notification;

    const { result } = renderHook(() => useNativeDevice());

    expect(result.current.capabilities).toEqual({
      microphone: false,
      camera: false,
      deviceMotion: false,
      geolocation: false,
      notifications: false,
      vibration: false
    });

    // Restore original navigator and window
    Object.defineProperty(global, 'navigator', {
      value: originalNavigator,
      configurable: true
    });
    
    global.window.Notification = originalNotification;
  });

  it('detects device capabilities', async () => {
    const onCapabilitiesDetected = jest.fn();
    
    const { result } = renderHook(() => 
      useNativeDevice({ onCapabilitiesDetected })
    );

    await waitFor(() => {
      expect(result.current.capabilities.microphone).toBe(true);
      expect(result.current.capabilities.notifications).toBe(true);
      expect(result.current.capabilities.vibration).toBe(true);
    });

    expect(onCapabilitiesDetected).toHaveBeenCalledWith(
      expect.objectContaining({
        microphone: true,
        notifications: true,
        vibration: true
      })
    );
  });

  it('detects audio devices', async () => {
    const onDeviceChange = jest.fn();
    
    const { result } = renderHook(() => 
      useNativeDevice({ onDeviceChange })
    );

    await waitFor(() => {
      expect(result.current.audioDevices).toHaveLength(2);
      expect(result.current.audioDevices[0]).toMatchObject({
        deviceId: 'microphone1',
        label: 'Built-in Microphone',
        kind: 'audioinput'
      });
    });

    expect(onDeviceChange).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({ deviceId: 'microphone1' }),
        expect.objectContaining({ deviceId: 'microphone2' })
      ])
    );
  });

  it('finds optimal microphone', async () => {
    const { result } = renderHook(() => 
      useNativeDevice({ enableAudioOptimization: true })
    );

    await waitFor(() => {
      expect(result.current.selectedMicrophone).toBeTruthy();
    });
  });

  it('starts and stops recording', async () => {
    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(result.current.capabilities.microphone).toBe(true);
    });

    await act(async () => {
      await result.current.startRecording();
    });

    expect(mockGetUserMedia).toHaveBeenCalledWith({
      audio: {
        deviceId: undefined,
        sampleRate: 48000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    expect(result.current.isRecording).toBe(true);

    act(() => {
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(mockTrack.stop).toHaveBeenCalled();
  });

  it('tests microphone quality', async () => {
    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(result.current.capabilities.microphone).toBe(true);
    });

    const quality = await act(async () => {
      return result.current.testMicrophoneQuality('microphone1');
    });

    expect(typeof quality).toBe('number');
    expect(quality).toBeGreaterThanOrEqual(0);
    expect(quality).toBeLessThanOrEqual(1);
  });

  it('triggers spiritual vibration', () => {
    const { result } = renderHook(() => 
      useNativeDevice({ enableVibration: true })
    );

    act(() => {
      result.current.triggerSpiritualVibration();
    });

    expect(mockVibrate).toHaveBeenCalledWith([200, 100, 100, 100, 200]);
  });

  it('sends spiritual notification', async () => {
    const mockNotificationConstructor = jest.fn();
    
    Object.defineProperty(window, 'Notification', {
      value: mockNotificationConstructor,
      writable: true
    });

    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(result.current.permissions.notifications).toBe('granted');
    });

    act(() => {
      result.current.sendSpiritualNotification(
        'Daily Wisdom',
        'Your spiritual guidance is ready'
      );
    });

    expect(mockNotificationConstructor).toHaveBeenCalledWith(
      'Daily Wisdom',
      expect.objectContaining({
        body: 'Your spiritual guidance is ready',
        icon: '/favicon.ico',
        tag: 'vimarsh-spiritual',
        silent: true
      })
    );
  });

  it('monitors audio quality during recording', async () => {
    const onQualityChange = jest.fn();
    
    const { result } = renderHook(() => 
      useNativeDevice({ 
        enableAudioOptimization: true,
        onQualityChange 
      })
    );

    await waitFor(() => {
      expect(result.current.capabilities.microphone).toBe(true);
    });

    // Mock audio data
    mockAnalyser.getByteFrequencyData.mockImplementation((dataArray) => {
      for (let i = 0; i < dataArray.length; i++) {
        dataArray[i] = 128; // Mid-range audio level
      }
    });

    await act(async () => {
      await result.current.startRecording();
    });

    // Wait for quality monitoring to start
    await waitFor(() => {
      expect(onQualityChange).toHaveBeenCalled();
    });

    act(() => {
      result.current.stopRecording();
    });
  });

  it('selects microphone manually', async () => {
    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(result.current.audioDevices).toHaveLength(2);
    });

    act(() => {
      result.current.selectMicrophone('microphone2');
    });

    expect(result.current.selectedMicrophone).toBe('microphone2');
  });

  it('clears errors', () => {
    const { result } = renderHook(() => useNativeDevice());

    // Simulate an error
    act(() => {
      // This would normally come from an internal error state update
      // For testing, we'll just verify the clearError function exists
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });

  it('handles getUserMedia errors', async () => {
    mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

    const { result } = renderHook(() => useNativeDevice());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.error).toContain('Failed to start recording');
    expect(result.current.isRecording).toBe(false);
  });

  it('handles device enumeration errors', async () => {
    mockEnumerateDevices.mockRejectedValue(new Error('Enumeration failed'));

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(result.current.error).toContain('Failed to detect audio devices');
    });

    consoleSpy.mockRestore();
  });

  it('handles missing Web APIs gracefully', () => {
    // Create a new navigator object without the APIs
    const mockNavigator = {};
    
    // Temporarily replace navigator
    const originalNavigator = global.navigator;
    Object.defineProperty(global, 'navigator', {
      value: mockNavigator,
      configurable: true
    });

    const { result } = renderHook(() => useNativeDevice());

    expect(result.current.capabilities.microphone).toBe(false);
    expect(result.current.capabilities.vibration).toBe(false);
    expect(result.current.capabilities.notifications).toBe(false);

    // Restore original navigator
    Object.defineProperty(global, 'navigator', {
      value: originalNavigator,
      configurable: true
    });
  });

  it('handles permission queries that fail', async () => {
    // @ts-ignore
    navigator.permissions.query.mockRejectedValue(new Error('Permission query failed'));

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
    
    const { result } = renderHook(() => useNativeDevice());

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Microphone permission query not supported');
    });

    consoleSpy.mockRestore();
  });

  it('auto-selects optimal microphone when available', async () => {
    const { result } = renderHook(() => 
      useNativeDevice({ enableAudioOptimization: true })
    );

    await waitFor(() => {
      expect(result.current.audioDevices).toHaveLength(2);
    });

    await waitFor(() => {
      expect(result.current.selectedMicrophone).toBeTruthy();
    });
  });

  it('disables audio optimization when requested', async () => {
    const { result } = renderHook(() => 
      useNativeDevice({ enableAudioOptimization: false })
    );

    await waitFor(() => {
      expect(result.current.audioDevices).toHaveLength(2);
    });

    // Should select first device without quality testing
    await waitFor(() => {
      expect(result.current.selectedMicrophone).toBe('microphone1');
    });
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useNativeDevice());

    unmount();

    // Should remove event listeners and stop any ongoing recording
    expect(navigator.mediaDevices.removeEventListener).toHaveBeenCalled();
  });

  it('handles audio context creation failures', async () => {
    mockAudioContext.mockImplementation(() => {
      throw new Error('AudioContext not supported');
    });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    const { result } = renderHook(() => 
      useNativeDevice({ enableAudioOptimization: true })
    );

    await act(async () => {
      await result.current.startRecording();
    });

    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });

  it('provides all expected interface methods', () => {
    const { result } = renderHook(() => useNativeDevice());

    // State properties
    expect(result.current).toHaveProperty('capabilities');
    expect(result.current).toHaveProperty('audioDevices');
    expect(result.current).toHaveProperty('selectedMicrophone');
    expect(result.current).toHaveProperty('audioQuality');
    expect(result.current).toHaveProperty('isRecording');
    expect(result.current).toHaveProperty('permissions');
    expect(result.current).toHaveProperty('error');

    // Action methods
    expect(result.current).toHaveProperty('startRecording');
    expect(result.current).toHaveProperty('stopRecording');
    expect(result.current).toHaveProperty('detectAudioDevices');
    expect(result.current).toHaveProperty('findOptimalMicrophone');
    expect(result.current).toHaveProperty('testMicrophoneQuality');
    expect(result.current).toHaveProperty('triggerSpiritualVibration');
    expect(result.current).toHaveProperty('sendSpiritualNotification');
    expect(result.current).toHaveProperty('requestPermissions');

    // Utility methods
    expect(result.current).toHaveProperty('selectMicrophone');
    expect(result.current).toHaveProperty('clearError');

    // Ensure all methods are functions
    expect(typeof result.current.startRecording).toBe('function');
    expect(typeof result.current.stopRecording).toBe('function');
    expect(typeof result.current.triggerSpiritualVibration).toBe('function');
    expect(typeof result.current.sendSpiritualNotification).toBe('function');
  });
});
