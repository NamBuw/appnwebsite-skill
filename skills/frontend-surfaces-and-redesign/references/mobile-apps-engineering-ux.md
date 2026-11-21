# Mobile Apps Engineering and UX

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module covers native and cross-platform mobile product engineering across SwiftUI (iOS), Jetpack Compose (Android), React Native with Expo Router, Flutter, and responsive mobile web/PWA. It preserves native platform ergonomics (iOS Human Interface Guidelines and Android Material 3), platform-native icon systems (SF Symbols on iOS and Android native vector drawables on Android, while enforcing web font/icon bans on mobile web), offline sync integrity, and Radical Simplicity ("Least Code, Highest Craft").

---

## 1. Decision Framework

### 1.1 Mobile Stack Selection Matrix

Choose the simplest stack that meets hardware integration, team ownership, and distribution requirements:

| Stack Option | Best-Fit Scenario | Navigation Primitive | State Default ("Least Code") | Native Material / Glass Fallback |
|---|---|---|---|---|
| **SwiftUI (iOS Native)** | iOS-first app needing Liquid Glass, widgets, Live Activities, or Metal | `NavigationStack` + `TabView` + `.sheet(item:)` | MV-first (`@State`, `@Observable`, `@Environment`, `.task(id:)`) | `#available(iOS 26, *)` `GlassEffectContainer` -> `.ultraThinMaterial` |
| **Jetpack Compose (Android Native)** | Android-first app needing Material 3 adaptive rails, predictive back, WorkManager | Navigation Compose + Material 3 `NavigationBar` / `NavigationRail` | Hoisted `UiState` sealed interface + `collectAsStateWithLifecycle` + `Channel` events | Material 3 tonal surface elevation + system predictive back |
| **React Native + Expo Router** | Shared iOS/Android product team shipping fast with Expo Go / EAS | `<NativeTabs>` (`<= 5` tabs) + nested `<Stack>` + `formSheet` | URL route params + TanStack Query (`onlineManager`) + `expo-secure-store` | `GlassView` + `isLiquidGlassAvailable()` -> `expo-blur` `BlurView` |
| **Flutter** | Brand-uniform custom canvas UI across iOS, Android, and embedded screens | `go_router` + `PopScope` (Android 14+ predictive back) | `StatelessWidget` + `const` constructors + `ValueNotifier`/`Riverpod` | `BackdropFilter` only on bounded single overlays; avoid stacked blurs |
| **Responsive Mobile Web / PWA** | Broad reach without App Store gatekeeping | Semantic links + bottom thumb bar (`100dvh`) | URL `searchParams` + Service Worker outbox | `@media (hover: hover) and (pointer: fine)` guard; flat surfaces + `Phosphor`/`Solar`/`Iconamoon` |

### 1.2 iOS HIG vs. Android Material 3 Ergonomic & Navigation Matrix

| Dimension | iOS Human Interface Standard | Android Material 3 Standard | Shared Cross-Platform Invariant |
|---|---|---|---|
| **Minimum Touch Target** | `>= 44 x 44 pt` with `>= 8 pt` gap | `>= 48 x 48 dp` with `>= 8 dp` gap | Use `hitSlop` / padding expansion when visual icon is `20-24px` |
| **Primary Navigation Bar** | Bottom `TabView` / `NativeTabs` (`<= 5` tabs; search tab last) | `NavigationBar` (`<= 5` items); switch to `NavigationRail` at `>= 600dp` width | Never hide top-level destinations inside hamburger-only menus on mobile |
| **Modal Presentation** | `formSheet` detents `[0.25, 0.5, 1.0]`, `sheetGrabberVisible`, `sheetLargestUndimmedDetentIndex` | `ModalBottomSheet` with drag handle + predictive back dismissal | Pair drag gestures with explicit close/cancel control for VoiceOver/TalkBack |
| **Back Navigation** | Interactive edge-swipe pop via native stack | Android 14+ predictive back gesture (`PopScope` / Compose `BackHandler`) | Never hijack system back swipe with conflicting horizontal carousels at screen edge |
| **Platform Iconography** | Platform-native **SF Symbols** (`sf:` in Expo `expo-image`, `Image(systemName:)` in SwiftUI) | Platform-native Android **Vector Drawables** / M3 system symbols | On mobile-web surfaces, strictly use `Phosphor`, `Solar`, or `Iconamoon` (`Inter`/`Roboto`/`Lucide`/`Feather`/`Heroicons` banned on web) |
| **Typography & Dynamic Scaling** | SF Pro / system Dynamic Type (`fontWeight`, `@ScaledMetric`) | System Roboto/variable sans + `sp` font scaling | Support `allowFontScaling` up to `200%` without clipping buttons or labels |

