import { useState, useEffect, useCallback, useRef } from 'react';

interface DeviceCapabilities {
  microphone: boolean;
  camera: boolean;
  deviceMotion: boolean;
  geolocation: boolean;
  notifications: boolean;
  vibration: boolean;
}

interface AudioDevice {
  deviceId: string;
  label: string;
  kind: MediaDeviceKind;
  groupId: string;
  quality?: number;
}

interface UseNativeDeviceOptions {
  enableVibration?: boolean;
  enableMotionDetection?: boolean;
  enableAudioOptimization?: boolean;
  onDeviceChange?: (devices: AudioDevice[]) => void;
  onQualityChange?: (quality: number) => void;
  onCapabilitiesDetected?: (capabilities: DeviceCapabilities) => void;
}

interface NativeDeviceState {
  capabilities: DeviceCapabilities;
  audioDevices: AudioDevice[];
  selectedMicrophone: string;
  audioQuality: number;
  isRecording: boolean;
  permissions: { [key: string]: PermissionState };
  error: string | null;
}

export const useNativeDevice = (options: UseNativeDeviceOptions = {}) => {
  const {
    enableVibration = false,
    enableMotionDetection = false,
    enableAudioOptimization = true,
    onDeviceChange,
    onQualityChange,
    onCapabilitiesDetected
  } = options;

  const [state, setState] = useState<NativeDeviceState>({
    capabilities: {
      microphone: false,
      camera: false,
      deviceMotion: false,
      geolocation: false,
      notifications: false,
      vibration: false
    },
    audioDevices: [],
    selectedMicrophone: '',
    audioQuality: 0,
    isRecording: false,
    permissions: {},
    error: null
  });

  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const qualityMonitorRef = useRef<number | null>(null);

  // Check device capabilities
  const checkCapabilities = useCallback(async () => {
    const capabilities: DeviceCapabilities = {
      microphone: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      deviceMotion: 'DeviceOrientationEvent' in window && 'DeviceMotionEvent' in window,
      geolocation: 'geolocation' in navigator,
      notifications: 'Notification' in window,
      vibration: 'vibrate' in navigator
    };

    setState(prev => ({ ...prev, capabilities }));
    onCapabilitiesDetected?.(capabilities);

    return capabilities;
  }, [onCapabilitiesDetected]);

  // Request permissions
  const requestPermissions = useCallback(async () => {
    const permissionResults: { [key: string]: PermissionState } = {};

    try {
      // Microphone permission
      if (state.capabilities.microphone) {
        try {
          const micResult = await navigator.permissions.query({ name: 'microphone' as PermissionName });
          permissionResults.microphone = micResult.state;
        } catch (error) {
          console.warn('Microphone permission query not supported');
        }
      }

      // Notification permission
      if (state.capabilities.notifications) {
        try {
          const notificationPermission = await Notification.requestPermission();
          permissionResults.notifications = notificationPermission as PermissionState;
        } catch (error) {
          console.warn('Notification permission request failed:', error);
        }
      }

      setState(prev => ({ ...prev, permissions: permissionResults }));
      return permissionResults;
    } catch (error) {
      console.error('Error requesting permissions:', error);
      setState(prev => ({ ...prev, error: 'Failed to request permissions' }));
      return permissionResults;
    }
  }, [state.capabilities]);

  // Detect and enumerate audio devices
  const detectAudioDevices = useCallback(async () => {
    const hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    if (!hasMediaDevices) return [];

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs: AudioDevice[] = devices
        .filter(device => device.kind === 'audioinput' && device.deviceId !== 'default')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.substring(0, 8)}`,
          kind: device.kind,
          groupId: device.groupId
        }));

      setState(prev => ({ ...prev, audioDevices: audioInputs }));
      onDeviceChange?.(audioInputs);

      return audioInputs;
    } catch (error) {
      console.error('Error detecting audio devices:', error);
      setState(prev => ({ ...prev, error: 'Failed to detect audio devices' }));
      return [];
    }
  }, [onDeviceChange]);

  // Test microphone quality
  const testMicrophoneQuality = useCallback(async (deviceId: string): Promise<number> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: { exact: deviceId },
          sampleRate: 48000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      const audioContext = new AudioContext({ sampleRate: 48000 });
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      
      analyser.fftSize = 2048;
      source.connect(analyser);

      // Test for 500ms to measure quality
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      let qualitySum = 0;
      let samples = 0;

      return new Promise((resolve) => {
        const measureQuality = () => {
          analyser.getByteFrequencyData(dataArray);
          
          // Calculate signal quality metrics
          const avgVolume = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          const maxValue = Math.max.apply(null, Array.from(dataArray));
          const minValue = Math.min.apply(null, Array.from(dataArray));
          const dynamicRange = maxValue - minValue;
          
          const quality = (avgVolume * dynamicRange) / (255 * 255);
          qualitySum += quality;
          samples++;

          if (samples < 5) {
            setTimeout(measureQuality, 100);
          } else {
            const finalQuality = qualitySum / samples;
            
            // Cleanup
            stream.getTracks().forEach(track => track.stop());
            audioContext.close();
            
            resolve(Math.min(finalQuality * 10, 1.0)); // Normalize to 0-1
          }
        };

        measureQuality();
      });
    } catch (error) {
      console.error('Error testing microphone quality:', error);
      return 0;
    }
  }, []);

  // Find optimal microphone
  const findOptimalMicrophone = useCallback(async (devices: AudioDevice[]): Promise<AudioDevice | null> => {
    if (!enableAudioOptimization || devices.length === 0) {
      return devices[0] || null;
    }

    let bestDevice: AudioDevice | null = null;
    let bestQuality = 0;

    for (const device of devices) {
      try {
        const quality = await testMicrophoneQuality(device.deviceId);
        device.quality = quality;
        
        if (quality > bestQuality) {
          bestQuality = quality;
          bestDevice = device;
        }
      } catch (error) {
        console.warn(`Failed to test microphone ${device.deviceId}:`, error);
      }
    }

    if (bestDevice) {
      setState(prev => ({ ...prev, selectedMicrophone: bestDevice!.deviceId }));
    }

    return bestDevice;
  }, [enableAudioOptimization, testMicrophoneQuality]);

  // Start optimized recording
  const startRecording = useCallback(async (deviceId?: string) => {
    if (state.isRecording) return;

    try {
      const targetDeviceId = deviceId || state.selectedMicrophone || 'default';
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: targetDeviceId !== 'default' ? { exact: targetDeviceId } : undefined,
          sampleRate: 48000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      mediaStreamRef.current = stream;
      
      if (enableAudioOptimization) {
        // Set up audio context for quality monitoring
        audioContextRef.current = new AudioContext({ 
          sampleRate: 48000,
          latencyHint: 'interactive'
        });

        const source = audioContextRef.current.createMediaStreamSource(stream);
        const analyser = audioContextRef.current.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);

        // Start quality monitoring
        const monitorQuality = () => {
          if (!state.isRecording || !analyser) return;

          const dataArray = new Uint8Array(analyser.frequencyBinCount);
          analyser.getByteFrequencyData(dataArray);
          
          const avgVolume = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          const quality = Math.min(avgVolume / 128, 1.0);
          
          setState(prev => ({ ...prev, audioQuality: quality }));
          onQualityChange?.(quality);

          qualityMonitorRef.current = requestAnimationFrame(monitorQuality);
        };

        monitorQuality();
      }

      setState(prev => ({ ...prev, isRecording: true, error: null }));
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setState(prev => ({ 
        ...prev, 
        error: `Failed to start recording: ${error instanceof Error ? error.message : 'Unknown error'}` 
      }));
    }
  }, [state.isRecording, state.selectedMicrophone, enableAudioOptimization, onQualityChange]);

  // Stop recording
  const stopRecording = useCallback(() => {
    setState(prev => ({ ...prev, isRecording: false, audioQuality: 0 }));

    if (qualityMonitorRef.current) {
      cancelAnimationFrame(qualityMonitorRef.current);
      qualityMonitorRef.current = null;
    }

    if (mediaStreamRef.current && mediaStreamRef.current.getTracks) {
      const tracks = mediaStreamRef.current.getTracks();
      if (tracks && Array.isArray(tracks)) {
        tracks.forEach(track => track.stop());
      }
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  }, []);

  // Trigger spiritual vibration
  const triggerSpiritualVibration = useCallback(() => {
    if (!enableVibration || !state.capabilities.vibration) return;

    // Gentle Om-like vibration pattern: long-short-long
    const omPattern = [200, 100, 100, 100, 200];
    navigator.vibrate(omPattern);
  }, [enableVibration, state.capabilities.vibration]);

  // Send spiritual notification
  const sendSpiritualNotification = useCallback((title: string, body: string, options: NotificationOptions = {}) => {
    if (!state.capabilities.notifications || state.permissions.notifications !== 'granted') {
      return;
    }

    const spiritualOptions: NotificationOptions = {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'vimarsh-spiritual',
      requireInteraction: false,
      silent: true, // Spiritual notifications should be peaceful
      ...options
    };

    new Notification(title, { body, ...spiritualOptions });
  }, [state.capabilities.notifications, state.permissions.notifications]);

  // Initialize on mount
  useEffect(() => {
    const initialize = async () => {
      await checkCapabilities();
      await requestPermissions();
      await detectAudioDevices();
    };

    initialize();

    // Set up device change listener
    const handleDeviceChange = () => {
      detectAudioDevices();
    };

    navigator.mediaDevices?.addEventListener('devicechange', handleDeviceChange);

    return () => {
      navigator.mediaDevices?.removeEventListener('devicechange', handleDeviceChange);
      stopRecording();
    };
  }, []);

  // Auto-select optimal microphone when devices are detected
  useEffect(() => {
    if (state.audioDevices.length > 0 && !state.selectedMicrophone) {
      findOptimalMicrophone(state.audioDevices);
    }
  }, [state.audioDevices, state.selectedMicrophone, findOptimalMicrophone]);

  return {
    // State
    capabilities: state.capabilities,
    audioDevices: state.audioDevices,
    selectedMicrophone: state.selectedMicrophone,
    audioQuality: state.audioQuality,
    isRecording: state.isRecording,
    permissions: state.permissions,
    error: state.error,

    // Actions
    startRecording,
    stopRecording,
    detectAudioDevices,
    findOptimalMicrophone,
    testMicrophoneQuality,
    triggerSpiritualVibration,
    sendSpiritualNotification,
    requestPermissions,

    // Utilities
    selectMicrophone: (deviceId: string) => {
      setState(prev => ({ ...prev, selectedMicrophone: deviceId }));
    },
    clearError: () => {
      setState(prev => ({ ...prev, error: null }));
    }
  };
};
