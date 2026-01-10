# Implementation Plan: UI Flow Update with CSS Animations

**Date**: 2026-01-10
**Task**: Update Telegram File Manager UI flow with GramJS authentication and CSS animations
**Estimated Effort**: 4-6 hours

---

## 🎯 Objectives

1. Implement new onboarding flow with GramJS authentication
2. Replace all Framer Motion animations with CSS for better performance
3. Add comprehensive file type preview support
4. Fix UI display issues (especially input fields)
5. Remove demo mode and unnecessary UI elements
6. Persist session in local storage

---

## 📐 Architecture Changes

### Current Flow
```
App.tsx (shows main view with "Demo Mode" banner)
├── Settings Dialog (manual connection)
└── TelegramLoginDialog (complex multi-step)
```

### New Flow
```
App.tsx (router logic)
├── OnboardingPage (first-time setup)
│   ├── Step 1: API Credentials (with help link)
│   ├── Step 2: Phone Number
│   ├── Step 3: OTP Verification
│   ├── Step 4: 2FA Password (if enabled)
│   └── Step 5: Chat Selection
└── MainView (authenticated only)
    ├── Header
    ├── Sidebar
    ├── FileGrid
    └── Modals (with CSS animations)
```

---

## 🔨 Implementation Steps

### Phase 1: CSS Animation System (1 hour)

**Files to modify:**
- `src/index.css` - Add CSS animation classes

**Tasks:**
1. Create CSS animation keyframes for common transitions:
   - `@keyframes fadeIn`
   - `@keyframes fadeOut`
   - `@keyframes slideUp`
   - `@keyframes slideDown`
   - `@keyframes slideInFromRight`
   - `@keyframes slideOutToLeft`
   - `@keyframes scaleIn`
   - `@keyframes scaleOut`

2. Create utility classes:
   - `.animate-fade-in`
   - `.animate-slide-up`
   - `.animate-slide-in`
   - `.animate-scale-in`
   - `.modal-overlay-enter/exit`
   - `.modal-content-enter/exit`

3. Add performance optimizations:
   - `will-change` property
   - Hardware acceleration with `transform: translateZ(0)`
   - Reduce motion media query support

---

### Phase 2: Onboarding Page Component (2 hours)

**New file:**
- `src/pages/Onboarding.tsx`

**Features:**
1. **Step 1: API Credentials**
   - Input for API ID (number only)
   - Input for API Hash
   - Help link to `https://my.telegram.org/apps`
   - Form validation
   - Save to localStorage

2. **Step 2: Phone Number**
   - Phone input with country code
   - Format validation
   - Send code button

3. **Step 3: OTP Verification**
   - 5-digit code input
   - Auto-submit when complete
   - Resend code option (future)

4. **Step 4: 2FA Password** (conditional)
   - Password input
   - Only shown if account has 2FA enabled

5. **Step 5: Chat Selection**
   - Grid/list of available chats
   - Show chat type icons (Saved, Channel, Group, User)
   - Recommended: "Saved Messages"
   - Save selection to localStorage

**Design:**
- Use CSS animations for step transitions
- Mobile-responsive (bottom sheet on mobile)
- Progress indicator
- Back button (except on first step)
- Error handling with toast notifications

---

### Phase 3: Update App.tsx Router Logic (1 hour)

**File to modify:**
- `src/App.tsx`

**Changes:**
1. Add authentication check at the top level
2. Route logic:
   ```tsx
   const isAuthenticated = useSettingsStore(state => state.isConnected());
   
   if (!isAuthenticated) {
     return <OnboardingPage />;
   }
   
   return <MainView />;
   ```

3. Remove "Demo Mode" banner completely
4. Remove unnecessary connection prompts

---

### Phase 4: Replace Framer Motion with CSS (1.5 hours)

**Files to modify:**
- `src/components/dialogs/PreviewModal.tsx`
- `src/components/dialogs/SettingsDialog.tsx`
- `src/components/dialogs/TelegramLoginDialog.tsx`
- `src/components/mobile/MobileActionSheet.tsx`
- `src/components/mobile/SwipeableDrawer.tsx`
- `src/App.tsx`

**Strategy:**
1. Remove `framer-motion` imports
2. Replace `<motion.div>` with `<div>`
3. Add CSS classes for animations:
   - Dialog enter/exit: `className="modal-overlay animate-fade-in"`
   - Content slide: `className="modal-content animate-slide-up"`
   - Mobile bottom sheet: `className="bottom-sheet animate-slide-up"`