### 1.3 Simplest High-Craft Option

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Reject reflexive MVVM `ViewModel` boilerplate per screen in SwiftUI, custom JS tab bars/bottom sheets in Expo, and user-agent sniffing on mobile web. Default to:
- **SwiftUI**: Direct MV architecture (`@State`, `@Observable`, `@Environment`, `.task(id:)`) plus pure domain services; introduce a dedicated `ViewModel` only when complex multi-stream debouncing or an existing MVVM codebase mandates it.
- **Expo / RN**: Native `<NativeTabs>`, `<Stack>`, and `presentation: 'formSheet'` with `process.env.EXPO_OS` branching and `expo-image`.
- **Jetpack Compose & Flutter**: Direct `StateFlow` + `collectAsStateWithLifecycle` or `StatelessWidget` + `const` builders over extra state-wrapper layers.
- **Mobile Web**: CSS `@media (hover: hover) and (pointer: fine)`, `min-height: 100dvh`, `env(safe-area-inset-*)`, and `overscroll-behavior-y: contain`.

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Read only the active platform stack guide (`SwiftUI` vs `Compose` vs `Expo` vs `Flutter` vs `Mobile Web`) and screen contract.
- Run deterministic platform analyzers (`expo-doctor`, `flutter analyze`, `xcodebuild`, Playwright `390x844`) instead of manual layout guesswork.

1. **Lock Thumb-Zone, Touch Target & Safe-Area Architecture (`Owner: Mobile UX / Engineer`)**
   - **Inputs**: Screen wireframes, `tokens.json`, target OS minimums (iOS / Android / mobile web).
   - **Action**:
     - Place primary conversion, submit, and navigation actions inside the **lower-third thumb arc**; keep destructive actions separated or guarded by confirmation.
     - Enforce `>= 44x44pt` (iOS), `>= 48x48dp` (Android), and `>= 44px` target (`>= 24x24px` hard floor) on mobile web with `>= 8px` clear separation between adjacent hit targets.
     - Respect hardware notches, Dynamic Island, and home indicator bars using `contentInsetAdjustmentBehavior="automatic"`, `SafeAreaProvider` / `useSafeAreaInsets()`, SwiftUI `.safeAreaInset`, or CSS `padding-bottom: max(16px, env(safe-area-inset-bottom))` paired with `min-height: 100dvh` (never `100vh`).
   - **Outputs**: Verified screen geometry and safe-area layout wrapper.

2. **Configure Platform-Idiomatic Navigation, Sheets & Foldables (`Owner: Mobile Engineer`)**
   - **Inputs**: Navigation map (`<= 5` root tabs), adaptive tablet/foldable breakpoints (`>= 600dp` / `768px`).
   - **Action**:
     - *Expo Router*: Configure `_layout.tsx` with `<NativeTabs minimizeBehavior="onScrollDown">` (keep static triggers; put search tab last; add `BottomAccessory` where needed), nested `<Stack>` headers, and `formSheet` detents `[0.25, 0.5, 1.0]` with `sheetGrabberVisible: true`.
     - *SwiftUI*: Configure `TabView` + `NavigationStack` + `.sheet(item:)` bound to a single optional `Identifiable` enum/model (eliminating competing `@State var showA / showB` boolean flag conflicts).
     - *Jetpack Compose & Flutter*: Wire M3 `NavigationBar` collapsing into `NavigationRail` / two-pane `ListDetailPaneScaffold` on `>= 600dp` window classes; enable Android 14+ predictive back via `PopScope` / Compose navigation.
   - **Outputs**: Platform-native navigation graph and tablet adaptive layout.

