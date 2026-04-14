# User Experience Specification: Vimarsh Platform

## 1. Design Philosophy
"Authentic Wisdom Through Intuitive Design". Vimarsh UX aligns distinct domain personalities through a singular, Apple-inspired layout vocabulary while shedding excessive inline formatting loops.

## 2. Routing & Architecture UX
* **Unbounded Landing Page**: Standard index route `/` acts strictly as an unauthenticated Marketing presentation. The `LandingPage.tsx` will explicitly *not* auto-redirect on session validity, allowing users to voluntarily transition via "Go to Dashboard".
* **Modular Interface Components**: The central `GuidanceInterface.tsx` uses a centralized `GuidanceInterface.css` module file preventing CSS bloat. Navigation bars unify secondary tasks (like telemetry and memory status) into unified off-canvas menus ensuring a clean "Conversational Canvas" strictly honoring the selected AI persona.

## 3. Visual Domain Theming
1. **Spiritual (`#f97316`)**: Lotus animations, sacred saffron and meditation gold highlighting. 
2. **Scientific (`#0066CC`)**: Lab silver aesthetics with mathematical notation highlighting.
3. **Leadership (`#DC2626`)**: Heritage and gravitas with robust typography.
4. **Philosophical (`#6B7280`)**: Stoic greys, margin-based reading layouts.

## 4. Growth & Gamification Flow
* **Intelligent Onboarding**: 3-step intent discovery funnel pairing users to an optimal philosophical guide within 60 seconds of signing up.
* **Dynamic Streaks & Wisdom Badges**: Engagement is measured chronologically with visualizations encouraging user return patterns (e.g. "Consistent Seeker" badges, "Krishna Devotee" achievements).
* **The Wisdom Dashboard**: Complete panoramic view of "relationship levels" per personality, historical exploration charts, and contextual guidance recommendations. 
