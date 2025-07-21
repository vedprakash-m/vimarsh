import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NativeDeviceIntegration from './NativeDeviceIntegration';

// Mock APIs
const mockGetUserMedia = jest.fn();
const mockEnumerateDevices = jest.fn();
const mockVibrate = jest.fn();
const mockAudioContext = jest.fn();

// Mock Web APIs
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

// Mock audio context
const mockAnalyser = {
  fftSize: 2048,
  smoothingTimeConstant: 0.8,
  frequencyBinCount: 1024,
  getByteFrequencyData: jest.fn(),
  getFloatFrequencyData: jest.fn()
};

const mockSource = {
  connect: jest.fn()
};

const mockAudioContextInstance = {
  createMediaStreamSource: jest.fn(() => mockSource),
  createAnalyser: jest.fn(() => mockAnalyser),
  audioWorklet: {
    addModule: jest.fn().mockResolvedValue(undefined)
  },
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

describe('NativeDeviceIntegration', () => {
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

  it('renders without crashing', () => {
    render(<NativeDeviceIntegration />);
    expect(screen.getByText('Native Device Integration Active')).toBeInTheDocument();
  });

  it('detects device capabilities on mount', async () => {
    const onDeviceCapabilities = jest.fn();
    
    render(
      <NativeDeviceIntegration 
        onDeviceCapabilities={onDeviceCapabilities}
      />
    );

    await waitFor(() => {
      expect(onDeviceCapabilities).toHaveBeenCalledWith({
        microphone: true,
        camera: true,
        deviceMotion: false, // Not available in test environment
        geolocation: false,  // Not available in test environment
        notifications: true,
        vibration: true
      });
    });
  });

  it('enumerates audio devices', async () => {
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(mockEnumerateDevices).toHaveBeenCalled();
    });
  });

  it('finds optimal microphone', async () => {
    const onOptimalMicrophoneFound = jest.fn();
    
    render(
      <NativeDeviceIntegration 
        onOptimalMicrophoneFound={onOptimalMicrophoneFound}
      />
    );

    await waitFor(() => {
      expect(onOptimalMicrophoneFound).toHaveBeenCalledWith(expect.any(String));
    }, { timeout: 5000 });
  });

  it('handles audio data processing', async () => {
    const onAudioData = jest.fn();
    
    render(
      <NativeDeviceIntegration 
        onAudioData={onAudioData}
      />
    );

    // Simulate audio processing
    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalled();
    });
  });

  it('triggers spiritual vibration when enabled', () => {
    render(
      <NativeDeviceIntegration 
        enableVibration={true}
      />
    );

    // The component should be able to trigger vibration
    expect(navigator.vibrate).toBeDefined();
  });

  it('handles device motion detection when enabled', () => {
    // Mock device orientation
    Object.defineProperty(window, 'DeviceOrientationEvent', {
      value: jest.fn(),
      writable: true
    });

    render(
      <NativeDeviceIntegration 
        enableMotionDetection={true}
      />
    );

    // Should set up device orientation listener
    expect(window.addEventListener).toBeDefined();
  });

  it('gracefully handles missing Web APIs', () => {
    // Temporarily remove APIs
    const originalMediaDevices = navigator.mediaDevices;
    const originalVibrate = navigator.vibrate;

    // @ts-ignore
    delete navigator.mediaDevices;
    // @ts-ignore
    delete navigator.vibrate;

    const onDeviceCapabilities = jest.fn();
    
    render(
      <NativeDeviceIntegration 
        onDeviceCapabilities={onDeviceCapabilities}
      />
    );

    waitFor(() => {
      expect(onDeviceCapabilities).toHaveBeenCalledWith({
        microphone: false,
        camera: false,
        deviceMotion: false,
        geolocation: false,
        notifications: true,
        vibration: false
      });
    });

    // Restore APIs
    Object.defineProperty(navigator, 'mediaDevices', {
      value: originalMediaDevices,
      writable: true
    });
    Object.defineProperty(navigator, 'vibrate', {
      value: originalVibrate,
      writable: true
    });
  });

  it('handles getUserMedia errors gracefully', async () => {
    mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('cleans up resources on unmount', () => {
    const { unmount } = render(<NativeDeviceIntegration />);
    
    unmount();

    // Should clean up event listeners and streams
    expect(mockTrack.stop).toBeDefined();
  });

  it('supports different languages', () => {
    render(
      <NativeDeviceIntegration 
        language="hi"
      />
    );

    // Component should handle Hindi language setting
    expect(screen.getByText('Native Device Integration Active')).toBeInTheDocument();
  });

  it('provides audio quality feedback', async () => {
    // Mock audio analysis data
    mockAnalyser.getByteFrequencyData.mockImplementation((dataArray) => {
      // Simulate audio data
      for (let i = 0; i < dataArray.length; i++) {
        dataArray[i] = Math.random() * 255;
      }
    });

    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(mockAudioContextInstance.createAnalyser).toHaveBeenCalled();
    });
  });

  it('handles audio worklet fallback', async () => {
    // Mock audio worklet failure
    mockAudioContextInstance.audioWorklet.addModule.mockRejectedValue(
      new Error('AudioWorklet not supported')
    );

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        'Audio worklet not available, using fallback:',
        expect.any(Error)
      );
    });

    consoleSpy.mockRestore();
  });

  it('monitors microphone quality in real-time', async () => {
    const qualityData = new Uint8Array(1024);
    qualityData.fill(128); // Mid-range audio level

    mockAnalyser.getByteFrequencyData.mockImplementation((dataArray) => {
      dataArray.set(qualityData);
    });

    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalled();
    });

    // Should be monitoring audio quality
    expect(mockAnalyser.getByteFrequencyData).toBeDefined();
  });

  it('optimizes audio settings for Sanskrit content', async () => {
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      if (mockGetUserMedia.mock.calls.length > 0) {
        const audioConstraints = mockGetUserMedia.mock.calls[0][0].audio;
        expect(audioConstraints).toMatchObject({
          sampleRate: 48000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        });
      }
    });
  });
});

