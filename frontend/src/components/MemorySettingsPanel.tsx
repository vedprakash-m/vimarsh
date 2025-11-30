/**
 * Memory Settings Panel Component
 * 
 * User memory preferences and controls for the hierarchical memory system.
 * Part of Phase 3: Frontend Memory UX implementation.
 * 
 * Features:
 * - Memory retention preferences
 * - Privacy controls
 * - Export/import memory data
 * - Clear memory options
 * - Notification preferences
 */

import React, { useState, useCallback } from 'react';
import { useMemory, EmotionalTone } from '../contexts/MemoryContext';

interface MemorySettings {
  memoryRetentionDays: number;
  enableCrossPersonalityMemory: boolean;
  enableEmotionalTracking: boolean;
  enableTopicSuggestions: boolean;
  privacyMode: 'standard' | 'enhanced' | 'minimal';
  autoSessionSummary: boolean;
  notifyOnMilestones: boolean;
  preferredTone: EmotionalTone;
}

interface MemorySettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

// Default settings
const DEFAULT_SETTINGS: MemorySettings = {
  memoryRetentionDays: 90,
  enableCrossPersonalityMemory: true,
  enableEmotionalTracking: true,
  enableTopicSuggestions: true,
  privacyMode: 'standard',
  autoSessionSummary: true,
  notifyOnMilestones: true,
  preferredTone: 'curious',
};

// Privacy mode descriptions
const PRIVACY_MODES = {
  standard: {
    label: 'Standard',
    description: 'Full memory features enabled. Your conversations help build personalized guidance.',
    icon: '🔓',
  },
  enhanced: {
    label: 'Enhanced Privacy',
    description: 'Limited cross-session memory. Conversations not linked over time.',
    icon: '🔐',
  },
  minimal: {
    label: 'Minimal Memory',
    description: 'Session-only memory. Nothing saved after you leave.',
    icon: '🔒',
  },
};

// Retention period options
const RETENTION_OPTIONS = [
  { value: 30, label: '30 days' },
  { value: 60, label: '60 days' },
  { value: 90, label: '90 days (recommended)' },
  { value: 180, label: '6 months' },
  { value: 365, label: '1 year' },
];

// Tone options
const TONE_OPTIONS: Array<{ value: EmotionalTone; label: string; emoji: string }> = [
  { value: 'curious', label: 'Curious & Open', emoji: '🤔' },
  { value: 'seeking', label: 'Seeking Guidance', emoji: '🙏' },
  { value: 'peaceful', label: 'Peaceful', emoji: '😌' },
  { value: 'reflective', label: 'Reflective', emoji: '💭' },
  { value: 'determined', label: 'Determined', emoji: '💪' },
  { value: 'grateful', label: 'Grateful', emoji: '🙏' },
];

