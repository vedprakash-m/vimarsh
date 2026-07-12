# UX Specification: Vimarsh

| Field | Value |
|---|---|
| **Product** | Vimarsh — AI-Powered Multi-Personality Conversational Wisdom Platform |
| **Version** | 2.2 (April 2026) |
| **Philosophy** | **Invisible UI** — Precision through subtraction. |
| **Design System** | Inter & Merriweather Hybrid with 6 domain-specific themes |

---

## 1. Design Philosophy

### Core Principles

1. **Invisible UI (Precision through Subtraction)** — We strip away everything that does not serve the soul of the conversation. No aggressive modals, no layout-shifting elements, and zero "pop-up fatigue".
2. **Typography-First Canvas** — Using the **Inter** (sans-serif) and **Merriweather** (serif) font families to create a balance between modern utility and timeless wisdom.
3. **Decoupled Discovery** — Allowing users to read and interact with "Wisdom of the Day" fragments before full authentication, reducing barriers to first-interaction.
4. **Fluid Streaming** — Leveraging SSE to reduce the Time-to-First-Token (TTFT), making the interface feel "alive" and breathing as thoughts are generated.

### Design System Stack

| Layer | File | Purpose |
|---|---|---|
| **Core Tokens** | `tokens.css` | Canonical semantic variables (typography, spacing, semantic colors) powering Tailwind |
| **Component Styles** | Tailwind CSS | Tailwind utility classes |

**Aurora Ink Aesthetic:** A dark-default (or warm-light) canvas where personality domains are expressed through subtle light/glows rather than flat color.
**Ink Gathering:** The magical, domain-tinted 3-dot animation representing an AI's "thinking" state.

### Typography

