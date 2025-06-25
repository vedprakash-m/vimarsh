import React, { useState, useEffect, useRef, useCallback } from 'react';

interface DeviceCapabilities {
  microphone: boolean;
  camera: boolean;
  deviceMotion: boolean;
  geolocation: boolean;
  notifications: boolean;
  vibration: boolean;
}

interface AudioConfig {
  sampleRate: number;
  channelCount: number;
  echoCancellation: boolean;
  noiseSuppression: boolean;
  autoGainControl: boolean;
}

interface NativeDeviceIntegrationProps {
  onAudioData?: (audioData: Float32Array) => void;
  onDeviceCapabilities?: (capabilities: DeviceCapabilities) => void;
  onOptimalMicrophoneFound?: (deviceId: string) => void;
  enableVibration?: boolean;
  enableMotionDetection?: boolean;
  language?: 'en' | 'hi';
}

interface AudioDevice {
  deviceId: string;
  label: string;
  kind: MediaDeviceKind;
  groupId: string;
  quality?: number;
}

const NativeDeviceIntegration: React.FC<NativeDeviceIntegrationProps> = ({
  onAudioData,
  onDeviceCapabilities,
  onOptimalMicrophoneFound,
  enableVibration = false,
  enableMotionDetection = false,
  language = 'en'
}) => {
  const [capabilities, setCapabilities] = useState<DeviceCapabilities>({
    microphone: false,
    camera: false,
    deviceMotion: false,
    geolocation: false,
    notifications: false,
    vibration: false
  });
  
  const [audioDevices, setAudioDevices] = useState<AudioDevice[]>([]);
  const [selectedMicrophone, setSelectedMicrophone] = useState<string>('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioQuality, setAudioQuality] = useState<number>(0);
  const [permissions, setPermissions] = useState<{[key: string]: PermissionState}>({});

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioWorkletRef = useRef<AudioWorkletNode | null>(null);
  const deviceOrientationRef = useRef<{alpha: number, beta: number, gamma: number} | null>(null);

  // Optimal audio configuration for spiritual content
  const OPTIMAL_AUDIO_CONFIG: AudioConfig = {
    sampleRate: 48000, // High quality for Sanskrit pronunciation
    channelCount: 1, // Mono for voice
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  };

  // Check device capabilities on mount
  useEffect(() => {
    checkDeviceCapabilities();
    requestPermissions();
    detectAudioDevices();
    
    // Set up device change listener
    navigator.mediaDevices.addEventListener('devicechange', detectAudioDevices);
    
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', detectAudioDevices);
      cleanup();
    };
  }, []);

  const checkDeviceCapabilities = async () => {
    const caps: DeviceCapabilities = {
      microphone: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      deviceMotion: 'DeviceOrientationEvent' in window,
      geolocation: 'geolocation' in navigator,
      notifications: 'Notification' in window,
      vibration: 'vibrate' in navigator
    };

    setCapabilities(caps);
    onDeviceCapabilities?.(caps);
  };

  const requestPermissions = async () => {
    const permissionResults: {[key: string]: PermissionState} = {};

    // Request microphone permission
    if (capabilities.microphone) {
      try {
        const result = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        permissionResults.microphone = result.state;
      } catch (error) {
        console.warn('Microphone permission query failed:', error);
      }
    }

    // Request notification permission if supported
    if (capabilities.notifications) {
      try {
        const permission = await Notification.requestPermission();
        permissionResults.notifications = permission as PermissionState;
      } catch (error) {
        console.warn('Notification permission request failed:', error);
      }
    }

    setPermissions(permissionResults);
  };

  const detectAudioDevices = useCallback(async () => {
    if (!capabilities.microphone) return;

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices
        .filter(device => device.kind === 'audioinput' && device.deviceId !== 'default')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.substring(0, 8)}`,
          kind: device.kind,
          groupId: device.groupId,
          quality: 0 // Will be calculated during testing
        }));

      setAudioDevices(audioInputs);
      
      // Find optimal microphone
      if (audioInputs.length > 0) {
        const optimalDevice = await findOptimalMicrophone(audioInputs);
        if (optimalDevice) {
          setSelectedMicrophone(optimalDevice.deviceId);
          onOptimalMicrophoneFound?.(optimalDevice.deviceId);
        }
      }
    } catch (error) {
      console.error('Error detecting audio devices:', error);
    }
  }, [capabilities.microphone, onOptimalMicrophoneFound]);

  const findOptimalMicrophone = async (devices: AudioDevice[]): Promise<AudioDevice | null> => {
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

    return bestDevice;
  };

  const testMicrophoneQuality = async (deviceId: string): Promise<number> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: { exact: deviceId },
          ...OPTIMAL_AUDIO_CONFIG
        }
      });

      const audioContext = new AudioContext({ sampleRate: OPTIMAL_AUDIO_CONFIG.sampleRate });
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      
      analyser.fftSize = 2048;
      source.connect(analyser);

      // Test for 1 second to measure quality
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      let qualitySum = 0;
      let samples = 0;

      return new Promise((resolve) => {
        const measureQuality = () => {
          analyser.getByteFrequencyData(dataArray);
          
          // Calculate signal-to-noise ratio approximation
          const avgVolume = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          const maxValue = Math.max.apply(null, Array.from(dataArray));
          const minValue = Math.min.apply(null, Array.from(dataArray));
          const dynamicRange = maxValue - minValue;
          
          qualitySum += (avgVolume * dynamicRange) / 255;
          samples++;

          if (samples < 10) {
            setTimeout(measureQuality, 100);
          } else {
            const quality = qualitySum / samples;
            
            // Cleanup
            stream.getTracks().forEach(track => track.stop());
            audioContext.close();
            
            resolve(quality);
          }
        };

        measureQuality();
      });
    } catch (error) {
      console.error('Error testing microphone quality:', error);
      return 0;
    }
  };

  const startOptimizedRecording = async (deviceId?: string) => {
    if (isRecording) return;

    try {
      const constraints = {
        audio: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          ...OPTIMAL_AUDIO_CONFIG,
          // Additional spiritual content optimizations
          latency: 0.05, // Low latency for real-time interaction
          volume: 1.0
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      mediaStreamRef.current = stream;

      // Set up audio context for advanced processing
      audioContextRef.current = new AudioContext({ 
        sampleRate: OPTIMAL_AUDIO_CONFIG.sampleRate,
        latencyHint: 'interactive'
      });

      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0.8;
      source.connect(analyser);
      analyserRef.current = analyser;

      // Set up audio worklet for real-time processing
      try {
        await audioContextRef.current.audioWorklet.addModule('/audio-processor.js');
        const workletNode = new AudioWorkletNode(audioContextRef.current, 'audio-processor');
        
        workletNode.port.onmessage = (event) => {
          if (event.data.audioData && onAudioData) {
            onAudioData(event.data.audioData);
          }
        };

        source.connect(workletNode);
        audioWorkletRef.current = workletNode;
      } catch (error) {
        console.warn('Audio worklet not available, using fallback:', error);
        // Fallback to traditional audio processing
        setupAudioProcessing(analyser);
      }

      setIsRecording(true);
      
      // Start quality monitoring
      monitorAudioQuality();

    } catch (error) {
      console.error('Error starting optimized recording:', error);
      throw error;
    }
  };

  const setupAudioProcessing = (analyser: AnalyserNode) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);

    const processAudio = () => {
      if (!isRecording) return;

      analyser.getFloatFrequencyData(dataArray);
      
      if (onAudioData) {
        onAudioData(dataArray);
      }

      requestAnimationFrame(processAudio);
    };

    processAudio();
  };

  const monitorAudioQuality = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const checkQuality = () => {
      if (!isRecording || !analyserRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Calculate real-time audio quality metrics
      const avgVolume = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
      const quality = Math.min(avgVolume / 128, 1.0); // Normalize to 0-1
      
      setAudioQuality(quality);

      setTimeout(checkQuality, 100);
    };

    checkQuality();
  };

  const stopRecording = () => {
    if (!isRecording) return;

    setIsRecording(false);
    setAudioQuality(0);

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
    audioWorkletRef.current = null;
  };

  const setupDeviceMotionDetection = () => {
    if (!enableMotionDetection || !capabilities.deviceMotion) return;

    const handleDeviceOrientation = (event: DeviceOrientationEvent) => {
      const orientation = {
        alpha: event.alpha || 0,
        beta: event.beta || 0,
        gamma: event.gamma || 0
      };

      deviceOrientationRef.current = orientation;

      // Detect meditation posture (device relatively stable and upright)
      const isStable = Math.abs(orientation.beta) < 30 && Math.abs(orientation.gamma) < 30;
      
      if (isStable) {
        // User might be in meditation posture - could trigger spiritual mode
        triggerSpiritualVibration();
      }
    };

    window.addEventListener('deviceorientation', handleDeviceOrientation);

    return () => {
      window.removeEventListener('deviceorientation', handleDeviceOrientation);
    };
  };

  const triggerSpiritualVibration = () => {
    if (!enableVibration || !capabilities.vibration) return;

    // Gentle vibration pattern for spiritual context (Om rhythm: long-short-long)
    const omPattern = [200, 100, 100, 100, 200];
    navigator.vibrate(omPattern);
  };

  const cleanup = () => {
    stopRecording();
    
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  // Set up device motion detection
  useEffect(() => {
    const cleanup = setupDeviceMotionDetection();
    return cleanup;
  }, [enableMotionDetection, capabilities.deviceMotion]);

  return (
    <div className="native-device-integration">
      {/* Device capabilities status */}
      <div className="device-status" style={{ display: 'none' }}>
        <div className="capabilities">
          <span>Microphone: {capabilities.microphone ? '✓' : '✗'}</span>
          <span>Camera: {capabilities.camera ? '✓' : '✗'}</span>
          <span>Motion: {capabilities.deviceMotion ? '✓' : '✗'}</span>
          <span>Vibration: {capabilities.vibration ? '✓' : '✗'}</span>
        </div>
        
        {isRecording && (
          <div className="audio-quality">
            Audio Quality: {Math.round(audioQuality * 100)}%
          </div>
        )}
      </div>

      {/* Audio device selector for advanced users */}
      {audioDevices.length > 1 && (
        <div className="device-selector" style={{ display: 'none' }}>
          <select 
            value={selectedMicrophone} 
            onChange={(e) => setSelectedMicrophone(e.target.value)}
          >
            {audioDevices.map(device => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label} {device.quality ? `(Quality: ${Math.round(device.quality * 100)}%)` : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Hidden interface - this component works behind the scenes */}
      <div style={{ display: 'none' }}>
        Native Device Integration Active
      </div>
    </div>
  );
};

export default NativeDeviceIntegration;
