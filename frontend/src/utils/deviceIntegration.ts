// Native device integration utilities
// Handles camera, microphone optimization, and device-specific features

import React from 'react';

export interface DeviceCapabilities {
  hasCamera: boolean;
  hasMicrophone: boolean;
  hasAudio: boolean;
  hasVideoInput: boolean;
  hasAudioInput: boolean;
  supportsTouchGestures: boolean;
  supportsVibration: boolean;
  supportsSpeechRecognition: boolean;
  supportsSpeechSynthesis: boolean;
  supportsWakeLock: boolean;
  supportsMediaSession: boolean;
  isStandalone: boolean;
  platform: 'ios' | 'android' | 'desktop' | 'unknown';
}

export interface MediaDeviceInfo {
  deviceId: string;
  label: string;
  kind: 'audioinput' | 'videoinput' | 'audiooutput';
  groupId?: string;
}

export interface AudioSettings {
  echoCancellation: boolean;
  noiseSuppression: boolean;
  autoGainControl: boolean;
  sampleRate?: number;
  channelCount?: number;
}

export interface VideoSettings {
  width: number;
  height: number;
  frameRate: number;
  facingMode: 'user' | 'environment';
}

class DeviceIntegrationManager {
  private capabilities: DeviceCapabilities | null = null;
  private mediaDevices: MediaDeviceInfo[] = [];
  private currentAudioStream: MediaStream | null = null;
  private currentVideoStream: MediaStream | null = null;
  private wakeLock: any = null;
  private mediaSession: any = null;

  constructor() {
    this.initializeDeviceIntegration();
  }

  private async initializeDeviceIntegration() {
    await this.detectCapabilities();
    await this.enumerateDevices();
    this.setupMediaSession();
    this.setupTouchGestures();
  }

  // Device Capabilities Detection
  private async detectCapabilities(): Promise<void> {
    this.capabilities = {
      hasCamera: await this.checkCameraAccess(),
      hasMicrophone: await this.checkMicrophoneAccess(),
      hasAudio: 'AudioContext' in window,
      hasVideoInput: await this.hasVideoInputDevice(),
      hasAudioInput: await this.hasAudioInputDevice(),
      supportsTouchGestures: 'ontouchstart' in window,
      supportsVibration: 'vibrate' in navigator,
      supportsSpeechRecognition: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
      supportsSpeechSynthesis: 'speechSynthesis' in window,
      supportsWakeLock: 'wakeLock' in navigator,
      supportsMediaSession: 'mediaSession' in navigator,
      isStandalone: this.isStandaloneApp(),
      platform: this.detectPlatform()
    };
  }

  private async checkCameraAccess(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch {
      return false;
    }
  }

  private async checkMicrophoneAccess(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch {
      return false;
    }
  }