- **Primary Font Stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`
- **Font Weights:** 400 (body), 500 (medium), 600 (semibold), 700 (headings)
- **Font Scale:** 0.65rem → 0.875rem → 1rem → 1.25rem → 1.5rem hierarchy
- **Letter Spacing:** 0.5px for uppercase labels (e.g., domain badges)

### Spacing & Grid

```
4px  (0.25rem) — Micro spacing (icon gaps)
8px  (0.5rem)  — Tight spacing (within groups)
12px (0.75rem) — Comfortable spacing (component padding)
16px (1rem)    — Spacious spacing (section separators)
24px (1.5rem)  — Section spacing
32px (2rem)    — Major section breaks
```

### Elevation (Shadows)

```
Level 0: none (flat)
Level 1: 0 1px 3px rgba(0, 0, 0, 0.05) — Cards, subtle lift
Level 2: 0 2px 8px rgba(color, 0.3)     — Personality badges, active elements
Level 3: 0 4px 12px rgba(color, 0.4)    — Modals, overlays
Level 4: 0 8px 24px rgba(0, 0, 0, 0.15) — Floating action buttons
```

### Transitions

- **Standard:** `all 0.2s cubic-bezier(0.4, 0, 0.2, 1)` — Most interactive elements
- **Hover Lift:** `transform: translateY(-1px)` with background color change
- **Page Transitions:** Fade-in via React Suspense fallback (spinner → content)

---

## 2. Information Architecture

### Site Map

```
vimarsh.vedmishra.com
├── / (Landing Page — public)
│   ├── Hero + Value Proposition
│   ├── Feature Showcase
│   ├── Personality Preview Grid
│   ├── Social Proof + CTA
│   └── Sign In (MSAL redirect)
│
├── /guidance (Core Conversation — protected)
│   ├── Top Navigation Header
│   │   ├── Logo + Title
│   │   ├── Active Personality Badge (domain-colored)
│   │   ├── Engagement Metrics (Memory + Streak)
│   │   └── Actions (Settings, Admin, Logout)
│   ├── Personality Selector (modal overlay)
│   ├── Wisdom of the Day (collapsible)
│   ├── Message Thread (scrollable)
│   └── Input Area (text + voice + send)
│
├── /wisdom/archive (Conversation Archive — protected)
├── /memory (Memory Dashboard — protected)
├── /progress (Progress Dashboard — protected)
├── /settings (User Settings — protected)
│   ├── My Profile tab
│   ├── Experience tab
│   ├── Notifications tab
│   ├── Memory & Privacy tab
│   └── Account tab
│
├── /admin (Admin Dashboard — protected, admin-only)
├── /share/:shareId (Shared Wisdom Card — public)
└── /auth/callback (Authentication handler)
```

### Navigation Model

| Element | Behavior |
|---|---|
| **Top Nav** | Persistent header on `/guidance` — Logo, personality badge, metrics, settings/logout |
| **Personality Selector** | Modal overlay triggered from personality badge click |
| **Settings** | Profile tab in bottom nav (mobile) or top nav (desktop) → `/settings` page |
| **Admin** | Icon in top nav (visible only to admin users) → `/admin` dashboard (Linear-style cockpit with Prompt Studio) |
| **Back Navigation** | Browser back button + in-app navigation via React Router |

---

## 3. Screen Specifications

### 3.1 Landing Page (`/`)

**Purpose:** Public-facing marketing page that converts visitors into authenticated users.  
**Component:** `LandingPage.tsx` (57.3 KB)

#### Layout

```
┌────────────────────────────────────────────────────┐
│                   HERO SECTION                      │
│  "Seek Wisdom from History's Greatest Minds"       │
│                                                     │
│  [Animated personality avatars rotating]            │
│                                                     │
│        [Sign In with Microsoft] CTA                 │
├────────────────────────────────────────────────────┤
│              FEATURE SHOWCASE GRID                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│  │ 25   │ │ RAG  │ │Voice │ │Memory│              │
│  │Minds │ │Cited │ │Mode  │ │Track │              │
│  └──────┘ └──────┘ └──────┘ └──────┘              │
├────────────────────────────────────────────────────┤
│           PERSONALITY PREVIEW GRID                  │
│  6 domain-organized sections with personality cards│
├────────────────────────────────────────────────────┤
│              SOCIAL PROOF + FOOTER                  │
└────────────────────────────────────────────────────┘
```

#### Behavior
- **Unauthenticated user:** Renders full marketing page with Sign In CTA
- **Authenticated user:** Redirects to `/guidance` after 500ms stabilization delay (prevents auth race condition with ProtectedRoute)
- **Onboarding:** New users trigger 3-step onboarding wizard before redirect

### 3.2 Onboarding Flow (3-Step Wizard)

**Target:** First meaningful conversation in < 60 seconds.

```
Step 1: Intent Discovery                Step 2: Personality Match              Step 3: First Question Catalyst
┌─────────────────────┐                ┌─────────────────────┐                ┌─────────────────────┐
│ "What brings you    │                │ "Based on your      │                │ "Here's a great     │
│  to Vimarsh today?" │                │  interest, we       │                │  first question     │
│                     │                │  recommend..."      │                │  for [Personality]:" │
│ ○ Spiritual growth  │  ───────▶      │                     │  ───────▶      │                     │
│ ○ Philosophy        │                │ [Top 3 personality  │                │ [Pre-crafted prompt]│
│ ○ Leadership        │                │  cards with domain  │                │                     │
│ ○ Science           │                │  colors]            │                │ [Start Conversation]│
│ ○ Literature        │                │                     │                │                     │
│ ○ Just exploring    │                │ [Select one]        │                │ [Ask my own]        │
└─────────────────────┘                └─────────────────────┘                └─────────────────────┘
```

### 3.3 Guidance Interface (`/guidance`)

**Purpose:** The primary conversation UI — where users interact with wisdom personalities.  
**Component:** `GuidanceInterface.tsx` (56.6 KB)

#### Top Navigation Header

```
┌────────────────────────────────────────────────────────────────────┐
│  🕉️ Vimarsh  ┊  [👤 Krishna │ SPIRITUAL]  │  [💎 3] [🔥 5]  │  [⚙️] [⚙️] [↗️]  │
│  (Logo)         (Personality Badge)           (Metrics)          (Actions)         │
└────────────────────────────────────────────────────────────────────┘

Visual Hierarchy: PRIMARY ──────────────── SECONDARY ──── TERTIARY ──────
```

**Design Patterns:**
- **Primary:** Rich background with domain color, border (`1.5px solid domainColor`), and shadow (`0 2px 8px`)
- **Secondary:** Subtle metrics with hover effects, no borders
- **Tertiary:** Ghost buttons (transparent background, muted gray `#64748b`)
- **Visual Separators:** Gradient dividers between groups (`linear-gradient(to bottom, transparent, #e5e7eb, transparent)`, 1px width, 0.5 opacity)
- **Semantic Hover Colors:** Settings (blue `#f1f5f9`), Admin (amber `#fef3c7`), Logout (red `#fef2f2`)
- **Touch Targets:** Minimum 44×44px (Apple HIG compliant)

