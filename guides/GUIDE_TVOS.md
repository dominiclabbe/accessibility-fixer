# tvOS Accessibility Audit Guide
## Apple TV and Focus Engine

---

## Overview

tvOS has unique accessibility requirements for living room interfaces.

**Key Focus:**
- Focus engine
- Siri Remote navigation
- VoiceOver for TV

---

## tvOS Specific Patterns

### 1. Focus Engine Configuration

```swift
// ✅ CORRECT: Focus engine configuration
override var canBecomeFocused: Bool {
    return true
}

override func didUpdateFocus(
    in context: UIFocusUpdateContext,
    with coordinator: UIFocusAnimationCoordinator
) {
    super.didUpdateFocus(in: context, with: coordinator)
    
    if context.nextFocusedView == self {
        // Handle focus gained - scale up
        coordinator.addCoordinatedAnimations({
            self.transform = CGAffineTransform(scaleX: 1.1, y: 1.1)
        }, completion: nil)
    } else {
        // Handle focus lost - scale down
        coordinator.addCoordinatedAnimations({
            self.transform = .identity
        }, completion: nil)
    }
}
```

### 2. SwiftUI Focus

```swift
// ✅ CORRECT: SwiftUI tvOS button
Button("Watch Now") {
    playVideo()
}
.buttonStyle(.card)
.focusable()
```

---

### 3. Accessibility Labels

All guidance from GUIDE_IOS.md applies - labels, traits, etc. are the same.

---

## Testing

- Test with Siri Remote
- Enable VoiceOver on Apple TV
- Verify focus animations are clear
- Ensure focus order is logical

---

**Related Guides:**
- GUIDE_IOS.md - Core iOS patterns apply to tvOS
- GUIDE_WCAG_REFERENCE.md