export const MemorySettingsPanel: React.FC<MemorySettingsPanelProps> = ({
  isOpen,
  onClose,
  className = '',
}) => {
  const { memoryProfile, isMemoryEnabled } = useMemory();
  
  // Settings state
  const [settings, setSettings] = useState<MemorySettings>(DEFAULT_SETTINGS);
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Update a single setting
  const updateSetting = useCallback(<K extends keyof MemorySettings>(
    key: K,
    value: MemorySettings[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  }, []);

  // Save settings
  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setSaveMessage(null);
    
    try {
      // TODO: API call to save settings
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSaveMessage('Settings saved successfully! ✓');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      setSaveMessage('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [settings]);

  // Clear all memory
  const handleClearMemory = useCallback(async () => {
    try {
      // TODO: API call to clear memory
      await new Promise((resolve) => setTimeout(resolve, 500));
      setShowConfirmClear(false);
      setSaveMessage('Memory cleared successfully.');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      setSaveMessage('Failed to clear memory. Please try again.');
    }
  }, []);

  // Export memory data
  const handleExport = useCallback(async () => {
    try {
      // TODO: API call to export memory data
      const exportData = {
        profile: memoryProfile,
        settings: settings,
        exportedAt: new Date().toISOString(),
        version: '1.0',
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `vimarsh-memory-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      setShowExportModal(false);
      setSaveMessage('Memory data exported successfully!');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      setSaveMessage('Failed to export memory. Please try again.');
    }
  }, [memoryProfile, settings]);

  if (!isOpen) return null;

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div 
        style={styles.panel} 
        onClick={(e) => e.stopPropagation()}
        className={className}
      >
        {/* Header */}
        <div style={styles.header}>
          <h2 style={styles.title}>
            <span style={styles.titleIcon}>⚙️</span>
            Memory Settings
          </h2>
          <button style={styles.closeButton} onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={styles.content}>
          {/* Memory Status */}
          <div style={styles.section}>
            <div style={styles.statusCard}>
              <div style={styles.statusIcon}>
                {isMemoryEnabled ? '🧠' : '💤'}
              </div>
              <div style={styles.statusText}>
                <h3 style={styles.statusTitle}>
                  Memory {isMemoryEnabled ? 'Active' : 'Inactive'}
                </h3>
                <p style={styles.statusDesc}>
                  {isMemoryEnabled 
                    ? `${memoryProfile?.totalSessions || 0} sessions • ${memoryProfile?.totalMessages || 0} messages`
                    : 'Enable memory for personalized guidance'}
                </p>
              </div>
            </div>
          </div>

          {/* Privacy Mode */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Privacy Mode</h3>
            <div style={styles.privacyOptions}>
              {(Object.entries(PRIVACY_MODES) as Array<[keyof typeof PRIVACY_MODES, typeof PRIVACY_MODES[keyof typeof PRIVACY_MODES]]>).map(([mode, config]) => (
                <div
                  key={mode}
                  style={{
                    ...styles.privacyOption,
                    ...(settings.privacyMode === mode ? styles.privacyOptionSelected : {}),
                  }}
                  onClick={() => updateSetting('privacyMode', mode as MemorySettings['privacyMode'])}
                >
                  <div style={styles.privacyIcon}>{config.icon}</div>
                  <div style={styles.privacyInfo}>
                    <strong>{config.label}</strong>
                    <p style={styles.privacyDesc}>{config.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Retention Period */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Memory Retention</h3>
            <select
              value={settings.memoryRetentionDays}
              onChange={(e) => updateSetting('memoryRetentionDays', Number(e.target.value))}
              style={styles.select}
            >
              {RETENTION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <p style={styles.hint}>
              Memories older than this will be automatically archived.
            </p>
          </div>

          {/* Feature Toggles */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Features</h3>
            
            <label style={styles.toggle}>
              <input
                type="checkbox"
                checked={settings.enableCrossPersonalityMemory}
                onChange={(e) => updateSetting('enableCrossPersonalityMemory', e.target.checked)}
                style={styles.checkbox}
              />
              <span>Cross-Personality Memory</span>
              <p style={styles.toggleDesc}>
                Share context between different personalities
              </p>
            </label>

            <label style={styles.toggle}>
              <input
                type="checkbox"
                checked={settings.enableEmotionalTracking}
                onChange={(e) => updateSetting('enableEmotionalTracking', e.target.checked)}
                style={styles.checkbox}
              />
              <span>Emotional Journey Tracking</span>
              <p style={styles.toggleDesc}>
                Track emotional patterns across sessions
              </p>
            </label>

            <label style={styles.toggle}>
              <input
                type="checkbox"
                checked={settings.enableTopicSuggestions}
                onChange={(e) => updateSetting('enableTopicSuggestions', e.target.checked)}
                style={styles.checkbox}
              />
              <span>Topic Suggestions</span>
              <p style={styles.toggleDesc}>
                Get personalized conversation starters
              </p>
            </label>

            <label style={styles.toggle}>
              <input
                type="checkbox"
                checked={settings.autoSessionSummary}
                onChange={(e) => updateSetting('autoSessionSummary', e.target.checked)}
                style={styles.checkbox}
              />
              <span>Auto Session Summary</span>
              <p style={styles.toggleDesc}>
                Generate summary when session ends
              </p>
            </label>

            <label style={styles.toggle}>
              <input
                type="checkbox"
                checked={settings.notifyOnMilestones}
                onChange={(e) => updateSetting('notifyOnMilestones', e.target.checked)}
                style={styles.checkbox}
              />
              <span>Milestone Notifications</span>
              <p style={styles.toggleDesc}>
                Celebrate relationship milestones
              </p>
            </label>
          </div>

          {/* Preferred Tone */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Preferred Conversation Tone</h3>
            <div style={styles.toneGrid}>
              {TONE_OPTIONS.map((tone) => (
                <div
                  key={tone.value}
                  style={{
                    ...styles.toneOption,
                    ...(settings.preferredTone === tone.value ? styles.toneOptionSelected : {}),
                  }}
                  onClick={() => updateSetting('preferredTone', tone.value)}
                >
                  <span style={styles.toneEmoji}>{tone.emoji}</span>
                  <span style={styles.toneLabel}>{tone.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Data Management */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Data Management</h3>
            <div style={styles.dataButtons}>
              <button
                style={styles.exportButton}
                onClick={() => setShowExportModal(true)}
              >
                📥 Export Memory
              </button>
              <button
                style={styles.clearButton}
                onClick={() => setShowConfirmClear(true)}
              >
                🗑️ Clear Memory
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={styles.footer}>
          {saveMessage && (
            <div style={{
              ...styles.saveMessage,
              color: saveMessage.includes('success') ? '#22c55e' : '#ef4444',
            }}>
              {saveMessage}
            </div>
          )}
          <button
            style={{
              ...styles.saveButton,
              opacity: isSaving ? 0.7 : 1,
            }}
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>

        {/* Confirm Clear Modal */}
        {showConfirmClear && (
          <div style={styles.modal}>
            <div style={styles.modalContent}>
              <h3 style={styles.modalTitle}>⚠️ Clear All Memory?</h3>
              <p style={styles.modalText}>
                This will permanently delete all your conversation history, 
                relationship progress, and session summaries. This action cannot be undone.
              </p>
              <div style={styles.modalButtons}>
                <button
                  style={styles.cancelButton}
                  onClick={() => setShowConfirmClear(false)}
                >
                  Cancel
                </button>
                <button
                  style={styles.confirmClearButton}
                  onClick={handleClearMemory}
                >
                  Yes, Clear Everything
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Export Modal */}
        {showExportModal && (
          <div style={styles.modal}>
            <div style={styles.modalContent}>
              <h3 style={styles.modalTitle}>📥 Export Memory Data</h3>
              <p style={styles.modalText}>
                Download a JSON file containing your memory profile, 
                conversation history, and settings. This can be used 
                for backup or transfer purposes.
              </p>
              <div style={styles.modalButtons}>
                <button
                  style={styles.cancelButton}
                  onClick={() => setShowExportModal(false)}
                >
                  Cancel
                </button>
                <button
                  style={styles.exportConfirmButton}
                  onClick={handleExport}
                >
                  Download Export
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  panel: {
    background: '#ffffff',
    borderRadius: '1rem',
    maxWidth: '500px',
    width: '90%',
    maxHeight: '85vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.25rem 1.5rem',
    borderBottom: '1px solid #e2e8f0',
  },
  title: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#1e293b',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  titleIcon: {
    fontSize: '1.25rem',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '1.25rem',
    color: '#64748b',
    cursor: 'pointer',
    padding: '0.25rem',
    borderRadius: '0.25rem',
  },
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '1.5rem',
  },
  section: {
    marginBottom: '1.5rem',
  },
  sectionTitle: {
    margin: '0 0 0.75rem 0',
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#475569',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  statusCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '1rem',
    background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)',
    borderRadius: '0.75rem',
    border: '1px solid rgba(249, 115, 22, 0.2)',
  },
  statusIcon: {
    fontSize: '2rem',
  },
  statusText: {
    flex: 1,
  },
  statusTitle: {
    margin: 0,
    fontSize: '1rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  statusDesc: {
    margin: '0.25rem 0 0 0',
    fontSize: '0.8rem',
    color: '#64748b',
  },
  privacyOptions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  privacyOption: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.75rem',
    padding: '0.875rem',
    background: '#f8fafc',
    borderRadius: '0.5rem',
    border: '2px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  privacyOptionSelected: {
    background: 'rgba(249, 115, 22, 0.1)',
    borderColor: '#f97316',
  },
  privacyIcon: {
    fontSize: '1.25rem',
  },
  privacyInfo: {
    flex: 1,
  },
  privacyDesc: {
    margin: '0.25rem 0 0 0',
    fontSize: '0.75rem',
    color: '#64748b',
    lineHeight: '1.4',
  },
  select: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #e2e8f0',
    fontSize: '0.9rem',
    color: '#1e293b',
    backgroundColor: '#ffffff',
    cursor: 'pointer',
  },
  hint: {
    margin: '0.5rem 0 0 0',
    fontSize: '0.75rem',
    color: '#94a3b8',
  },
  toggle: {
    display: 'flex',
    flexDirection: 'column',
    padding: '0.75rem 0',
    borderBottom: '1px solid #f1f5f9',
    cursor: 'pointer',
  },
  checkbox: {
    marginRight: '0.75rem',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  toggleDesc: {
    margin: '0.25rem 0 0 26px',
    fontSize: '0.75rem',
    color: '#94a3b8',
  },
  toneGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '0.5rem',
  },
  toneOption: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '0.75rem',
    background: '#f8fafc',
    borderRadius: '0.5rem',
    border: '2px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  toneOptionSelected: {
    background: 'rgba(249, 115, 22, 0.1)',
    borderColor: '#f97316',
  },
  toneEmoji: {
    fontSize: '1.5rem',
    marginBottom: '0.25rem',
  },
  toneLabel: {
    fontSize: '0.7rem',
    fontWeight: '500',
    color: '#475569',
    textAlign: 'center' as const,
  },
  dataButtons: {
    display: 'flex',
    gap: '0.75rem',
  },
  exportButton: {
    flex: 1,
    padding: '0.75rem',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '0.5rem',
    color: '#475569',
    fontSize: '0.9rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  clearButton: {
    flex: 1,
    padding: '0.75rem',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '0.5rem',
    color: '#dc2626',
    fontSize: '0.9rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  footer: {
    padding: '1rem 1.5rem',
    borderTop: '1px solid #e2e8f0',
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    gap: '1rem',
  },
  saveMessage: {
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  saveButton: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
    border: 'none',
    borderRadius: '0.5rem',
    color: '#ffffff',
    fontSize: '0.9rem',
    fontWeight: '600',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(249, 115, 22, 0.3)',
    transition: 'all 0.2s',
  },
  modal: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '1rem',
  },
  modalContent: {
    background: '#ffffff',
    borderRadius: '0.75rem',
    padding: '1.5rem',
    maxWidth: '350px',
    textAlign: 'center' as const,
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)',
  },
  modalTitle: {
    margin: '0 0 0.75rem 0',
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  modalText: {
    margin: '0 0 1.25rem 0',
    fontSize: '0.875rem',
    color: '#64748b',
    lineHeight: '1.5',
  },
  modalButtons: {
    display: 'flex',
    gap: '0.75rem',
  },
  cancelButton: {
    flex: 1,
    padding: '0.625rem',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '0.5rem',
    color: '#475569',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
  },
  confirmClearButton: {
    flex: 1,
    padding: '0.625rem',
    background: '#dc2626',
    border: 'none',
    borderRadius: '0.5rem',
    color: '#ffffff',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
  },
  exportConfirmButton: {
    flex: 1,
    padding: '0.625rem',
    background: 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
    border: 'none',
    borderRadius: '0.5rem',
    color: '#ffffff',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
  },
};

export default MemorySettingsPanel;