#### Conversation Area

```
┌────────────────────────────────────────────────────┐
│  Wisdom of the Day (collapsible banner)            │
│  "The unexamined life is not worth living."        │
│  — Socrates                                        │
├────────────────────────────────────────────────────┤
│                                                     │
│  [User Message Bubble]                    (right)  │
│                                                     │
│  [AI Response Card]                       (left)   │
│  ┌──────────────────────────────────┐             │
│  │ [Personality Avatar + Name]      │             │
│  │                                   │             │
│  │ Response text with **markdown**   │             │
│  │ support and inline citations [1]  │             │
│  │                                   │             │
│  │ ┌─────────────────────────┐      │             │
│  │ │ 📖 Sources:             │      │             │
│  │ │ [1] Meditations 2.11    │      │             │
│  │ │ [2] Meditations 4.3     │      │             │
│  │ └─────────────────────────┘      │             │
│  │                                   │             │
│  │ [🔊 Play] [📋 Copy] [🔗 Share]  │             │
│  │ [⭐ Bookmark]                    │             │
│  └──────────────────────────────────┘             │
│                                                     │
│  ... (scrollable message history)                  │
│                                                     │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │  [🎤 Voice] │ Ask your question...  │ [Send ▶]│  │
│  │             │ (auto-resize textarea) │        │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

**AI Response Card Features:**
- **Markdown Rendering:** Full markdown support via `react-markdown` — headers, lists, bold, italic, code blocks
- **Citation Cards:** Expandable source reference list with document title, chapter/verse when available
- **Action Bar:** Play Voice, Copy to Clipboard, Share (social platforms), Bookmark (with optional notes)
- **Loading State:** Animated typing indicator with personality avatar

#### Personality Selector Modal

```
┌─────────────────────────────────────────────┐
│  ✕  Choose Your Guide                       │
│                                              │
│  [🔍 Search personalities...]               │
│                                              │
│  🕉️ SPIRITUAL                               │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐       │
│  │Kri │ │Bud │ │Jes │ │Rum │ │Viv │       │
│  │shna│ │dha │ │us  │ │i   │ │eka │       │
│  └────┘ └────┘ └────┘ └────┘ └────┘       │
│                                              │
│  💭 PHILOSOPHICAL                            │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐│
│  │Mar │ │Lao │ │Con │ │Ari │ │Pla │ │Soc ││
│  │cus │ │Tzu │ │fu  │ │sto │ │to  │ │rat ││
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘│
│                                              │
│  🏛️ LEADERSHIP                              │
│  ... (6 cards)                               │
│                                              │
│  🔬 SCIENTIFIC                               │
│  ... (5 cards)                               │
│                                              │
│  📚 LITERARY                                 │
│  ... (2 cards)                               │
│                                              │
│  🧠 PSYCHOLOGY                               │
│  ... (1 card)                                │
└─────────────────────────────────────────────┘
```

**Card Design:**
- Domain-specific background gradient
- Personality name + domain label
- Document count indicator
- Active selection state with elevated shadow
- ⭐ Favorite indicator (if configured in settings)

### 3.4 User Settings (`/settings`)

**Component:** `UserSettings.tsx` (page wrapper) + `components/Settings/` directory  
**Pattern:** Horizontal tab bar (desktop) / Vertical list (mobile) with 5 tabs

#### Tab: My Profile
```
┌─────────────────────────────────────────────┐
│  [Profile]  Experience  Notifications       │
│             Memory    Account               │
├─────────────────────────────────────────────┤
│  ┌─────────┐  Name: Spiritual Seeker       │
│  │ Avatar  │  Email: seeker@vimarsh.app     │
│  │  [MS]   │  Member since: Jan 2025       │
│  └─────────┘                                │
│                                              │
│  ── Journey Statistics ──────────────────    │
│  🔥 Current Streak: 14 days                 │
│  📊 Total Conversations: 87                 │
│  🏆 Achievements: 5/20 unlocked            │
│  📈 Wisdom Level: Student                   │
│                                              │
│  ── AI Usage ────────────────────────────    │
│  This Month: $2.15 covered for you          │
│  [████████░░░░░░░░] 42% of limit            │
│  Status: 🟢 Well Within Limits              │
│                                              │
│  ── Domain Exploration ──────────────────    │
│  Spiritual:     [████████████] 35            │
│  Philosophical: [████████]     22            │
│  Scientific:    [████]         12            │
│  Leadership:    [████]         10            │
│  Literary:      [██]            5            │
│  Psychology:    [█]             3            │
│                                              │
│  Quick Links:                                │
│  [📚 Archive] [🧠 Memory] [📊 Progress]    │
└─────────────────────────────────────────────┘
```

#### Tab: Experience
- **Conversation Style:** Brief / Balanced / Detailed (radio group with description)
- **Language:** English / Hindi (dropdown)
- **Formality:** Very Formal / Respectful / Friendly / Casual (radio group)
- **Favorite Personalities:** Grid selector (max 5, with domain color indicators)
- **Appearance:** Theme (Light/Dark/Auto), Text Size (Small/Medium/Large), Reduce Animations (toggle), Show Citations (toggle)

#### Tab: Notifications
- **Master Toggle:** Enable/disable all notifications
- **Daily Wisdom:** Toggle + preferred time picker (HH:MM, 24h) with presets (Morning 9:00, Afternoon 14:00, Evening 18:00, Night 21:00)
- **Timezone:** Dropdown with 9 major timezone options
- **Quiet Hours:** Enable toggle + start/end time pickers (supports midnight span)
- **Notification Types:** Individual toggles for Daily Wisdom, Streak Reminders, Achievements, Weekly Summary
- **Test Notification:** Button to trigger browser notification permission + sample notification

#### Tab: Memory & Privacy
- **Memory Features:** 4 toggles — Remember Conversations, Connect Insights, Track Emotions, Suggest Topics
- **Privacy Mode:** Standard / Private / Minimal (radio with impact matrix)
- **Data Transparency:** Allow Analytics (default on), Allow Research (default off)
- **Data Retention:** 30 / 90 / 180 / 365 days (dropdown)
- **Data Management:** [Export Data] and [Clear History] buttons with confirmation modals

#### Tab: Account
- **Subscription:** Free tier display with usage progress bars (monthly conversations, daily messages)
- **Premium Teaser:** Coming soon card with feature preview
- **Security:** Email (linked to MS account), Password (redirect to MS account), 2FA status
- **Account Actions:** [Log Out] with confirmation, [Delete Account] with email-match confirmation + 30-day recovery notice

#### Auto-Save Behavior
- **500ms debounce** after last input change
- **Optimistic UI** — Changes appear instantly
- **Status indicators:** ⏳ Saving... → ✓ Saved (3s fade) → ✗ Failed (with Retry button)
- **Manual-only actions:** Account deletion, data export, clear history (require explicit user confirmation)

### 3.5 Progress Dashboard (`/progress`)

**Wisdom Journey Overview:**
- Streak calendar (GitHub-style heatmap)
- Domain exploration radar chart
- Personality relationship levels (Stranger → Acquaintance → Student → Devotee)
- Achievement badge gallery with locked/unlocked states
- Next milestone suggestions

### 3.6 Wisdom Archive (`/wisdom/archive`)

- Conversation list organized by date and personality
- Full-text search across past conversations
- Bookmark management (view, add notes, remove)
- Personality filter and date range filter
- Conversation replay with full message thread

### 3.7 Memory Dashboard (`/memory`)

- Per-personality relationship status visualization
- Insight timeline (discoveries and connections across sessions)
- Conversation context summary
- Memory strength indicator (active memories, connection count)

### 3.8 Share View (`/share/:shareId`)

**Public page for shared wisdom cards:**
- Personality avatar and name with domain badge
- Wisdom text with styled quote formatting
- Source citation
- CTA to visit Vimarsh and start own conversation
- OG metadata for social platform previews (1200×630 image)

---

## 4. Voice Interface UX

### 4.1 Input (Speech-to-Text)

| Property | Specification |
|---|---|
| **API** | Web Speech API (browser-native) |
| **Trigger** | Microphone button in input area |
| **Visual Feedback** | Pulsing red mic icon during recording |
| **Language** | Follows user language setting (en-US / hi-IN) |
| **Fallback** | Graceful degradation to text-only on unsupported browsers |

### 4.2 Output (Text-to-Speech)

| Property | Specification |
|---|---|
| **Service** | Azure Neural TTS with SSML markup |
| **Voices** | 25 personality-specific voice configurations |
| **Controls** | Play / Pause / Stop in response action bar |
| **SSML Styles** | Per-personality emotional styles: empathetic, calm, gentle, lyrical, cheerful, serious, hopeful, excited |
| **Rate Range** | 0.78x (Lao Tzu) to 0.95x (Vivekananda, Tesla) |
| **Autoplay** | User-triggered only (never autoplay) |

### 4.3 Voice Personality Selector

**Component:** `PersonalityVoiceSelector.tsx`  
Allows users to preview personality voices before selecting, with:
- Voice sample playback (short quote in personality's voice)
- Style/rate/pitch information display
- Domain-grouped organization

---

## 5. Responsive Design

### Breakpoints

| Breakpoint | Target | Layout Adjustments |
|---|---|---|
| **≤ 480px** | Small mobile | Icon-only nav buttons, personality badge max 120px with ellipsis, hide domain labels |
| **481–768px** | Mobile/Tablet | Selective text labels, reduced padding/gaps, 36×36px action buttons |
| **769–1024px** | Tablet/Small desktop | Full nav with labels, two-column settings layout |
| **> 1024px** | Desktop | Full navigation, multi-column layouts, hover states, visual separators |

### Mobile-Specific Patterns

| Pattern | Implementation |
|---|---|
| **Touch Targets** | Minimum 44×44px for all interactive elements |
| **Input Area** | Full-width textarea with auto-resize; large Send button |
| **Personality Selector** | Full-screen modal (bottom sheet on small screens) |
| **Settings Tabs** | Vertical list with icons instead of horizontal tabs |
| **Gestures** | Swipe left/right for tab navigation in settings |
| **Keyboard** | `inputMode` optimization for different field types |

### PWA Experience

| Feature | Implementation |
|---|---|
| **Install Prompt** | Custom in-app install banner with dismiss memory |
| **Home Screen Icon** | App icon with personality-themed splash screen |
| **Offline Support** | Service worker caches static assets + recent conversations |
| **Background Sync** | Auto-save queues when offline; syncs on reconnection |
| **Update Prompt** | Workbox-powered update banner when new version available |

---

## 6. Loading & Empty States

### Loading States

| Context | Component | Behavior |
|---|---|---|
| **App Init** | `AppleLoadingSpinner` | Centered spinner with "Loading wisdom guidance..." text, orange accent |
| **Route Loading** | React Suspense fallback → `AppleLoadingSpinner` | Same spinner during lazy-load |
| **Auth Transition** | ProtectedRoute circuit breaker | "Synchronizing authentication..." with subtle spinner (cooldown state) |
| **AI Response** | Typing indicator | Personality avatar with animated dots (3-dot pulse) |
| **Settings Save** | Toast notification | ⏳ "Saving..." spinner → ✓ "Saved" green check (3s auto-dismiss) |

### Error States

| Scenario | Display | Recovery |
|---|---|---|
| **Auth Loop Detected** | "Authentication Loop Detected" full-screen error | "Refresh Page" button |
| **API Failure** | Toast notification with error message | Automatic retry with exponential backoff; manual "Retry" button |
| **AI Generation Failure** | Inline error card in conversation thread | "Try Again" button; fallback template response |
| **Settings Save Failure** | Red toast "Failed to Save" | "Retry" button; changes revert to last saved state |
| **Offline** | Subtle banner "You're offline — changes will sync when connected" | Auto-recovery on reconnection |

### Empty States

| Context | Display |
|---|---|
| **No Conversations** | Welcome message + personality suggestion with "Start a conversation" CTA |
| **No Bookmarks** | "You haven't bookmarked any wisdom yet" + hint about how to bookmark |
| **No Achievements** | "Your journey has just begun" with first-achievable badge highlighted |

---

## 7. Accessibility

### WCAG 2.1 AA Compliance

| Criterion | Implementation |
|---|---|
| **Color Contrast** | All text meets AA minimums (4.5:1 for body, 3:1 for large text) |
| **Keyboard Navigation** | Tab order follows logical reading flow; all actions keyboard-accessible |
| **Focus Indicators** | Browser default focus rings preserved; custom focus states for domain-themed elements |
| **ARIA Labels** | All buttons have descriptive `title` and `aria-label` attributes |
| **Touch Targets** | Minimum 44×44px per Apple HIG / WCAG 2.5.5 |
| **Reduced Motion** | `reduce_animations` user preference; `prefers-reduced-motion` CSS media query supported |
| **Text Resizing** | Text Size setting (Small/Medium/Large) in Experience tab |
| **Screen Reader** | Semantic HTML5 elements; proper heading hierarchy (single `<h1>` per page) |
| **Skip Links** | Skip-to-content link for keyboard users |

---

## 8. Domain Theming

Each of the 6 domains has a distinct visual identity applied when a personality from that domain is active:

### Color System

| Domain | Icon | Primary | Accent | Background | Border |
|---|---|---|---|---|---|
| **Spiritual** | 🕉️ | Amber `#f59e0b` | Orange `#f97316` | Warm cream `#fef3c7` | Amber `#f59e0b` |
| **Philosophical** | 💭 | Indigo `#6366f1` | Violet `#8b5cf6` | Soft lavender `#eef2ff` | Indigo `#6366f1` |
| **Leadership** | 🏛️ | Emerald `#10b981` | Green `#22c55e` | Mint `#ecfdf5` | Emerald `#10b981` |
| **Scientific** | 🔬 | Blue `#3b82f6` | Cyan `#06b6d4` | Sky `#eff6ff` | Blue `#3b82f6` |
| **Literary** | 📚 | Rose `#f43f5e` | Pink `#ec4899` | Blush `#fff1f2` | Rose `#f43f5e` |
| **Psychology** | 🧠 | Teal `#14b8a6` | Cyan `#06b6d4` | Sea foam `#f0fdfa` | Teal `#14b8a6` |