4. Use CSS transitions for interactive states:
   ```css
   .btn-gradient {
     transition: transform 0.2s ease, opacity 0.2s ease;
   }
   .btn-gradient:hover {
     transform: scale(1.05);
   }
   ```

5. Handle exit animations with state + setTimeout:
   ```tsx
   const [isExiting, setIsExiting] = useState(false);
   
   const handleClose = () => {
     setIsExiting(true);
     setTimeout(() => {
       onClose();
       setIsExiting(false);
     }, 300); // Animation duration
   };
   ```

---

### Phase 5: Enhanced File Preview (1 hour)

**File to modify:**
- `src/components/dialogs/PreviewModal.tsx`

**File type support:**
1. **Images**: jpg, png, gif, webp, svg
   - Full-size display
   - Zoom controls

2. **Videos**: mp4, webm, mov, avi
   - Native video player
   - Controls overlay

3. **Audio**: mp3, wav, ogg, m4a
   - Waveform visualization (optional)
   - Playback controls

4. **Documents**: pdf, txt, md
   - PDF viewer (embedded iframe or custom)
   - Text renderer with syntax highlighting

5. **Archives**: zip, rar, 7z
   - File list preview
   - Download prompt

6. **Fallback**: Unknown types
   - File icon
   - Download button
   - File info (size, type)

**UI Improvements:**
- Proper loading states
- Error handling for corrupt files
- Navigation arrows (prev/next)
- Close button always visible
- File info overlay

---

### Phase 6: Fix Input UI Issues (0.5 hours)

**Files to check:**
- `src/components/upload/DropZone.tsx`
- `src/components/dialogs/SettingsDialog.tsx`
- `src/pages/Onboarding.tsx`

**Issues to fix:**
1. Input field padding/alignment
2. Icon positioning in inputs
3. Focus states
4. Placeholder text contrast
5. Mobile keyboard handling
6. Auto-complete attributes

**CSS updates:**
```css
.input-glass {
  padding: 0.75rem 1rem;
  padding-left: 2.5rem; /* When icon present */
}

.input-glass:focus {
  outline: 2px solid rgba(124, 58, 237, 0.5);
  outline-offset: 2px;
}
```

---

### Phase 7: Remove Demo UI (0.5 hours)

**Files to modify:**
- `src/App.tsx` - Remove demo banner
- `src/components/layout/Header.tsx` - Remove demo indicators
- `src/pages/Setup.tsx` - Can be deleted (replaced by Onboarding)

---

## 🧪 Testing Checklist

### Functional Tests
- [ ] API credentials validation works
- [ ] Phone number sends OTP correctly
- [ ] OTP verification succeeds
- [ ] 2FA password flow works (if enabled)
- [ ] Chat selection displays all chats
- [ ] Session persists after page reload
- [ ] Logout clears session
- [ ] All animations are smooth (60fps)

### UI/UX Tests
- [ ] All modals animate with CSS
- [ ] Mobile bottom sheets work correctly
- [ ] Input fields display properly on all screen sizes
- [ ] Preview modal supports all file types
- [ ] Navigation between files works
- [ ] Error messages display correctly
- [ ] Loading states are visible
- [ ] No demo mode visible

### Performance Tests
- [ ] Page load time < 2s
- [ ] Animation FPS >= 60
- [ ] No jank during scrolling
- [ ] Bundle size reduction (after removing Framer Motion)

---

## 📦 Dependencies

### To Remove
- `framer-motion` (if not used elsewhere)

### To Keep
- `gramjs` - Telegram MTProto client
- `zustand` - State management
- `lucide-react` - Icons

---

## 🚀 Deployment Notes

1. Clear localStorage key `file-manager-settings` for testing
2. Test with both new users and returning users
3. Verify session persistence across tabs
4. Test on mobile devices (iOS Safari, Chrome)

---

## 📝 Future Enhancements

- [ ] Biometric authentication (Face ID, Touch ID)
- [ ] Multiple account support
- [ ] Session expiry warnings
- [ ] Advanced file preview (Office docs, code)
- [ ] Lazy loading for chat list
- [ ] Search/filter chats during selection

---

## ✅ Success Metrics

- User completes onboarding in < 2 minutes
- 0 JavaScript animation libraries in production bundle
- Animation performance: 60fps on mid-range devices
- Session persistence: 100% success rate
- All file types have preview support
