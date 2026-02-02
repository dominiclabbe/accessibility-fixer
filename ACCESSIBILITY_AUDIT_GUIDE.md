# Accessibility Audit Guide
## Comprehensive Source Code Analysis Framework

---

## Table of Contents
1. [Introduction](#introduction)
2. [WCAG 2.2 Overview](#wcag-22-overview)
3. [Audit Methodology](#audit-methodology)
4. [Platform-Specific Analysis](#platform-specific-analysis)
5. [Audit Report Structure](#audit-report-structure)
6. [Common Issues Reference](#common-issues-reference)
7. [Resources](#resources)

---

## Introduction

### Purpose
This guide provides a systematic framework for analyzing source code to identify accessibility issues across multiple platforms (Android mobile, Android TV, iOS, tvOS, Web, etc.). Each audit produces a platform-specific report documenting issues according to WCAG 2.2 guidelines.

### Scope
- Source code analysis (not limited to UI testing)
- Multi-platform coverage with platform-specific reports
- WCAG 2.2 Level A and AA compliance focus
- Documentation with visual evidence (screenshots)

---

## WCAG 2.2 Overview

### The POUR Principles

All WCAG success criteria are organized under four core principles:

1. **Perceivable** - Information and UI components must be presentable to users in ways they can perceive
2. **Operable** - UI components and navigation must be operable
3. **Understandable** - Information and operation of UI must be understandable
4. **Robust** - Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies

### Conformance Levels

- **Level A**: Basic accessibility features (minimum requirement)
- **Level AA**: Most common compliance target, addresses major barriers
- **Level AAA**: Enhanced accessibility (not required for full sites)

**Target for most audits: Level AA compliance**

### Mobile Considerations

When applying WCAG to mobile:
- "Web pages" = "screens" or "views"
- Focus on platform accessibility services (TalkBack, VoiceOver)
- Consider touch interfaces and gesture controls
- Account for device capabilities (orientation, sensors)

---

## Audit Methodology

### Phase 1: Project Setup

1. **Platform Identification**
   - Identify all platforms in the codebase
   - Determine technology stack for each platform
   - Set up development environment for testing

2. **Documentation Review**
   - Review existing accessibility documentation
   - Check for accessibility guidelines or standards already in use
   - Identify accessibility test coverage

### Phase 2: Code Analysis

#### General Analysis Approach

For each platform, systematically analyze:

1. **UI Component Inventory**
   - List all interactive elements (buttons, inputs, links, etc.)
   - Document custom components
   - Identify complex UI patterns (modals, carousels, tabs, etc.)

2. **Accessibility Implementation Review**
   - Check for accessibility labels/descriptions
   - Verify semantic structure
   - Analyze keyboard/focus management
   - Review color contrast implementation
   - Examine error handling and validation

3. **Automated Scanning**
   - Use platform-specific accessibility scanners
   - Document automated findings for manual verification

4. **Manual Code Review**
   - Search for accessibility anti-patterns
   - Verify assistive technology compatibility
   - Check dynamic content handling

### Phase 3: Testing

1. **Assistive Technology Testing**
   - Screen readers (TalkBack, VoiceOver, NVDA, JAWS)
   - Switch Control / Switch Access
   - Voice Control
   - Keyboard navigation

2. **Visual Testing**
   - Color contrast verification
   - Text scaling (up to 200%)
   - Screen orientation
   - Dark mode / High contrast modes

3. **Documentation**
   - Capture screenshots for each issue
   - Record screen reader behavior
   - Document steps to reproduce

---

## Platform-Specific Analysis

### Web Platform

#### Technology Focus
- HTML semantic markup
- ARIA attributes and roles
- CSS (color, focus states, responsive design)
- JavaScript (dynamic updates, keyboard handling)

#### Key Code Patterns to Check

**1. Semantic HTML**
```javascript
// ISSUE: Non-semantic markup
<div onclick="handleClick()">Click me</div>

// CORRECT: Semantic button
<button onClick={handleClick}>Click me</button>
```

**2. Alternative Text**
```javascript
// ISSUE: Missing alt text
<img src="logo.png" />

// CORRECT: Descriptive alt text
<img src="logo.png" alt="Company name logo" />

// CORRECT: Decorative image
<img src="decorative.png" alt="" role="presentation" />
```

**3. Form Labels**
```javascript
// ISSUE: Unlabeled input
<input type="text" placeholder="Enter name" />

// CORRECT: Properly labeled
<label htmlFor="name">Name</label>
<input type="text" id="name" />
```

**4. Keyboard Navigation**
```javascript
// ISSUE: Keyboard trap or missing focus management
<div onClick={handleClick}>Custom button</div>

// CORRECT: Keyboard accessible
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Custom button
</div>
```

**5. Color Contrast**
```css
/* ISSUE: Insufficient contrast (2.5:1) */
.text {
  color: #999;
  background: #fff;
}

/* CORRECT: Minimum 4.5:1 for normal text */
.text {
  color: #767676;
  background: #fff;
}
```

**6. Dynamic Content**
```javascript
// ISSUE: Screen reader not notified of updates
setContent(newContent);

// CORRECT: ARIA live region
<div aria-live="polite" aria-atomic="true">
  {content}
</div>
```

#### Files to Analyze
- Component files (`.jsx`, `.tsx`, `.vue`, `.svelte`)
- Style files (`.css`, `.scss`, `.styled.js`)
- Routing configuration
- Form validation logic
- Modal/Dialog implementations

#### Testing Tools
- axe DevTools browser extension
- WAVE browser extension
- Lighthouse accessibility audit
- NVDA / JAWS (screen readers)
- Keyboard-only navigation

---

### Android (Mobile & TV)

#### Technology Focus
- XML layouts and Compose UI
- ContentDescription attributes
- Accessibility events
- Touch target sizes
- TalkBack compatibility

#### Key Code Patterns to Check

**1. Content Descriptions (XML)**
```xml
<!-- ISSUE: Missing contentDescription on ImageButton -->
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!-- CORRECT: Descriptive contentDescription -->
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:contentDescription="@string/play_button"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!-- CORRECT: Decorative image -->
<ImageView
    android:src="@drawable/decorative_border"
    android:importantForAccessibility="no"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**2. Content Descriptions (Compose)**
```kotlin
// ISSUE: Missing semantics
Icon(
    painter = painterResource(R.drawable.ic_play),
    contentDescription = null
)

// CORRECT: Descriptive content description
Icon(
    painter = painterResource(R.drawable.ic_play),
    contentDescription = stringResource(R.string.play_button)
)

// CORRECT: Decorative icon
Icon(
    painter = painterResource(R.drawable.decorative),
    contentDescription = null,
    modifier = Modifier.semantics {
        invisibleToUser()
    }
)
```

**3. Touch Target Size**
```xml
<!-- ISSUE: Touch target too small (32dp) -->
<Button
    android:layout_width="32dp"
    android:layout_height="32dp"
    android:text="X" />

<!-- CORRECT: Minimum 48dp touch target -->
<Button
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:text="X" />
```

**4. Clickable Items with Custom Views**
```kotlin
// ISSUE: Custom view not marked as clickable/focusable
customView.setOnClickListener { handleClick() }

// CORRECT: Proper accessibility setup
customView.apply {
    isClickable = true
    isFocusable = true
    contentDescription = "Custom action button"
    setOnClickListener { handleClick() }
}
```

**5. Headings and Structure**
```kotlin
// ISSUE: No heading structure
Text("Section Title")

// CORRECT: Marked as heading
Text(
    "Section Title",
    modifier = Modifier.semantics {
        heading()
    }
)
```

**6. Live Regions**
```kotlin
// ISSUE: Dynamic content without announcement
Text(text = statusMessage)

// CORRECT: Announces changes
Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite
    }
)
```

**7. EditText Labels**
```xml
<!-- ISSUE: Placeholder used as label -->
<EditText
    android:id="@+id/emailInput"
    android:hint="Email address"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- CORRECT: TextInputLayout provides persistent label -->
<com.google.android.material.textfield.TextInputLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:hint="Email address">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/emailInput"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

</com.google.android.material.textfield.TextInputLayout>
```

#### Android TV Specific

```kotlin
// ISSUE: D-pad navigation not configured
RecyclerView(...)

// CORRECT: Enable D-pad focus
RecyclerView(...).apply {
    isFocusable = true
    descendantFocusability = ViewGroup.FOCUS_AFTER_DESCENDANTS
}
```

#### Files to Analyze
- Layout XML files (`res/layout/*.xml`)
- Compose files (`*Screen.kt`, `*Composable.kt`)
- Custom view implementations
- Adapters (RecyclerView, ViewPager)
- Fragment and Activity classes
- Navigation graphs

#### Testing Tools
- Android Accessibility Scanner app
- TalkBack screen reader
- Switch Access
- Espresso with accessibility checks
- Layout Inspector

---

### iOS & tvOS

#### Technology Focus
- UIKit and SwiftUI accessibility properties
- VoiceOver compatibility
- Accessibility labels, hints, and traits
- Dynamic Type support
- Switch Control

#### Key Code Patterns to Check

**1. Accessibility Labels (UIKit)**
```swift
// ISSUE: Button with icon but no label
let playButton = UIButton()
playButton.setImage(UIImage(named: "play"), for: .normal)

// CORRECT: Descriptive label
let playButton = UIButton()
playButton.setImage(UIImage(named: "play"), for: .normal)
playButton.accessibilityLabel = "Play"

// CORRECT: Decorative image
decorativeImageView.isAccessibilityElement = false
```

**2. Accessibility Labels (SwiftUI)**
```swift
// ISSUE: Image without label
Image("play")
    .onTapGesture { play() }

// CORRECT: Descriptive label
Image("play")
    .accessibilityLabel("Play")
    .onTapGesture { play() }

// CORRECT: Button with automatic label
Button("Play") {
    play()
}
```

**3. Accessibility Traits**
```swift
// ISSUE: Custom interactive view without proper trait
let customButton = UIView()
customButton.isAccessibilityElement = true
customButton.accessibilityLabel = "Submit"
// Missing: button trait

// CORRECT: Proper trait for interactive element
let customButton = UIView()
customButton.isAccessibilityElement = true
customButton.accessibilityLabel = "Submit"
customButton.accessibilityTraits = .button

// SwiftUI
Text("Submit")
    .accessibilityAddTraits(.isButton)
    .onTapGesture { submit() }
```

**4. Headings**
```swift
// ISSUE: Section title without heading trait
let titleLabel = UILabel()
titleLabel.text = "Settings"
titleLabel.font = .preferredFont(forTextStyle: .headline)

// CORRECT: Marked as heading
let titleLabel = UILabel()
titleLabel.text = "Settings"
titleLabel.font = .preferredFont(forTextStyle: .headline)
titleLabel.accessibilityTraits = .header

// SwiftUI
Text("Settings")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
```

**5. Grouping Elements**
```swift
// ISSUE: Multiple elements read separately
VStack {
    Image(systemName: "star.fill")
    Text("Rating: 4.5")
}

// CORRECT: Grouped for VoiceOver
VStack {
    Image(systemName: "star.fill")
    Text("Rating: 4.5")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Rating: 4.5 stars")
```

**6. Text Input Labels**
```swift
// ISSUE: Placeholder used as only label
let textField = UITextField()
textField.placeholder = "Email address"

// CORRECT: Accessibility label provided
let textField = UITextField()
textField.placeholder = "Email address"
textField.accessibilityLabel = "Email address"
// Even better: Use a visible UILabel

// SwiftUI
TextField("Email address", text: $email)
    .accessibilityLabel("Email address")
```

**7. Dynamic Content Announcements**
```swift
// ISSUE: Status change not announced
statusLabel.text = "Upload complete"

// CORRECT: Post announcement
statusLabel.text = "Upload complete"
UIAccessibility.post(
    notification: .announcement,
    argument: "Upload complete"
)

// SwiftUI
.accessibilityLiveRegion(.polite)
```

**8. Custom Actions**
```swift
// ISSUE: Swipe actions not accessible to VoiceOver users
// Requires physical swipe gesture

// CORRECT: Provide custom accessibility actions
cell.accessibilityCustomActions = [
    UIAccessibilityCustomAction(
        name: "Delete",
        target: self,
        selector: #selector(deleteItem)
    ),
    UIAccessibilityCustomAction(
        name: "Archive",
        target: self,
        selector: #selector(archiveItem)
    )
]
```

#### tvOS Specific

```swift
// ISSUE: Focus not properly configured for tvOS
UIButton()

// CORRECT: Focus engine configuration
override var canBecomeFocused: Bool {
    return true
}

override func didUpdateFocus(
    in context: UIFocusUpdateContext,
    with coordinator: UIFocusAnimationCoordinator
) {
    super.didUpdateFocus(in: context, with: coordinator)

    if context.nextFocusedView == self {
        // Handle focus gained
    }
}
```

#### Files to Analyze
- View Controllers (`.swift`)
- SwiftUI Views (`*View.swift`)
- Custom view classes
- Storyboards and XIBs
- Table/Collection view cells
- Navigation flow

#### Testing Tools
- Xcode Accessibility Inspector
- VoiceOver
- Switch Control
- Voice Control
- Accessibility Audits in Xcode

---

### React Native

#### Technology Focus
- Cross-platform accessibility props
- Platform-specific accessibility implementations
- Screen reader compatibility (TalkBack & VoiceOver)

#### Key Code Patterns to Check

**1. Accessibility Labels**
```javascript
// ISSUE: Image without label
<Image source={require('./play.png')} />

// CORRECT: Accessible image
<Image
  source={require('./play.png')}
  accessible={true}
  accessibilityLabel="Play"
/>

// CORRECT: Decorative image
<Image
  source={require('./decorative.png')}
  accessible={false}
/>
```

**2. Accessibility Roles**
```javascript
// ISSUE: Touchable without role
<TouchableOpacity onPress={handlePress}>
  <Text>Submit</Text>
</TouchableOpacity>

// CORRECT: Explicit button role
<TouchableOpacity
  onPress={handlePress}
  accessibilityRole="button"
  accessibilityLabel="Submit"
>
  <Text>Submit</Text>
</TouchableOpacity>
```

**3. Accessibility States**
```javascript
// ISSUE: Toggle button without state
<TouchableOpacity onPress={togglePlay}>
  <Icon name={isPlaying ? 'pause' : 'play'} />
</TouchableOpacity>

// CORRECT: State communicated to screen reader
<TouchableOpacity
  onPress={togglePlay}
  accessibilityRole="button"
  accessibilityLabel={isPlaying ? "Pause" : "Play"}
  accessibilityState={{ selected: isPlaying }}
>
  <Icon name={isPlaying ? 'pause' : 'play'} />
</TouchableOpacity>
```

**4. Form Inputs**
```javascript
// ISSUE: Input without label
<TextInput
  placeholder="Email"
  value={email}
  onChangeText={setEmail}
/>

// CORRECT: Properly labeled input
<View>
  <Text accessibilityRole="header">Email</Text>
  <TextInput
    accessibilityLabel="Email"
    accessibilityHint="Enter your email address"
    placeholder="Email"
    value={email}
    onChangeText={setEmail}
  />
</View>
```

---

### Flutter

#### Technology Focus
- Semantics widget
- MergeSemantics and ExcludeSemantics
- Screen reader support

#### Key Code Patterns to Check

**1. Image Semantics**
```dart
// ISSUE: Image without semantics
Image.asset('assets/play.png')

// CORRECT: Semantic image
Semantics(
  label: 'Play',
  button: true,
  child: GestureDetector(
    onTap: handlePlay,
    child: Image.asset('assets/play.png'),
  ),
)

// CORRECT: Decorative image
ExcludeSemantics(
  child: Image.asset('assets/decorative.png'),
)
```

**2. Custom Buttons**
```dart
// ISSUE: Custom clickable widget without semantics
GestureDetector(
  onTap: handleSubmit,
  child: Container(
    child: Text('Submit'),
  ),
)

// CORRECT: Proper semantic button
Semantics(
  button: true,
  label: 'Submit',
  onTap: handleSubmit,
  child: GestureDetector(
    onTap: handleSubmit,
    child: Container(
      child: Text('Submit'),
    ),
  ),
)
```

---

## Audit Report Structure

### Report Organization

Create **separate reports for each platform** using this structure:

```
├── Accessibility_Audit_Report_[Platform]_[Date].md
├── screenshots/
│   ├── [platform]/
│   │   ├── issue_001_button_no_label.png
│   │   ├── issue_002_low_contrast.png
│   │   └── ...
```

---

### Report Template

```markdown
# Accessibility Audit Report
## [Platform Name] - [App Name]

**Date:** [Audit Date]
**Auditor:** [Name]
**WCAG Version:** 2.2
**Conformance Target:** Level AA
**Platform Version:** [OS/Browser versions tested]

---

## Executive Summary

**Total Issues Found:** [Number]
- Critical: [Number]
- High: [Number]
- Medium: [Number]
- Low: [Number]

**WCAG Success Criteria Violated:**
- [List of unique SCs violated]

**Overall Assessment:**
[Brief paragraph summarizing accessibility state]

---

## Methodology

**Testing Environment:**
- Device/Browser: [Details]
- OS Version: [Version]
- Assistive Technologies: [TalkBack, VoiceOver, NVDA, etc.]
- Testing Tools: [Scanners, validators used]

**Scope:**
- Screens/Pages audited: [List]
- Code files reviewed: [Number/List]

---

## Issues by Severity

### Critical Issues

#### Issue #001: [Brief Title]

**WCAG SC Violated:**
- **Primary:** [SC X.X.X - Name] (Level X)
- **Secondary:** [SC Y.Y.Y - Name] (Level Y)

**Severity:** Critical
**Impact:** [Who is affected and how]

**Location:**
- File: `path/to/file.ext`
- Line: `123`
- Screen: [Screen name]
- Component: [Component name]

**Description:**
[Detailed description of the issue]

**Current Code:**
```[language]
[Code snippet showing the issue]
```

**Recommended Fix:**
```[language]
[Code snippet showing the solution]
```

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Visual Evidence:**
![Screenshot showing issue](screenshots/[platform]/issue_001_description.png)

**Screen Reader Behavior:**
- Current: "[What screen reader announces]"
- Expected: "[What it should announce]"

**Resources:**
- [WCAG Understanding doc link]
- [Platform-specific documentation]

---

[Repeat for each issue]

---

## Issues by WCAG Guideline

### 1. Perceivable

#### 1.1 Text Alternatives

##### 1.1.1 Non-text Content (Level A)

**Issues:** #001, #005, #012

[Brief summary of these issues]

#### 1.3 Adaptable

##### 1.3.1 Info and Relationships (Level A)

**Issues:** #003, #007

[Brief summary]

##### 1.3.5 Identify Input Purpose (Level AA)

**Issues:** #009

[Brief summary]

#### 1.4 Distinguishable

##### 1.4.3 Contrast (Minimum) (Level AA)

**Issues:** #002, #008, #015

[Brief summary]

##### 1.4.11 Non-text Contrast (Level AA)

**Issues:** #011

[Brief summary]

### 2. Operable

#### 2.1 Keyboard Accessible

##### 2.1.1 Keyboard (Level A)

**Issues:** #004, #010

[Brief summary]

##### 2.1.2 No Keyboard Trap (Level A)

**Issues:** #013

[Brief summary]

#### 2.4 Navigable

##### 2.4.3 Focus Order (Level A)

**Issues:** #006

[Brief summary]

##### 2.4.7 Focus Visible (Level AA)

**Issues:** #014

[Brief summary]

#### 2.5 Input Modalities

##### 2.5.3 Label in Name (Level A)

**Issues:** #016

[Brief summary]

##### 2.5.8 Target Size (Minimum) (Level AA)

**Issues:** #017, #018

[Brief summary]

### 3. Understandable

#### 3.3 Input Assistance

##### 3.3.1 Error Identification (Level A)

**Issues:** #019

[Brief summary]

##### 3.3.2 Labels or Instructions (Level A)

**Issues:** #020, #021

[Brief summary]

### 4. Robust

#### 4.1 Compatible

##### 4.1.2 Name, Role, Value (Level A)

**Issues:** #001, #004, #005

[Brief summary]

---

## Recommendations Summary

### High Priority Fixes
1. [Action item 1]
2. [Action item 2]

### Process Improvements
1. [Recommendation for development process]
2. [Recommendation for testing procedures]

### Training Needs
- [Topics developers should be trained on]

---

## Appendix

### A. Testing Checklist Used
- [ ] All images have text alternatives
- [ ] All buttons have accessible labels
- [ ] Color contrast meets minimum ratios
- [ ] Keyboard navigation is functional
- [ ] Screen reader announces content correctly
- [etc.]

### B. Automated Scan Results
[Summary or attachment of automated tool results]

### C. Platform-Specific Requirements Met
- [ ] [Platform requirement 1]
- [ ] [Platform requirement 2]

---

## Sign-off

**Auditor:** [Name]
**Date:** [Date]
**Next Review Date:** [Recommended date]
```

---

## Common Issues Reference

### Quick WCAG SC Reference Table

| Issue Type | Primary SC | Secondary SC | Severity |
|------------|-----------|--------------|----------|
| Image without alt text | 1.1.1 | 4.1.2 | Critical |
| Button without label | 4.1.2 | 2.4.4 | Critical |
| Insufficient color contrast | 1.4.3 | 1.4.11 | High |
| Missing form label | 3.3.2 | 1.3.1, 4.1.2 | Critical |
| No keyboard access | 2.1.1 | 2.1.2 | Critical |
| No focus indicator | 2.4.7 | - | High |
| Small touch target (<24px) | 2.5.8 | - | Medium |
| Heading structure incorrect | 1.3.1 | 2.4.6 | Medium |
| No error identification | 3.3.1 | 3.3.3 | High |
| Custom control no role | 4.1.2 | - | Critical |
| Content not in landmarks | 1.3.1 | 2.4.1 | Medium |
| Link without purpose | 2.4.4 | 2.4.9 | Medium |
| Decorative image not hidden | 1.1.1 | - | Low |
| No skip link | 2.4.1 | - | Medium |
| Keyboard trap | 2.1.2 | - | Critical |
| Motion without pause | 2.2.2 | 2.3.3 | High |
| Dynamic content not announced | 4.1.3 | - | High |
| Incorrect language attribute | 3.1.1 | 3.1.2 | Medium |

---

### Common Patterns by Issue Type

#### 1. Missing Alternative Text

**WCAG SC:**
- 1.1.1 Non-text Content (Level A)
- 4.1.2 Name, Role, Value (Level A)

**Platforms Affected:** All

**Detection:**
- Web: `<img>` without `alt` attribute
- Android: `ImageView`/`Icon` without `contentDescription`
- iOS: `UIImageView`/`Image` without `accessibilityLabel`
- React Native: `<Image>` without `accessibilityLabel`

**Fix Pattern:** Provide descriptive text alternative or mark as decorative

---

#### 2. Unlabeled Interactive Elements

**WCAG SC:**
- 4.1.2 Name, Role, Value (Level A)
- 2.4.4 Link Purpose (In Context) (Level A)

**Platforms Affected:** All

**Detection:**
- Buttons with only icons
- Links with generic text ("click here")
- Custom interactive elements without semantic information

**Fix Pattern:** Add explicit accessible label describing the action

---

#### 3. Insufficient Color Contrast

**WCAG SC:**
- 1.4.3 Contrast (Minimum) (Level AA) - Text
- 1.4.11 Non-text Contrast (Level AA) - UI components

**Platforms Affected:** All

**Requirements:**
- Normal text: 4.5:1 minimum
- Large text (18pt+ or 14pt+ bold): 3:1 minimum
- UI components and graphics: 3:1 minimum

**Detection:**
- Use contrast checking tools
- Look for light gray text on white backgrounds
- Check disabled state styling

**Fix Pattern:** Adjust colors to meet minimum ratios

---

#### 4. Missing Form Labels

**WCAG SC:**
- 3.3.2 Labels or Instructions (Level A)
- 1.3.1 Info and Relationships (Level A)
- 4.1.2 Name, Role, Value (Level A)

**Platforms Affected:** All

**Detection:**
- Inputs with only placeholder text
- Form fields without associated labels
- Groups of inputs without fieldset/legend

**Fix Pattern:** Provide persistent, visible labels

---

#### 5. Keyboard Accessibility Issues

**WCAG SC:**
- 2.1.1 Keyboard (Level A)
- 2.1.2 No Keyboard Trap (Level A)
- 2.4.3 Focus Order (Level A)
- 2.4.7 Focus Visible (Level AA)

**Platforms Affected:** Web, Desktop apps

**Detection:**
- Interactive elements not in tab order
- Missing keyboard event handlers
- Illogical focus order
- No visible focus indicator

**Fix Pattern:** Ensure all functionality available via keyboard with logical order and visible focus

---

#### 6. Touch Target Size Issues

**WCAG SC:**
- 2.5.8 Target Size (Minimum) (Level AA)

**Platforms Affected:** Mobile (Android, iOS, React Native)

**Requirements:**
- Minimum 24×24 CSS pixels
- Recommended: 48×48 dp (Android), 44×44 pt (iOS)

**Detection:**
- Small buttons or tap areas
- Close-together interactive elements

**Fix Pattern:** Increase touch target size or add spacing

---

#### 7. Heading Structure Issues

**WCAG SC:**
- 1.3.1 Info and Relationships (Level A)
- 2.4.6 Headings and Labels (Level AA)

**Platforms Affected:** Web, Mobile

**Detection:**
- Skipped heading levels (h1 → h3)
- Text styled to look like heading but not marked as such
- Multiple h1 elements (web)

**Fix Pattern:** Use proper semantic heading hierarchy

---

#### 8. Dynamic Content Not Announced

**WCAG SC:**
- 4.1.3 Status Messages (Level AA)

**Platforms Affected:** All

**Detection:**
- Content updates without screen reader notification
- Loading states not announced
- Error messages appearing silently
- Success notifications not communicated

**Fix Pattern:**
- Web: ARIA live regions
- Android: LiveRegion semantics
- iOS: UIAccessibility announcements

---

## Resources

### WCAG Documentation
- **WCAG 2.2 Guidelines:** https://www.w3.org/TR/WCAG22/
- **Understanding WCAG 2.2:** https://www.w3.org/WAI/WCAG22/Understanding/
- **How to Meet WCAG (Quick Reference):** https://www.w3.org/WAI/WCAG22/quickref/
- **WCAG 2.2 on Mobile:** https://www.w3.org/TR/wcag2mobile-22/

### Platform-Specific Resources

#### Android
- **Accessibility Guide:** https://developer.android.com/guide/topics/ui/accessibility
- **Testing:** https://developer.android.com/guide/topics/ui/accessibility/testing
- **Jetpack Compose Accessibility:** https://developer.android.com/jetpack/compose/accessibility

#### iOS/tvOS
- **Human Interface Guidelines - Accessibility:** https://developer.apple.com/design/human-interface-guidelines/accessibility
- **UIAccessibility Documentation:** https://developer.apple.com/documentation/uikit/uiaccessibility
- **SwiftUI Accessibility:** https://developer.apple.com/documentation/swiftui/view-accessibility

#### Web
- **MDN Accessibility:** https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **WAI-ARIA Practices:** https://www.w3.org/WAI/ARIA/apg/
- **WebAIM:** https://webaim.org/

#### React Native
- **Accessibility Guide:** https://reactnative.dev/docs/accessibility

#### Flutter
- **Accessibility Guide:** https://docs.flutter.dev/ui/accessibility-and-internationalization/accessibility

### Testing Tools

#### Web
- axe DevTools
- WAVE
- Lighthouse
- Pa11y
- NVDA (screen reader)
- JAWS (screen reader)
- ChromeVox (screen reader)

#### Android
- Accessibility Scanner
- TalkBack
- Switch Access
- Espresso Accessibility Checks

#### iOS
- Xcode Accessibility Inspector
- VoiceOver
- Switch Control
- Voice Control

#### Cross-Platform
- Color Contrast Analyzers (TPGI, WebAIM)
- Accessible Name & Description Inspector (ANDI)

### Community Resources
- **WebAIM Mailing List:** https://webaim.org/discussion/
- **A11y Slack Community:** https://web-a11y.slack.com/
- **Deque Blog:** https://www.deque.com/blog/

---

## Version History

**Version 1.0** - [Current Date]
- Initial framework created
- Includes WCAG 2.2 guidelines
- Platform coverage: Web, Android, iOS, tvOS, React Native, Flutter

---

## Notes for Auditors

### Best Practices

1. **Be Specific:** Always provide file paths, line numbers, and exact locations
2. **Show Impact:** Explain how each issue affects real users
3. **Provide Solutions:** Include working code examples for fixes
4. **Visual Evidence:** Screenshot every issue when possible
4. **Test with Real AT:** Don't rely only on automated tools
5. **Consider Context:** Mobile apps have different patterns than web
6. **Stay Updated:** WCAG and platform guidelines evolve

### Screenshot Guidelines

**What to Capture:**
- The UI element with the issue highlighted
- Screen reader focus/output (if applicable)
- Contrast analyzer results
- Code editor showing the problematic code

**Naming Convention:**
```
issue_[number]_[brief_description].png
Example: issue_001_button_no_label.png
```

**Storage:**
```
screenshots/
├── web/
├── android/
├── ios/
├── tvos/
└── react_native/
```

### Severity Guidelines

**Critical:**
- Blocks core functionality
- Affects many users
- Violates Level A criteria
- Examples: Cannot submit form, cannot navigate with keyboard

**High:**
- Significantly impairs experience
- Affects moderate number of users
- Violates Level AA criteria
- Examples: Low contrast, missing headings

**Medium:**
- Degrades experience
- Affects specific user groups
- Best practice violation
- Examples: Suboptimal focus order, missing skip link

**Low:**
- Minor inconvenience
- Affects few users
- Enhancement opportunity
- Examples: Decorative image not hidden, verbose label

---

**End of Guide**