3. **Implement Framework-Specific Performance & Craft Rules (`Owner: Mobile Engineer`)**
   - **Inputs**: Screen specs, media/list payloads, auth/storage contracts.
   - **Action**:
     - *Expo / React Native*: Branch platform behavior with `process.env.EXPO_OS`, render icons/images via `expo-image` (`sf:` on iOS), measure dynamic viewports with `useWindowDimensions()`, style rounded cards with `{ borderCurve: 'continuous' }` and CSS `boxShadow` prop, trigger subtle `expo-haptics` on iOS key completions, virtualize lists with `FlatList` (`keyExtractor`, `getItemLayout`) or `FlashList`, and store auth tokens exclusively in `expo-secure-store` (never `AsyncStorage`).
     - *SwiftUI*: Order properties top-to-bottom (`@Environment` -> `@State` -> `let` -> `var` -> `body` -> helpers), split large screens into dedicated `struct SubView: View` components (`< 300` lines/file) rather than computed `some View` builders, keep root view trees structurally stable (never swap root views with top-level `if/else` when `.opacity`/modifier state suffices), and audit scroll smoothness with Instruments for unstable `ForEach` IDs or `GeometryReader` thrash.
     - *Jetpack Compose*: Mark data classes `@Immutable`, hoist state cleanly, consume flows with `collectAsStateWithLifecycle()`, pass `key` in `LazyColumn`, and apply `Modifier` chains directly rather than wrapping single children in redundant `Box`.
     - *Flutter*: Prefer `StatelessWidget` with `const` constructors, use `ListView.builder` with `itemExtent` and `ValueKey`, wrap heavy animated subtrees in `RepaintBoundary`, and `dispose()` every `AnimationController`/`TextEditingController`.
     - *Mobile Web*: Wrap `:hover` styles inside `@media (hover: hover) and (pointer: fine)` to eliminate sticky hover after taps, set `touch-action: pan-y` or `none` explicitly on custom swipe/canvas zones, use `window.visualViewport` to anchor sticky toolbars cleanly above virtual keyboards, and add `overscroll-behavior-y: contain` inside drawers/sheets.
   - **Outputs**: Smooth `60/120 fps` platform components with clean memory and storage hygiene.

4. **Wire Gesture Accessibility, Offline Outbox & Permission Priming (`Owner: Mobile / Full-Stack Engineer`)**
   - **Inputs**: Mutation endpoints, hardware permission requirements (Camera, Location, Push).
   - **Action**:
     - Pair every hidden gesture (swipe-to-archive, long-press menu, shake-to-undo) with a visible accessible button or context trigger (`accessibilityActions` / `onLongPress` + visible overflow button).
     - Wire connectivity awareness (`NetInfo` + TanStack `onlineManager` or platform reachability): display an unobtrusive `Offline — showing cached data` banner, queue safe offline writes in an outbox stamped with a client UUID `idempotency_key`, and reconcile cleanly on reconnect.
     - **Just-In-Time Permission Priming**: NEVER fire OS permission dialogs on first app launch. Wait until user intent triggers the capability, render a lightweight value-explaining pre-prompt card, fire the OS prompt only on confirmation, and provide a direct `"Open Settings"` recovery path if denied.
   - **Outputs**: Resilient offline-aware flows and ethical permission gates.

