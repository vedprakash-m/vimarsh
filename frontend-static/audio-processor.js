// Audio Worklet Processor for Vimarsh Spiritual Guidance
// Optimized for Sanskrit pronunciation and spiritual content processing

class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    
    // Spiritual audio processing parameters
    this.bufferSize = 4096;
    this.sampleBuffer = new Float32Array(this.bufferSize);
    this.bufferIndex = 0;
    
    // Sanskrit-specific frequency analysis
    this.sanskritFrequencyBands = {
      fundamentalLow: { min: 80, max: 250 },   // Low Om frequencies
      vowelClarity: { min: 250, max: 1000 },   // Sanskrit vowel definition
      consonantDetail: { min: 1000, max: 4000 }, // Consonant articulation
      harmonicRich: { min: 4000, max: 8000 }   // Harmonic richness
    };
    
    // Quality metrics
    this.qualityMetrics = {
      clarity: 0,
      tonal: 0,
      spiritual: 0
    };
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    if (input.length > 0) {
      const inputChannel = input[0];
      
      // Copy input to output (passthrough)
      if (output.length > 0) {
        output[0].set(inputChannel);
      }

      // Process audio for spiritual content optimization
      this.processForSpiritualContent(inputChannel);
      
      // Buffer audio data for analysis
      this.bufferAudioData(inputChannel);
    }

    return true;
  }

  processForSpiritualContent(audioData) {
    // Analyze audio for spiritual qualities
    const metrics = this.analyzeSpiritualQualities(audioData);
    
    // Apply gentle enhancement for Sanskrit pronunciation
    this.enhanceForSanskrit(audioData);
    
    // Update quality metrics
    this.qualityMetrics = metrics;
  }

  analyzeSpiritualQualities(audioData) {
    const fftSize = 1024;
    const fft = this.performFFT(audioData.slice(0, fftSize));
    
    // Calculate clarity (how well-defined the speech is)
    const clarity = this.calculateClarity(fft);
    
    // Calculate tonal quality (harmonic richness for chanting)
    const tonal = this.calculateTonalQuality(fft);
    
    // Calculate spiritual quality (presence of meditative frequencies)
    const spiritual = this.calculateSpiritualQuality(fft);
    
    return { clarity, tonal, spiritual };
  }

  calculateClarity(fftData) {
    const vowelEnergy = this.getEnergyInBand(fftData, this.sanskritFrequencyBands.vowelClarity);
    const consonantEnergy = this.getEnergyInBand(fftData, this.sanskritFrequencyBands.consonantDetail);
    const totalEnergy = this.getTotalEnergy(fftData);
    
    if (totalEnergy === 0) return 0;
    
    // High clarity when vowel and consonant bands are well-defined
    return (vowelEnergy + consonantEnergy) / totalEnergy;
  }

  calculateTonalQuality(fftData) {
    const fundamentalEnergy = this.getEnergyInBand(fftData, this.sanskritFrequencyBands.fundamentalLow);
    const harmonicEnergy = this.getEnergyInBand(fftData, this.sanskritFrequencyBands.harmonicRich);
    const totalEnergy = this.getTotalEnergy(fftData);
    
    if (totalEnergy === 0) return 0;
    
    // Good tonal quality when harmonics are present
    const harmonicRatio = harmonicEnergy / totalEnergy;
    const fundamentalRatio = fundamentalEnergy / totalEnergy;
    
    return Math.min(harmonicRatio * 2 + fundamentalRatio, 1.0);
  }

  calculateSpiritualQuality(fftData) {
    // Look for Om-like resonance patterns
    const omFrequencies = [110, 220, 330, 440]; // Approximate Om harmonics
    let omPresence = 0;
    
    for (const freq of omFrequencies) {
      const binIndex = Math.round(freq * fftData.length / (sampleRate / 2));
      if (binIndex < fftData.length) {
        omPresence += fftData[binIndex];
      }
    }
    
    const totalEnergy = this.getTotalEnergy(fftData);
    return totalEnergy > 0 ? Math.min(omPresence / totalEnergy * 4, 1.0) : 0;
  }

  enhanceForSanskrit(audioData) {
    // Gentle enhancement for Sanskrit pronunciation
    // This is a placeholder for more sophisticated processing
    
    // Slight boost to vowel frequencies for clarity
    const vowelBoost = 1.05;
    
    // Apply gentle filtering (this is simplified)
    for (let i = 1; i < audioData.length - 1; i++) {
      // Simple smoothing filter to reduce harsh consonants
      audioData[i] = (audioData[i - 1] + audioData[i] * vowelBoost + audioData[i + 1]) / 3;
    }
  }

  bufferAudioData(audioData) {
    // Buffer audio data for further analysis
    for (let i = 0; i < audioData.length; i++) {
      this.sampleBuffer[this.bufferIndex] = audioData[i];
      this.bufferIndex = (this.bufferIndex + 1) % this.bufferSize;
    }
    
    // Send buffered data to main thread every 1024 samples
    if (this.bufferIndex % 1024 === 0) {
      this.port.postMessage({
        audioData: this.sampleBuffer.slice(0, 1024),
        qualityMetrics: this.qualityMetrics,
        timestamp: currentTime
      });
    }
  }

  performFFT(audioData) {
    // Simplified FFT implementation for frequency analysis
    // In a real implementation, you'd use a proper FFT library
    const N = audioData.length;
    const result = new Float32Array(N / 2);
    
    for (let k = 0; k < N / 2; k++) {
      let real = 0;
      let imag = 0;
      
      for (let n = 0; n < N; n++) {
        const angle = -2 * Math.PI * k * n / N;
        real += audioData[n] * Math.cos(angle);
        imag += audioData[n] * Math.sin(angle);
      }
      
      result[k] = Math.sqrt(real * real + imag * imag);
    }
    
    return result;
  }

  getEnergyInBand(fftData, band) {
    const nyquist = sampleRate / 2;
    const binSize = nyquist / fftData.length;
    
    const startBin = Math.floor(band.min / binSize);
    const endBin = Math.ceil(band.max / binSize);
    
    let energy = 0;
    for (let i = startBin; i < Math.min(endBin, fftData.length); i++) {
      energy += fftData[i];
    }
    
    return energy;
  }

  getTotalEnergy(fftData) {
    let total = 0;
    for (let i = 0; i < fftData.length; i++) {
      total += fftData[i];
    }
    return total;
  }
}

registerProcessor('audio-processor', AudioProcessor);