  private async hasVideoInputDevice(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'videoinput');
    } catch {
      return false;
    }
  }

  private async hasAudioInputDevice(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'audioinput');
    } catch {
      return false;
    }
  }

  private isStandaloneApp(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }

  private detectPlatform(): DeviceCapabilities['platform'] {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (/iphone|ipad|ipod/.test(userAgent)) {
      return 'ios';
    } else if (/android/.test(userAgent)) {
      return 'android';
    } else if (/windows|mac|linux/.test(userAgent) && !('ontouchstart' in window)) {
      return 'desktop';
    } else {
      return 'unknown';
    }
  }

  // Media Device Management
  private async enumerateDevices(): Promise<void> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      this.mediaDevices = devices.map(device => ({
        deviceId: device.deviceId,
        label: device.label || `${device.kind} ${device.deviceId.slice(0, 8)}`,
        kind: device.kind as 'audioinput' | 'videoinput' | 'audiooutput',
        groupId: device.groupId
      }));
    } catch (error) {
      console.error('[Device] Failed to enumerate devices:', error);
      this.mediaDevices = [];
    }
  }

  // Optimized Audio Capture
  public async startOptimizedAudioCapture(
    deviceId?: string,
    settings?: Partial<AudioSettings>
  ): Promise<MediaStream | null> {
    try {
      const defaultSettings: AudioSettings = {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 44100,
        channelCount: 1
      };

      const audioSettings = { ...defaultSettings, ...settings };
      
      const constraints: MediaStreamConstraints = {
        audio: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          echoCancellation: audioSettings.echoCancellation,
          noiseSuppression: audioSettings.noiseSuppression,
          autoGainControl: audioSettings.autoGainControl,
          sampleRate: audioSettings.sampleRate,
          channelCount: audioSettings.channelCount
        }
      };

      // Platform-specific optimizations
      if (this.capabilities?.platform === 'ios') {
        // iOS-specific audio optimizations
        (constraints.audio as any).suppressLocalAudioPlayback = true;
      } else if (this.capabilities?.platform === 'android') {
        // Android-specific audio optimizations
        (constraints.audio as any).googEchoCancellation = true;
        (constraints.audio as any).googAutoGainControl = true;
        (constraints.audio as any).googNoiseSuppression = true;
      }

      this.currentAudioStream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Apply additional audio processing for spiritual content
      this.applyAudioProcessing(this.currentAudioStream);
      
      return this.currentAudioStream;
    } catch (error) {
      console.error('[Device] Failed to start audio capture:', error);
      return null;
    }
  }

  private applyAudioProcessing(stream: MediaStream): void {
    if (!('AudioContext' in window)) return;

    try {
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      
      // Create audio processing nodes for spiritual content
      const gainNode = audioContext.createGain();
      const compressor = audioContext.createDynamicsCompressor();
      const filter = audioContext.createBiquadFilter();
      
      // Configure for voice clarity (important for Sanskrit pronunciation)
      filter.type = 'highpass';
      filter.frequency.setValueAtTime(80, audioContext.currentTime); // Remove low-frequency noise
      
      compressor.threshold.setValueAtTime(-24, audioContext.currentTime);
      compressor.knee.setValueAtTime(30, audioContext.currentTime);
      compressor.ratio.setValueAtTime(12, audioContext.currentTime);
      compressor.attack.setValueAtTime(0.003, audioContext.currentTime);
      compressor.release.setValueAtTime(0.25, audioContext.currentTime);
      
      gainNode.gain.setValueAtTime(1.2, audioContext.currentTime);
      
      // Connect processing chain
      source.connect(filter);
      filter.connect(compressor);
      compressor.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
    } catch (error) {
      console.error('[Device] Audio processing setup failed:', error);
    }
  }

  // Camera Integration
  public async startCameraCapture(
    deviceId?: string,
    settings?: Partial<VideoSettings>
  ): Promise<MediaStream | null> {
    try {
      const defaultSettings: VideoSettings = {
        width: 640,
        height: 480,
        frameRate: 30,
        facingMode: 'user'
      };

      const videoSettings = { ...defaultSettings, ...settings };
      
      const constraints: MediaStreamConstraints = {
        video: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          width: { ideal: videoSettings.width },
          height: { ideal: videoSettings.height },
          frameRate: { ideal: videoSettings.frameRate },
          facingMode: { ideal: videoSettings.facingMode }
        }
      };

      this.currentVideoStream = await navigator.mediaDevices.getUserMedia(constraints);
      return this.currentVideoStream;
    } catch (error) {
      console.error('[Device] Failed to start camera capture:', error);
      return null;
    }
  }

  // Media Session API for background audio
  private setupMediaSession(): void {
    if (!this.capabilities?.supportsMediaSession) return;

    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: 'Vimarsh - Wisdom Without Boundaries',
        artist: 'Lord Krishna',
        album: 'Ancient Wisdom',
        artwork: [
          { src: '/logo192.png', sizes: '192x192', type: 'image/png' },
          { src: '/logo512.png', sizes: '512x512', type: 'image/png' }
        ]
      });

      // Handle media session actions
      navigator.mediaSession.setActionHandler('play', () => {
        this.resumeAudio();
      });

      navigator.mediaSession.setActionHandler('pause', () => {
        this.pauseAudio();
      });

      navigator.mediaSession.setActionHandler('stop', () => {
        this.stopAudio();
      });

    } catch (error) {
      console.error('[Device] Media session setup failed:', error);
    }
  }

  // Touch Gesture Support
  private setupTouchGestures(): void {
    if (!this.capabilities?.supportsTouchGestures) return;

    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;

    document.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchStartTime = Date.now();
      }
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      if (e.changedTouches.length === 1) {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        const touchEndTime = Date.now();
        
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        const deltaTime = touchEndTime - touchStartTime;
        
        // Detect swipe gestures
        if (Math.abs(deltaX) > 50 && deltaTime < 300) {
          if (deltaX > 0) {
            this.handleSwipeRight();
          } else {
            this.handleSwipeLeft();
          }
        }
        
        // Detect long press
        if (deltaTime > 500 && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
          this.handleLongPress();
        }
      }
    }, { passive: true });
  }

  // Wake Lock Management
  public async requestWakeLock(): Promise<void> {
    if (!this.capabilities?.supportsWakeLock) return;

    try {
      this.wakeLock = await (navigator as any).wakeLock.request('screen');
      console.log('[Device] Wake lock activated');
      
      this.wakeLock.addEventListener('release', () => {
        console.log('[Device] Wake lock released');
      });
    } catch (error) {
      console.error('[Device] Failed to request wake lock:', error);
    }
  }

  public releaseWakeLock(): void {
    if (this.wakeLock) {
      this.wakeLock.release();
      this.wakeLock = null;
    }
  }

  // Haptic Feedback
  public vibrate(pattern: number | number[]): void {
    if (this.capabilities?.supportsVibration) {
      navigator.vibrate(pattern);
    }
  }

  public provideFeedback(type: 'success' | 'error' | 'warning' | 'light'): void {
    const patterns = {
      success: [100, 50, 100],
      error: [200, 100, 200, 100, 200],
      warning: [150, 75, 150],
      light: [50]
    };
    
    this.vibrate(patterns[type]);
  }

  // Public API Methods
  public getCapabilities(): DeviceCapabilities | null {
    return this.capabilities;
  }

  public getMediaDevices(): MediaDeviceInfo[] {
    return [...this.mediaDevices];
  }

  public getAudioInputDevices(): MediaDeviceInfo[] {
    return this.mediaDevices.filter(device => device.kind === 'audioinput');
  }

  public getVideoInputDevices(): MediaDeviceInfo[] {
    return this.mediaDevices.filter(device => device.kind === 'videoinput');
  }

  public stopAllStreams(): void {
    if (this.currentAudioStream) {
      this.currentAudioStream.getTracks().forEach(track => track.stop());
      this.currentAudioStream = null;
    }
    
    if (this.currentVideoStream) {
      this.currentVideoStream.getTracks().forEach(track => track.stop());
      this.currentVideoStream = null;
    }
  }

  // Event handlers for gestures
  private handleSwipeLeft(): void {
    const event = new CustomEvent('device-swipe-left');
    window.dispatchEvent(event);
  }

  private handleSwipeRight(): void {
    const event = new CustomEvent('device-swipe-right');
    window.dispatchEvent(event);
  }

  private handleLongPress(): void {
    const event = new CustomEvent('device-long-press');
    window.dispatchEvent(event);
  }

  // Media control methods
  private resumeAudio(): void {
    const event = new CustomEvent('device-audio-resume');
    window.dispatchEvent(event);
  }

  private pauseAudio(): void {
    const event = new CustomEvent('device-audio-pause');
    window.dispatchEvent(event);
  }

  private stopAudio(): void {
    const event = new CustomEvent('device-audio-stop');
    window.dispatchEvent(event);
  }

  // Cleanup
  public cleanup(): void {
    this.stopAllStreams();
    this.releaseWakeLock();
  }
}