5. **Deletion Pass, Accessibility Scaling & Simulator Check (`Owner: Mobile QA`)**
   - **Inputs**: Built mobile app or responsive mobile-web build.
   - **Action**:
     - **Deletion Pass**: Remove redundant wrapper `Box`/`View`/`<div>` layers, replace custom JS modal overlays with native `formSheet`/`.sheet(item:)`, and strip unused animation packages.
     - Verify across `390x844` (phone) and `768x1024` (tablet) with `200%` Dynamic Type / `allowFontScaling`, VoiceOver/TalkBack focus order, `prefers-reduced-motion`, and offline airplane-mode toggle.
   - **Outputs**: Verified simulator screenshots and audit log.

### 2.6 Minimal Platform-Idiomatic Snippets (Mobile Web & Native Glass Fallback)

```css
/* Mobile web: 100dvh, safe-area inset, and zero sticky-hover on touch */
.mobile-shell {
  min-height: 100dvh;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
}
.mobile-drawer {
  overscroll-behavior-y: contain;
}
@media (hover: hover) and (pointer: fine) {
  .action-btn:hover { background-color: var(--color-bg-hover); }
}
```

```swift
// SwiftUI iOS 26+ Liquid Glass with ultraThinMaterial fallback
if #available(iOS 26, *) {
  GlassEffectContainer { ToolbarControls().glassEffect() }
} else {
  ToolbarControls().background(.ultraThinMaterial)
}
```

```kotlin
// Jetpack Compose: lifecycle-aware state collection + one-shot Channel navigation
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
LaunchedEffect(Unit) {
  viewModel.navEvents.collect { dest -> navController.navigate(dest) }
}
```

```dart
// Flutter: Android 14+ predictive back handling with PopScope
PopScope(
  canPop: !hasUnsavedChanges,
  onPopInvokedWithResult: (didPop, _) {
    if (!didPop) showDiscardConfirmation(context);
  },
  child: screenContent,
)
```

---

## 3. Reusable Artifact & Template

Mobile projects reuse [UI Redesign Audit & Preservation Template](../templates/ui-redesign-audit.md) for mobile UX/a11y audits and complete the **Cross-Platform Surface Parity Matrix**:

| Schema Column | Purpose | Required Concrete Values |
|---|---|---|
| `screen_or_flow` | Screen ID and route path | e.g., `SCR-04 /invoices/[id]` |
| `ios_pattern` | Native iOS presentation, icon, and material | e.g., `Stack push + formSheet [0.5, 1.0] + SF Symbol doc.text` |
| `android_pattern` | Native Android M3 navigation, icon, and back behavior | e.g., `M3 ModalBottomSheet + Vector Drawable + Predictive Back` |
| `thumb_and_safe_area` | Touch dimensions, lower-third triggers, inset rules | e.g., `48px primary CTA bottom-pinned + env(safe-area-inset-bottom)` |
| `offline_and_permission` | Reachability state, outbox key, permission pre-prompt | e.g., `Stale banner + UUID idempotency_key; Camera pre-prompt on Scan tap` |
| `a11y_and_scaling` | Screen-reader labels, action parity, `200%` text scaling | e.g., `Visible overflow alternative to swipe; allowFontScaling verified` |

---

## 4. Verification Checklist