### Application Points

Domain colors are applied to:
- Personality badge in top navigation (background, border, shadow)
- Personality selector card backgrounds
- Response card accent lines
- Achievement badge borders
- Settings personality grid highlights
- Wisdom of the Day accent color

### Component: DomainThemeManager

**File:** `components/DomainThemeManager.tsx`  
Listens to active personality changes and updates CSS custom properties globally:
```css
:root {
  --domain-primary: var(--spiritual-primary);
  --domain-bg: var(--spiritual-bg);
  --domain-border: var(--spiritual-border);
}
```

---

## 9. Social Sharing Design

### Wisdom Quote Cards

**Dimensions:**
- Feed format: 1200×630px (Facebook/LinkedIn/Twitter)
- Story format: 1080×1920px (Instagram/WhatsApp)

**Card Layout:**
```
┌────────────────────────────┐
│  [Domain color gradient bg] │
│                              │
│  "The unexamined life is    │
│   not worth living."        │
│                              │
│           — Socrates         │
│           📚 Meditations 2.1 │
│                              │
│  🕉️ vimarsh.vedmishra.com  │
└────────────────────────────┘
```

**Share Channels:**
- Twitter (with pre-formatted tweet text + card image)
- Facebook (OG metadata)
- LinkedIn (professional formatting)
- WhatsApp (link + preview image)
- Email (HTML-formatted quote)
- Clipboard (plain text)

