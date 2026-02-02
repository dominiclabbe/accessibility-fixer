# Android TV Accessibility Audit Guide
## 10-Foot UI and D-pad Navigation

---

## Overview

Android TV has specific accessibility requirements for living room interfaces.

**Key Focus:**
- D-pad navigation
- Focus management
- TalkBack for TV
- Larger touch targets (for remote pointer)

---

## Android TV Specific Patterns

### 1. D-pad Navigation

```kotlin
// ❌ ISSUE: D-pad navigation not configured
RecyclerView(...)

// ✅ CORRECT: Enable D-pad focus
recyclerView.apply {
    isFocusable = true
    descendantFocusability = ViewGroup.FOCUS_AFTER_DESCENDANTS
}

// Compose (Leanback library)
TvLazyColumn(
    modifier = Modifier.focusable()
) {
    items(items) { item ->
        TvCard(
            onClick = { /*...*/ },
            modifier = Modifier.focusable()
        ) {
            // Card content
        }
    }
}
```

---

### 2. Focus Indicators

```xml
<!-- ✅ CORRECT: Clear focus drawable -->
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape>
            <stroke android:width="4dp" android:color="#FFFFFF" />
            <corners android:radius="8dp" />
        </shape>
    </item>
</selector>
```

---

### 3. Content Descriptions

All guidance from GUIDE_ANDROID.md applies, plus:
- Even more critical for TV as touch feedback is absent
- TalkBack on TV works similarly to mobile

---

## Testing

- Test with D-pad remote
- Enable TalkBack on Android TV
- Verify focus order is logical
- Ensure all interactive elements are focusable

---

**Related Guides:**
- GUIDE_ANDROID.md - Core Android patterns
- GUIDE_WCAG_REFERENCE.md