- [ ] Interactive controls satisfy `>= 44x44pt` (iOS) / `>= 48x48dp` (Android) / `>= 44px` mobile-web touch targets with `>= 8px` gap.
- [ ] Notches, Dynamic Island, home indicator, and keyboard bars use native safe-area insets and `100dvh` (`0` usage of `100vh` on mobile web).
- [ ] Mobile-web hover rules are wrapped in `@media (hover: hover) and (pointer: fine)` with zero sticky hover states after tap.
- [ ] Auth tokens and sensitive credentials use `expo-secure-store`, iOS Keychain, or Android Keystore (`0` secrets in `AsyncStorage` or `localStorage`).
- [ ] Native platforms use idiomatic navigation (`NativeTabs`/`TabView`/M3 `NavigationBar`, `formSheet`/`.sheet(item:)`/`ModalBottomSheet`, Android predictive back `PopScope`).
- [ ] Every swipe/long-press/shake gesture has a visible, accessible button or menu fallback for assistive technology users.
- [ ] Permissions (Camera, Location, Notifications) prompt only after explicit user intent with a clear pre-prompt and Settings fallback on denial.
- [ ] Dynamic Type / `allowFontScaling` at `200%`, `prefers-reduced-motion`, and offline reachability transitions render without clipping or data loss.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - Zero clipped controls at `390x844` and `200%` font scaling; zero sticky hover or `100vh` viewport jumps; zero gesture-only dead ends.
  - Platform linters/diagnostics (`expo-doctor`, `flutter analyze`, SwiftUI/Xcode build, or Playwright `390x844` mobile-web check) exit `0` after the deletion pass.
  - Auth credentials stored strictly in Keychain/Keystore/`SecureStore`; offline reconnect preserves last-known-good state without duplicate writes.
- **`FAIL`**:
  - Any `AsyncStorage` token storage, startup permission ambush, `< 44px` cramped primary touch targets, top-level SwiftUI root `if/else` view swapping, or unvirtualized large scroll lists.
  - Any mobile-web surface importing banned fonts (`Inter`/`Roboto`/`Arial`/`Open Sans`/`Helvetica`) or banned icon sets (`Lucide`/`Feather`/`Heroicons`/`Material Icons`/`Material Symbols`).

```bash
# Platform diagnostics & mobile-viewport verification commands
npx expo-doctor && npx tsc --noEmit
flutter analyze
npx playwright test --project=mobile-safari-390x844
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Sticky Hover & `100vh` Mobile-Web Jump** | `:hover` stays stuck after tapping buttons; `100vh` hides bottom CTAs behind mobile browser chrome | Unscoped `:hover:` selectors or `h-screen` / `height: 100vh` in mobile CSS | Guard hover with `@media (hover: hover) and (pointer: fine)`; use `min-height: 100dvh` |
| **`AsyncStorage` Auth Tokens & Deprecated RN APIs** | Unencrypted local storage leaks session tokens; legacy RN modules break New Architecture builds | `AsyncStorage.setItem('token', ...)` or `Platform.OS` / legacy `Image` icon hacks | Store tokens in `expo-secure-store`; use `process.env.EXPO_OS` and `expo-image` |
| **Top-Level SwiftUI View Swapping & MVVM Bloat** | Destroys view identity, breaks transition state, and adds 3x boilerplate per simple screen | `if isReady { ViewA() } else { ViewB() }` at root or empty passthrough `ViewModel`s | Use MV (`@State`, `@Observable`, `.task`) and stable view trees with modifier state |
| **Gesture-Only Actions & Back-Gesture Hijack** | Screen-reader and motor-impaired users cannot discover or trigger hidden swipes; edge carousels trap back navigation | Swipe-to-delete without overflow button, or horizontal pager touching left screen edge | Pair every gesture with visible accessible controls; respect OS edge-back margins |
| **Page-Load OS Permission Ambush** | Asking for Camera/Location/Push on cold launch causes permanent OS denial rates above `60%` | `requestPermissionsAsync()` inside root `useEffect` or `App.init` | Trigger pre-prompt explanation card only when user taps the feature requiring hardware |
| **Stacked Blur Views & Unvirtualized Lists** | Nested `BlurView`/`.glassEffect` tanks GPU frame times; `.map()` over `500+` rows stalls scroll | Multiple nested blurs or `ScrollView` wrapping `.map()` instead of `FlatList`/`LazyColumn` | Apply glass strictly to 1 bounded nav/header surface; virtualize with keyed recyclers |