### OG Metadata

Server-rendered by `OGImageService` for rich social previews:
- `og:title` — Personality name + "on topic"
- `og:description` — Quote excerpt (≤ 200 characters)
- `og:image` — Server-generated card image URL
- `og:type` — `article`

---

## 10. Engagement Gamification UX

### Streak System

| Element | Display | Behavior |
|---|---|---|
| **Streak Counter** | 🔥 + number in top nav | Increments on daily engagement (any conversation) |
| **Streak Calendar** | Heatmap in Progress Dashboard | GitHub-contribution-style annual view |
| **Streak Protection** | 1 free pass per week | Visual indicator when protection available/used |
| **Milestone Badges** | 7 / 30 / 100 / 365 days | Celebration modal on milestone reach |

### Achievement System

| Category | Examples |
|---|---|
| **Engagement** | First Conversation, 10 Conversations, 50 Conversations |
| **Streak** | 7-Day Streak, 30-Day Streak, 100-Day Streak |
| **Exploration** | Domain Explorer (conversation in all 6 domains), Personality Collector |
| **Social** | First Share, Wisdom Spreader (10 shares) |
| **Special** | Night Owl (conversation after midnight), Early Bird (before 6am) |

### Wisdom Levels

```
Seeker (0-9 conversations)
  → Student (10-49)
    → Practitioner (50-149)
      → Scholar (150-499)
        → Sage (500-999)
          → Master (1000+)
```

---

*Cross-reference: [PRD.md](./PRD.md) for product requirements and feature scope · [Tech-Spec.md](./Tech-Spec.md) for architecture and implementation details*