// Create and export device manager instance
export const deviceManager = new DeviceIntegrationManager();

// React hook for device integration
export const useDeviceIntegration = () => {
  const [capabilities, setCapabilities] = React.useState<DeviceCapabilities | null>(null);
  const [mediaDevices, setMediaDevices] = React.useState<MediaDeviceInfo[]>([]);
  const [isAudioActive, setIsAudioActive] = React.useState(false);
  const [isVideoActive, setIsVideoActive] = React.useState(false);

  React.useEffect(() => {
    const updateCapabilities = () => {
      setCapabilities(deviceManager.getCapabilities());
      setMediaDevices(deviceManager.getMediaDevices());
    };

    // Initial load
    setTimeout(updateCapabilities, 100);

    // Listen for device changes
    navigator.mediaDevices?.addEventListener('devicechange', updateCapabilities);

    return () => {
      navigator.mediaDevices?.removeEventListener('devicechange', updateCapabilities);
    };
  }, []);

  const startAudioCapture = async (deviceId?: string, settings?: Partial<AudioSettings>) => {
    const stream = await deviceManager.startOptimizedAudioCapture(deviceId, settings);
    setIsAudioActive(!!stream);
    return stream;
  };

  const startVideoCapture = async (deviceId?: string, settings?: Partial<VideoSettings>) => {
    const stream = await deviceManager.startCameraCapture(deviceId, settings);
    setIsVideoActive(!!stream);
    return stream;
  };

  const stopAllStreams = () => {
    deviceManager.stopAllStreams();
    setIsAudioActive(false);
    setIsVideoActive(false);
  };

  return {
    capabilities,
    mediaDevices,
    isAudioActive,
    isVideoActive,
    audioInputDevices: deviceManager.getAudioInputDevices(),
    videoInputDevices: deviceManager.getVideoInputDevices(),
    startAudioCapture,
    startVideoCapture,
    stopAllStreams,
    vibrate: (pattern: number | number[]) => deviceManager.vibrate(pattern),
    provideFeedback: (type: 'success' | 'error' | 'warning' | 'light') => deviceManager.provideFeedback(type),
    requestWakeLock: () => deviceManager.requestWakeLock(),
    releaseWakeLock: () => deviceManager.releaseWakeLock()
  };
};

export default deviceManager;
