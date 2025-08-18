# Component Update Templates for Vimarsh Design System

## Template 1: Modal Components (PersonalitySelector, Settings, etc.)

### Design Pattern:
```tsx
// Vimarsh-style modal overlay
const modalOverlay = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'rgba(0, 0, 0, 0.4)',
  backdropFilter: 'blur(20px)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
  padding: '2rem'
};

// Vimarsh-style modal content
const modalContent = {
  background: '#ffffff',
  borderRadius: '20px',
  maxWidth: '900px',
  width: '100%',
  maxHeight: '80vh',
  overflowY: 'auto',
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
  border: '1px solid #e5e7eb',
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
};

// Vimarsh-style header
const modalHeader = {
  padding: '1.5rem 2rem',
  borderBottom: '1px solid #f3f4f6',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: '#ffffff',
  borderRadius: '20px 20px 0 0'
};
```

## Template 2: Card Components (ConversationHistory, ResponseDisplay, etc.)

### Design Pattern:
```tsx
// Vimarsh-style card
const cardStyle = {
  background: '#ffffff',
  borderRadius: '12px',
  padding: '1.25rem',
  border: '1px solid #e5e7eb',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  transition: 'all 0.2s ease',
  cursor: 'pointer'
};

// Hover effect
const cardHover = {
  transform: 'translateY(-1px)',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  borderColor: '#d1d5db'
};

// Card header pattern
const cardHeader = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem',
  marginBottom: '0.75rem',
  paddingBottom: '0.75rem',
  borderBottom: '1px solid #f3f4f6'
};
```

## Template 3: Button Components

### Design Pattern:
```tsx
// Primary button (brand)
const primaryButton = {
  background: 'linear-gradient(135deg, #f97316, #f59e0b)',
  color: 'white',
  border: 'none',
  padding: '0.75rem 1.5rem',
  borderRadius: '0.75rem',
  fontSize: '1rem',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  boxShadow: '0 4px 12px rgba(249, 115, 22, 0.3)',
  fontFamily: 'inherit'
};

// Secondary button
const secondaryButton = {
  background: '#ffffff',
  color: '#1d1d1f',
  border: '1px solid #e5e7eb',
  padding: '0.75rem 1.5rem',
  borderRadius: '0.75rem',
  fontSize: '1rem',
  fontWeight: 500,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  fontFamily: 'inherit'
};

// Interactive button (Vimarsh blue)
const interactiveButton = {
  background: '#007aff',
  color: 'white',
  border: 'none',
  padding: '0.75rem 1.5rem',
  borderRadius: '0.75rem',
  fontSize: '1rem',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  boxShadow: '0 4px 12px rgba(0, 122, 255, 0.25)',
  fontFamily: 'inherit'
};
```

## Template 4: Input Components

### Design Pattern:
```tsx
// Vimarsh-style input container
const inputContainer = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem',
  background: '#f8fafc',
  border: '1px solid #e2e8f0',
  borderRadius: '1rem',
  padding: '0.5rem',
  transition: 'border-color 0.2s ease'
};

// Focus state
const inputFocus = {
  borderColor: '#007aff',
  boxShadow: '0 0 0 3px rgba(0, 122, 255, 0.1)'
};

// Input field
const inputField = {
  flex: 1,
  border: 'none',
  background: 'none',
  padding: '0.75rem 1rem',
  fontSize: '1rem',
  outline: 'none',
  fontFamily: 'inherit',
  color: '#1e293b'
};
```

## Template 5: List Components (ConversationHistory, etc.)

### Design Pattern:
```tsx
// List container
const listContainer = {
  background: '#ffffff',
  borderRadius: '12px',
  border: '1px solid #e5e7eb',
  overflow: 'hidden'
};

// List item
const listItem = {
  padding: '1rem 1.25rem',
  borderBottom: '1px solid #f3f4f6',
  transition: 'background-color 0.2s ease',
  cursor: 'pointer'
};

// List item hover
const listItemHover = {
  background: '#f8fafc'
};

// List item active
const listItemActive = {
  background: '#f0f9ff',
  borderLeft: '3px solid #007aff'
};
```

## Template 6: Message Bubbles (GuidanceInterface)

### Design Pattern:
```tsx
// User message
const userMessage = {
  alignSelf: 'flex-end',
  maxWidth: '70%',
  background: '#007aff',
  color: 'white',
  padding: '0.75rem 1rem',
  borderRadius: '1.125rem',
  fontSize: '1rem',
  lineHeight: 1.4,
  wordWrap: 'break-word',
  boxShadow: '0 1px 2px rgba(0, 122, 255, 0.2)'
};

// Assistant message
const assistantMessage = {
  alignSelf: 'flex-start',
  maxWidth: '85%',
  background: '#f1f5f9',
  color: '#1e293b',
  padding: '1rem 1.25rem',
  borderRadius: '1.125rem',
  fontSize: '1rem',
  lineHeight: 1.5,
  border: '1px solid #e2e8f0',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
};
```

## Template 7: Status Indicators

### Design Pattern:
```tsx
// Status badge
const statusBadge = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.25rem',
  padding: '0.25rem 0.75rem',
  borderRadius: '9999px',
  fontSize: '0.75rem',
  fontWeight: 500
};

// Success status
const successStatus = {
  ...statusBadge,
  background: '#d1fae5',
  color: '#065f46'
};

// Warning status
const warningStatus = {
  ...statusBadge,
  background: '#fef3c7',
  color: '#92400e'
};

// Error status
const errorStatus = {
  ...statusBadge,
  background: '#fee2e2',
  color: '#991b1b'
};
```

## Template 8: Loading States

### Design Pattern:
```tsx
// Vimarsh-style spinner
const spinner = {
  width: '20px',
  height: '20px',
  border: '2px solid #f3f4f6',
  borderTop: '2px solid #007aff',
  borderRadius: '50%',
  animation: 'spin 1s linear infinite'
};

// Loading dots
const loadingDots = {
  display: 'flex',
  gap: '0.25rem',
  alignItems: 'center'
};

const loadingDot = {
  width: '6px',
  height: '6px',
  borderRadius: '50%',
  background: '#9ca3af',
  animation: 'pulse 1.5s ease-in-out infinite'
};
```

## Common CSS Classes to Add

```css
/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hover effects */
.hover-lift:hover {
  transform: translateY(-1px);
}

.hover-scale:hover {
  transform: scale(1.02);
}

/* Focus states */
.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

/* Transitions */
.transition-all {
  transition: all 0.2s ease;
}

.transition-colors {
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
```

## Migration Checklist for Each Component

### Before Starting:
- [ ] Backup existing component
- [ ] Review current functionality
- [ ] Identify key user interactions
- [ ] Note any custom styling needs

### During Migration:
- [ ] Update background colors to white/gray variants
- [ ] Replace gradients with subtle shadows
- [ ] - Update border radius to match Vimarsh standards (12px, 16px, 20px)
- [ ] Implement consistent spacing using 8px grid
- [ ] Update typography to system fonts
- [ ] Add smooth transitions (0.2s ease)
- [ ] Implement proper hover states
- [ ] Ensure mobile responsiveness

### After Migration:
- [ ] Test all interactive elements
- [ ] Verify mobile responsiveness
- [ ] Check accessibility (contrast, focus states)
- [ ] Validate against design system
- [ ] Update component documentation