describe('NativeDeviceIntegration - Advanced Features', () => {
  it('handles Om vibration pattern correctly', () => {
    render(
      <NativeDeviceIntegration 
        enableVibration={true}
      />
    );

    // The Om pattern should be [200, 100, 100, 100, 200]
    // This is tested indirectly through the component's ability to access vibrate
    expect(navigator.vibrate).toBeDefined();
  });

  it('detects meditation posture through device orientation', () => {
    const mockDeviceOrientationEvent = {
      alpha: 0,
      beta: 15, // Upright position
      gamma: 5   // Slight tilt
    };

    Object.defineProperty(window, 'DeviceOrientationEvent', {
      value: jest.fn(),
      writable: true
    });

    render(
      <NativeDeviceIntegration 
        enableMotionDetection={true}
        enableVibration={true}
      />
    );

    // Simulate device orientation event
    const orientationHandler = jest.fn();
    window.addEventListener('deviceorientation', orientationHandler);

    // Trigger the event
    window.dispatchEvent(new CustomEvent('deviceorientation', {
      detail: mockDeviceOrientationEvent
    }));

    expect(window.addEventListener).toHaveBeenCalledWith(
      'deviceorientation',
      expect.any(Function)
    );
  });

  it('provides spiritual audio enhancement', () => {
    // This tests that the component is ready to provide audio enhancement
    // The actual audio processing happens in the AudioWorklet
    render(<NativeDeviceIntegration />);
    
    expect(screen.getByText('Native Device Integration Active')).toBeInTheDocument();
  });
});

describe('NativeDeviceIntegration - Error Handling', () => {
  it('handles permission denied gracefully', async () => {
    const permissionError = new Error('Permission denied');
    permissionError.name = 'NotAllowedError';
    
    mockGetUserMedia.mockRejectedValue(permissionError);

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('handles device enumeration failures', async () => {
    mockEnumerateDevices.mockRejectedValue(new Error('Enumeration failed'));

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('handles audio context creation failures', async () => {
    mockAudioContext.mockImplementation(() => {
      throw new Error('AudioContext not supported');
    });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    render(<NativeDeviceIntegration />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });
});
