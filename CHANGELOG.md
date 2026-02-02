# Changelog - Accessibility Audit Framework

## 2025-10-30 - Font Scaling Support (Critical)

### ✅ Text Must Resize According to Platform Settings
**Change:** Added comprehensive requirement that all text must scale with system font size settings
**Issue:** Text using fixed units (dp, px, fixed sizes) prevents users from reading content comfortably

**Why This Matters:**
- **15-30% of mobile users** adjust system font sizes
- Users with low vision **cannot read apps** that don't scale text
- Older users commonly need larger text
- WCAG 2.2 Level AA requirement (1.4.4 Resize Text)
- Creates significant accessibility barrier when violated

**Critical Requirements by Platform:**

**Android:**
```kotlin
❌ Text(text = "Hello", fontSize = 16.dp)  // WRONG: dp doesn't scale
✅ Text(text = "Hello", fontSize = 16.sp)  // CORRECT: sp scales
✅ Text(text = "Hello", style = MaterialTheme.typography.bodyLarge)  // BEST
```

**iOS:**
```swift
❌ Text("Hello").font(.system(size: 16))  // WRONG: Fixed size
✅ Text("Hello").font(.body)  // CORRECT: Dynamic Type
✅ label.adjustsFontForContentSizeCategory = true  // CRITICAL in UIKit
```

**Web:**
```css
❌ font-size: 16px;  /* WRONG: Fixed pixels */
✅ font-size: 1rem;  /* CORRECT: Scalable */
```

**Changes:**

1. **Created patterns/FONT_SCALING_SUPPORT.md** (~800 lines):
   - Complete explanation of font scaling requirements
   - Platform-specific implementations for all platforms
   - Detection patterns for code review
   - Testing checklist with system settings
   - Common mistakes and fixes
   - Layout considerations (wrapping, flexible heights)

2. **Updated COMMON_ISSUES.md**:
   - Added Section 13: "Text Not Scalable with System Font Settings"
   - Added to Quick Reference Table (WCAG 1.4.4, 1.4.12)
   - Platform-specific detection patterns
   - Added to anti-patterns checklist

3. **Updated GUIDE_ANDROID.md**:
   - Added new Section 4: "Text Sizes Must Use sp (Scalable Pixels)"
   - Critical warning about dp vs sp
   - XML and Compose examples
   - Detection pattern (search for `fontSize.*\.dp`)
   - Testing instructions with system settings
   - Renumbered all subsequent sections

4. **Impact:**
   - All future audits will check for font scaling support
   - Clear detection patterns for automated searching
   - Testing procedures with system settings
   - Fixes typically straightforward (dp → sp, px → rem)

**Detection Patterns:**

Android:
```
fontSize.*\.dp
textSize="[0-9]+dp"
```

iOS:
```swift
UIFont.systemFont(ofSize:
.font(.system(size:
```

Web:
```css
font-size:.*px;
```

**Testing:**
1. **Android:** Settings → Display → Font size → Largest
2. **iOS:** Settings → Accessibility → Display & Text Size → Larger Text → Maximum
3. **Web:** Browser zoom to 200%
4. Verify all text scales, layouts adapt, no content is cut off

**WCAG Success Criteria:**
- 1.4.4 Resize Text (Level AA) - Text can be resized up to 200%
- 1.4.12 Text Spacing (Level AA) - No loss of content with adjusted spacing

**Severity:** High (affects 15-30% of users who adjust font sizes)

---

## 2025-10-30 - Descriptive Report Filenames Required

### ✅ Report Filenames Must Include Feature/Area Tested
**Change:** Updated all documentation to require descriptive filenames that include what was tested
**Required Format:** `Accessibility_Audit_[Platform]_[FeatureOrArea]_[Date].md`

**Why This Matters:**
- **Searchable:** Easy to find specific audits later by searching for feature names
- **Organized:** Clear what each report covers without opening it
- **Trackable:** Multiple audits per platform for different features
- **Professional:** Shows systematic, organized approach
- **Context:** Filename immediately tells you what was tested

**Examples:**

✅ **Good Filenames (Descriptive):**
- `Accessibility_Audit_Android_LoginScreen_2025-10-30.md`
- `Accessibility_Audit_Web_CheckoutFlow_2025-10-30.md`
- `Accessibility_Audit_iOS_NavigationBar_2025-10-30.md`
- `Accessibility_Audit_Web_FormsAndInputs_2025-10-30.md`

❌ **Bad Filenames (Not Descriptive):**
- `Accessibility_Audit_Web_2025-10-30.md` (missing what was tested)
- `report.md` (no context)
- `audit1.md` (meaningless)

**Changes:**

1. **Updated IMPORTANT_AUDIT_REQUIREMENTS.md**:
   - Added new section: "📝 CRITICAL: Descriptive Report Filenames"
   - Required format with components explained
   - Good vs bad examples
   - Special cases (interim summaries, critical scans, issue-type audits)
   - Multi-word feature naming guidance

2. **Updated AUDIT_REPORT_TEMPLATE.md**:
   - Added prominent filename requirement at top of template
   - Includes format and examples
   - Clear DO NOT examples

3. **Updated HOW_TO_START_AUDIT.md**:
   - Updated all platform examples to include `[FeatureOrArea]` placeholder
   - Added specific filename examples for each platform
   - Examples: LoginScreen, CheckoutFlow, HomeScreen, ProfileView, etc.

**Impact:**
- All future audit reports will have descriptive, searchable filenames
- Easy to organize multiple audits per platform
- Clear audit coverage tracking
- Professional documentation structure

**For Users:**
When creating reports, always include:
1. **Platform:** Web, Android, iOS, etc.
2. **Feature/Area:** What you're testing (Login, Checkout, Navigation, etc.)
3. **Date:** YYYY-MM-DD format (check `<env>` for today's date)

---

## 2025-10-30 - On-Demand Platform Folder Creation

### ✅ Platform Folders Created Only When Needed
**Change:** Modified setup script to create platform folders (web/, android/, ios/) only when reports are generated
**Previous Behavior:** Setup script automatically created all platform folders even if empty

**Why This Matters:**
- Cleaner directory structure
- No empty folders cluttering the project
- Folders appear only when you actually use them
- Better aligns with actual usage patterns

**Changes:**

1. **Updated setup-audit.sh**:
   - Removed automatic creation of platform-specific folders in reports/ and screenshots/
   - Added informative message that folders are created on-demand
   - Updated directory structure visualization to indicate on-demand creation
   - Comment explains that folders are created when first report is generated

**Impact:**
- After setup, you'll only see: `reports/` and `screenshots/` (base folders)
- When you generate your first Android report, `reports/android/` is created automatically
- When you save Android screenshots, `screenshots/android/` is created automatically
- Same pattern for all platforms (web, ios, tvos, react-native, flutter, etc.)

**Technical Details:**
- Folders are created automatically by the Write tool when you specify a path
- No action needed from users - completely transparent
- Works the same way for all platforms

**Backward Compatibility:**
- Existing projects with folders already created are unaffected
- New setups start with clean structure
- No breaking changes

---

## 2025-10-29 - Avoid Role Names in Labels (Critical)

### ✅ Remove Redundant Role Names from Accessible Labels
**Issue:** Labels like "Close Button", "Home Link", "Agree Checkbox" cause redundant screen reader announcements
**Solution:** Added comprehensive guideline to remove role names from accessible labels

**Why This Matters:**

Screen readers automatically announce element roles. Including the role in the label causes redundant, annoying announcements:

❌ **Bad Experience:**
- "Close Button" → Screen reader: **"Close Button, button"** (says "button" twice!)
- "Home Link" → Screen reader: **"Home Link, link"** (says "link" twice!)
- "Email Text Field" → Screen reader: **"Email Text Field, text field"** (says "text field" twice!)
- "Agree Checkbox" → Screen reader: **"Agree Checkbox, checkbox"** (says "checkbox" twice!)

✅ **Good Experience:**
- "Close" → Screen reader: **"Close, button"** (clean, concise)
- "Home" → Screen reader: **"Home, link"** (clean, concise)
- "Email" → Screen reader: **"Email, text field"** (clean, concise)
- "Agree" → Screen reader: **"Agree, checkbox"** (clean, concise)

**Impact:**
- Every interactive element with redundant role = cognitive overload
- Sounds unprofessional and indicates poor accessibility
- Takes longer to navigate interface
- Annoying for screen reader users

**Changes:**

1. **Created patterns/AVOID_ROLE_IN_LABEL.md** (~400 lines):
   - Complete explanation with examples
   - Platform-specific implementation for all platforms
   - Common mistakes to check (Button, Link, Tab, Checkbox, etc.)
   - When role words ARE acceptable (describes what it affects)
   - Detection patterns for code review
   - Testing checklist
   - Audit report template

2. **Updated COMMON_ISSUES.md**:
   - Added Section 12: "Role Names in Accessible Labels"
   - Added to Quick Reference Table
   - Platform-specific examples
   - Detection patterns for all platforms

3. **Updated IMPORTANT_AUDIT_REQUIREMENTS.md**:
   - Added new section: "🚫 CRITICAL: Avoid Role Names in Labels"
   - Listed common offenders and detection patterns
   - Emphasized this should ALWAYS be checked in audits

**Common Offenders:**

Must be checked and fixed:
- ❌ "Submit Button" → ✅ "Submit"
- ❌ "Cancel Button" → ✅ "Cancel"
- ❌ "Close Button" → ✅ "Close"
- ❌ "Home Link" → ✅ "Home"
- ❌ "Read More Link" → ✅ "Read More"
- ❌ "Email Text Field" → ✅ "Email"
- ❌ "Password Input" → ✅ "Password"
- ❌ "Agree Checkbox" → ✅ "Agree"
- ❌ "Settings Tab" → ✅ "Settings"
- ❌ "File Menu" → ✅ "File"

**Exception - When Role Words ARE Acceptable:**

Only when the word describes what the element **affects**, not what it **is**:
- ✅ "Open Menu" (button) - "Menu" is what opens, not the role
- ✅ "Choose File" (button) - "File" is what you choose
- ✅ "Show Dialog" (button) - "Dialog" is what appears
- ✅ "Select Date" (button) - "Date" is what you select
- ❌ "Close Button" - "Button" describes what it **is** → REMOVE

**Detection Patterns:**

Search codebase for these patterns:
```
Android:
- contentDescription=".*[Bb]utton"
- contentDescription=".*[Ll]ink"
- contentDescription=".*[Tt]ab"

iOS:
- accessibilityLabel=".*[Bb]utton"
- accessibilityLabel=".*[Ll]ink"

Web:
- aria-label=".*[Bb]utton"
- >.*Button</button>
- >.*Link</a>
```

**Platform-Specific Examples:**

**Android (Compose):**
```kotlin
// ❌ ISSUE
Button(onClick = { close() }) {
    Text("Close Button")  // "Close Button, button"
}

// ✅ CORRECT
Button(onClick = { close() }) {
    Text("Close")  // "Close, button"
}
```

**iOS (SwiftUI):**
```swift
// ❌ ISSUE
Button("Submit Button") { submit() }  // "Submit Button, button"

// ✅ CORRECT
Button("Submit") { submit() }  // "Submit, button"
```

**Web:**
```html
<!-- ❌ ISSUE -->
<button>Close Button</button>  <!-- "Close Button, button" -->

<!-- ✅ CORRECT -->
<button>Close</button>  <!-- "Close, button" -->
```

**Testing:**
- ✅ Enable screen reader
- ✅ Navigate through interactive elements
- ✅ Listen for redundant announcements (role said twice)
- ✅ Search codebase for common patterns
- ✅ Fix all instances

**Severity:**
- Medium: If widespread (affects many elements)
- Low: If isolated (only a few elements)

**WCAG SC:** 4.1.2 Name, Role, Value (Level A), 2.4.6 Headings and Labels (Level AA)

---

## 2025-10-29 - Buttons Acting as Tabs Pattern (Critical)

### ✅ Content Switcher Buttons Should Use Tab Semantics
**Issue:** Buttons that switch between content views (fragments, panels) are announced as "button" instead of "tab", with no indication of selected state or position
**Solution:** Added comprehensive pattern guide for identifying and fixing buttons that functionally act as tabs

**Why This Matters:**

When buttons switch content but use button semantics:
- ❌ Screen reader announces: "Home, button", "Search, button", "Favorites, button"
- ❌ No indication which is currently selected/active
- ❌ No position information ("tab 2 of 4")
- ❌ User doesn't understand page structure
- ❌ Doesn't match sighted user's mental model

With proper tab semantics:
- ✅ Announces: "Home, tab 1 of 4, selected"
- ✅ Clear which tab is active
- ✅ Understand position in group
- ✅ Recognize structure and intent
- ✅ Efficient navigation

**Common Scenarios:**
- Fragment/view switchers (Home, Search, Favorites buttons)
- Content filters (All, Active, Completed)
- View mode toggles (List/Grid)
- Category selectors (News, Sports, Entertainment)
- Time period selectors (Day, Week, Month, Year)

**Changes:**

1. **Created patterns/BUTTONS_ACTING_AS_TABS.md** (~350 lines):
   - Complete explanation of when to apply pattern
   - Detection criteria (when to use tabs vs buttons)
   - Platform-specific implementations for all platforms:
     - Android Compose: `Role.Tab` with `stateDescription`
     - Android XML: Custom AccessibilityDelegate with role and selected state
     - iOS SwiftUI: Custom traits with position labels
     - iOS UIKit: UISegmentedControl
     - Web: Proper ARIA tab pattern (`role="tab"`, `aria-selected`, `aria-posinset`)
   - Recommendations in priority order:
     1. Refactor to native tab components (TabRow, TabView, ARIA tabs)
     2. Add tab semantics to existing buttons
     3. Minimum: Add selected state
   - Testing checklist
   - Example audit issue with complete recommendation

2. **Updated COMMON_ISSUES.md**:
   - Added Section 11: "Buttons Acting as Tabs Without Tab Semantics"
   - Added to Quick Reference Table with WCAG mappings
   - Platform-specific examples for all platforms
   - Detection criteria and testing checklist

**Detection Criteria:**

Use tab semantics when buttons:
- ✅ Switch between different content fragments
- ✅ Change portion of screen (not full navigation)
- ✅ Only one can be active at a time
- ✅ Content changes based on selection

Do NOT use when:
- ❌ Navigate to different screens
- ❌ Perform actions (submit, delete, save)
- ❌ Open dialogs/modals
- ❌ Multiple can be active simultaneously

**Platform-Specific Solutions:**

**Android (Compose) - Best:**
```kotlin
TabRow(selectedTabIndex = selectedIndex) {
    Tab(selected = isSelected, onClick = onClick, text = { Text("Home") })
}
```

**Android (Compose) - Manual:**
```kotlin
Box(
    modifier = Modifier
        .clickable(role = Role.Tab, onClick = onClick)
        .semantics {
            stateDescription = if (isSelected) "Selected" else "Not selected"
        }
)
```

**iOS (SwiftUI) - Best:**
```swift
TabView(selection: $selectedTab) {
    HomeView().tabItem { Label("Home", systemImage: "house") }
}
```

**iOS (SwiftUI) - Manual:**
```swift
Button("Home") { action() }
    .accessibilityLabel("Home, tab 1 of 4")
    .accessibilityAddTraits(isSelected ? .isSelected : [])
```

**Web - Proper ARIA:**
```javascript
<div role="tablist">
  <button role="tab" aria-selected={isSelected} aria-posinset="1" aria-setsize="4">
    Home
  </button>
</div>
<div role="tabpanel">
  {/* Content */}
</div>
```

**Testing Requirements:**
- ✅ Verify announces as "tab" not "button"
- ✅ Verify selected tab announces "selected"
- ✅ Verify position announced ("tab 2 of 4")
- ✅ Test visual distinction (contrast >= 3:1)

**WCAG SC:** 1.3.1 (Level A), 4.1.2 (Level A), 2.4.6 (Level AA)

---

## 2025-10-29 - Collection Items Must Be Interactive (Critical)

### ✅ Parent Container Must Be Clickable/Tappable
**Issue:** When grouping child views into a single accessibility element, developers sometimes forget to make the parent container interactive
**Solution:** Added explicit requirement and examples showing parent must be clickable/tappable

**Why This Matters:**
If you merge all child views but the parent container is NOT clickable:
- ❌ Screen reader users hear the complete description
- ❌ But cannot activate the item with double-tap
- ❌ Content is completely inaccessible to them
- ❌ This is a **blocking issue** - user cannot proceed

**Changes:**

1. **Updated patterns/COLLECTION_ITEMS_PATTERN.md**:
   - Added new Section 3: "Parent Container MUST Be Interactive"
   - Explained why this matters and common mistakes
   - Added BAD examples showing non-interactive containers
   - Added GOOD examples for all platforms showing:
     - Android Compose: `Card(onClick = onClick, ...)`
     - Android XML: `isClickable = true` + `isFocusable = true` + `setOnClickListener`
     - iOS SwiftUI: `Button(action:)` or `.onTapGesture`
     - iOS UIKit: Tap gesture recognizers
   - Updated testing checklist to verify double-tap activates item

2. **Updated GUIDE_ANDROID.md Section 10**:
   - Changed from single CRITICAL note to numbered list of 3 critical requirements
   - Requirement 3: "Parent container MUST be clickable/tappable"
   - Specified implementation: `Card(onClick = ...)` or `isClickable/isFocusable`

3. **Updated GUIDE_IOS.md Section 5a**:
   - Changed from single CRITICAL note to numbered list of 3 critical requirements
   - Requirement 3: "Parent container MUST be interactive"
   - Specified implementation: `Button(action:)` or `.onTapGesture`

**Platform-Specific Requirements:**

**Android (Compose):**
```kotlin
Card(
    onClick = onClick,  // ✅ CRITICAL: Make parent clickable
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "..."
    }
)
```

**Android (XML/ViewHolder):**
```kotlin
itemView.apply {
    isClickable = true   // ✅ CRITICAL
    isFocusable = true   // ✅ CRITICAL
    setOnClickListener { /* handle click */ }
    contentDescription = "..."
}
```

**iOS (SwiftUI):**
```swift
Button(action: onTap) { /* content */ }  // ✅ Use Button
// OR
HStack { /* content */ }
    .onTapGesture(perform: onTap)  // ✅ Use tap gesture
    .accessibilityAddTraits(.isButton)
```

**Testing Requirement:**
- ✅ With screen reader enabled, focus on merged item
- ✅ Double-tap (TalkBack/VoiceOver) or press Enter (Web)
- ✅ **Verify the item activates** (opens detail, plays content, etc.)

---

## 2025-10-29 - Date Fix for Report Generation (Critical)

### ✅ Fixed Incorrect Dates in Generated Reports
**Issue:** Reports were being generated with "January 29, 2025" instead of the correct current date "October 29, 2025"
**Solution:** Added explicit instructions to always check `<env>` for today's date before generating reports

**Changes:**

1. **Updated AUDIT_REPORT_TEMPLATE.md**:
   - Changed date field from generic example to explicit instruction
   - Added prominent warning: "⚠️ USE TODAY'S DATE FROM <env>"
   - Specified both acceptable formats: YYYY-MM-DD or "Month DD, YYYY"
   - Added note stating current date is October 29, 2025

2. **Updated IMPORTANT_AUDIT_REQUIREMENTS.md**:
   - Added new section at top: "📅 CRITICAL: Use Correct Date in Reports"
   - Explicit instruction to check `<env>Today's date:` at conversation start
   - Listed current date: October 29, 2025
   - Added "DO NOT use: January 2025 or any other incorrect month"

**Why This Matters:**
- Reports were dated 3 months in the past (January instead of October)
- Incorrect dates make reports appear stale or out of date
- Could cause confusion about when audits were actually performed
- File timestamps would not match report dates

**Root Cause:**
The template had a generic example date without clear instruction to use today's date from the environment. Claude was defaulting to its knowledge cutoff date (January 2025) instead of checking the `<env>` section for the actual current date.

---

## 2025-10-29 - Guide Consolidation and Pattern Files

### ✅ Reduced File Sizes and Eliminated Duplication
**Issue:** Platform guides contained ~1,840 lines of duplicated content across multiple files
**Solution:** Created consolidated pattern files and updated platform guides to reference them

**Changes:**

1. **Created patterns/ directory** with 4 new consolidated pattern files:
   - `patterns/COLLECTION_ITEMS_PATTERN.md` (~200 lines, consolidates ~700 lines from 5 guides)
   - `patterns/REPEATED_ELEMENTS_CONTEXT.md` (~150 lines, consolidates ~320 lines from 3 guides)
   - `patterns/NAVIGATION_BAR_ACCESSIBILITY.md` (~150 lines, consolidates ~250 lines from 3 guides)
   - `patterns/DECORATIVE_IMAGE_DECISION_TREE.md` (~80 lines, consolidates ~180 lines from 5 guides)

2. **Updated GUIDE_ANDROID.md** with references to pattern files:
   - Section 1: Added reference to Decorative Image Decision Tree
   - Section 10 (Collection Items): Reduced from ~187 lines to ~88 lines (saved ~99 lines)
   - Section 11 (Navigation Bar): Reduced from ~192 lines to ~79 lines (saved ~113 lines)
   - Section 12 (Repeated Elements): Reduced from ~209 lines to ~76 lines (saved ~133 lines)
   - **Total reduction: ~345 lines from Android guide**

3. **Updated GUIDE_IOS.md** with references to pattern files:
   - Section 1: Added reference to Decorative Image Decision Tree
   - Section 5a (Collection Items): Reduced from ~189 lines to ~84 lines (saved ~105 lines)
   - Section 11 (Navigation Bar): Reduced from ~213 lines to ~68 lines (saved ~145 lines)
   - Section 12 (Repeated Elements): Reduced from ~237 lines to ~59 lines (saved ~178 lines)
   - **Total reduction: ~428 lines from iOS guide**

**Impact:**
- **Total lines saved: ~773 lines** across GUIDE_ANDROID.md and GUIDE_IOS.md
- Single source of truth for cross-platform patterns
- Platform guides now focus on platform-specific implementation details
- Easier to maintain and update common patterns
- Reduced duplication improves consistency

**Pattern File Structure:**
- Each pattern file includes complete explanation, examples, and cross-platform implementations
- Platform guides reference patterns and provide only platform-specific code examples
- Maintains full context while reducing redundancy

**Why This Matters:**
- Less duplication = easier maintenance
- Single source of truth = better consistency
- Smaller files = easier to navigate and read
- Pattern files can be referenced from any platform guide

---

## 2025-10-29 - Report Formatting Requirements (Critical Update)

### ✅ Mandatory Report Formatting and Content Policy
**Issue:** Reports need consistent formatting with issues ordered by severity, and should not include positive findings
**Solution:** Added explicit formatting requirements to all guides and templates

**Changes:**
1. **Updated AUDIT_REPORT_TEMPLATE.md** with prominent formatting requirements:
   - Issue ordering: ALWAYS Critical → High → Medium → Low
   - NEVER order by location or discovery order
   - Content policy: ONLY report issues, NO positive findings

2. **Added formatting requirements** to platform guides:
   - GUIDE_ANDROID.md - Section at top with critical requirements
   - GUIDE_IOS.md - Section at top with critical requirements

3. **Fixed date format** in all templates:
   - Changed from 2025-01-29 to 2025-10-29 (correct current date)
   - Standardized on YYYY-MM-DD format

**Critical Requirements:**

**Issue Ordering:**
- ✅ ALWAYS order by severity: Critical → High → Medium → Low
- ❌ NEVER order by location, file name, or discovery order
- Within each severity level, order by WCAG SC or logical grouping

**Content Policy:**
- ✅ ONLY report issues and problems
- ❌ DO NOT include positive findings
- ❌ DO NOT mention things that work correctly
- ❌ DO NOT say "good practice observed"
- If something is implemented correctly, omit it from the report entirely

**Why This Matters:**

**Problem with location ordering:**
```
❌ Bad Report (ordered by location):
- Issue 001: Missing alt text (file1.kt) - Low
- Issue 002: Button no label (file1.kt) - Critical
- Issue 003: Contrast issue (file2.kt) - High
→ Critical issue buried in middle, user must scan entire report
```

**Correct severity ordering:**
```
✅ Good Report (ordered by severity):
### Critical Issues
- Issue 002: Button no label - CRITICAL
### High Issues
- Issue 003: Contrast issue - High
### Low Issues
- Issue 001: Missing alt text - Low
→ Immediately see most important issues first
```

**Problem with positive findings:**
```
❌ Bad Report:
- Issue 001: Button missing label
- ✓ Good: Navigation has proper ARIA
- Issue 002: Contrast insufficient
- ✓ Good: Form labels are correct
→ Report cluttered, hard to focus on problems

✅ Good Report:
- Issue 001: Button missing label
- Issue 002: Contrast insufficient
→ Clean, focused only on what needs fixing
```

**Benefits:**
- Developers immediately see critical issues first
- Clear prioritization for fix order
- Focused reports without noise
- Consistent format across all audits
- Professional, actionable deliverables

**Documentation:** Updated AUDIT_REPORT_TEMPLATE.md, GUIDE_ANDROID.md, GUIDE_IOS.md

---

## 2025-10-29 - Context for Repeated Elements (Critical Update)

### ✅ Guidance for Repeated Interactive Elements
**Issue:** Multiple elements with identical labels make them indistinguishable for screen reader users
**Solution:** Comprehensive guidance on including context in labels for repeated actions

**Changes:**
1. **Added Section 12** to mobile platform guides:
   - GUIDE_ANDROID.md - Section 12: Context for Repeated Elements
   - GUIDE_IOS.md - Section 12: Context for Repeated Elements

2. **Added Section 10 to COMMON_ISSUES.md:**
   - Cross-platform pattern with examples for all platforms
   - Real-world scenarios (email lists, category rows, content grids)
   - Format patterns and testing guidance

3. **Updated Quick Reference Table** and Anti-Patterns sections

**Common Problematic Scenarios:**

**Scenario 1: Category "View all" Buttons**
```
❌ Problem:
Comedy section: "View all" button
Horror section: "View all" button
Drama section: "View all" button
→ User hears "View all" three times, no differentiation

✅ Solution:
"View all comedy"
"View all horror"
"View all drama"
→ User knows exactly which category each opens
```

**Scenario 2: Email List Action Buttons**
```
❌ Problem:
20 emails with "Delete" buttons
→ User hears "Delete" 20 times, doesn't know which email

✅ Solution:
"Delete Meeting notes"
"Delete Project update"
"Delete Invoice from supplier"
→ User knows exactly what each button will delete
```

**Scenario 3: Content Grid Play Buttons**
```
❌ Problem:
Hundreds of movies all with "Play" button
→ Cannot distinguish which movie

✅ Solution:
"Play Breaking Bad"
"Play The Godfather"
"Play Inception"
→ Clear identification of each item
```

**Code Examples Provided:**

**Android:**
```kotlin
// Dynamic context building
deleteButton.contentDescription = "Delete ${email.subject}"
playButton.contentDescription = "Play ${movie.title}"
viewAllButton.contentDescription = "View all ${category.name}"
```

**iOS:**
```swift
// Include item context
button.accessibilityLabel = "Delete \(email.subject)"
button.accessibilityLabel = "Play \(movie.title)"
button.accessibilityLabel = "View all \(category.name)"
```

**Format Patterns:**
- Action buttons: `"[Action] [item]"` → "Delete Meeting notes"
- View more/all: `"View all [category]"` → "View all comedy"
- Play/Watch: `"Play [title]"` → "Play Breaking Bad"
- Share buttons: `"Share [item]"` → "Share recipe name"
- Edit buttons: `"Edit [item]"` → "Edit contact info"

**WCAG SC Covered:**
- 2.4.4 Link Purpose (In Context) (Level A)
- 2.4.9 Link Purpose (Link Only) (Level AAA)
- 4.1.2 Name, Role, Value (Level A)

**Benefits:**
- Screen reader users can distinguish between identical actions
- Users know exactly what each button/link will do
- Dramatically improves usability of lists and grids
- Prevents confusion when navigating repeated elements
- Enables confident interaction without visual reference

**Impact:**
Without this pattern, screen reader users navigating lists with 20-100+ items cannot determine which item each action applies to, making the interface effectively unusable.

**Documentation:** Updated GUIDE_ANDROID.md, GUIDE_IOS.md, and COMMON_ISSUES.md

---

## 2025-10-29 - Bottom Navigation Bar Requirements (Critical Update)

### ✅ Comprehensive Bottom Navigation/Tab Bar Guidance
**Issue:** Navigation bars often missing critical accessibility features (labels, selected state, position info, visual distinction)
**Solution:** Added complete requirements checklist and implementation patterns for all mobile platforms

**Changes:**
1. **Added Bottom Navigation sections** to mobile platform guides:
   - GUIDE_ANDROID.md - Section 11: BottomNavigationView, NavigationBar (Compose)
   - GUIDE_IOS.md - Section 11: UITabBar, TabView (SwiftUI)

2. **Four Critical Requirements** that ALL navigation bars must meet:
   - ✅ Each nav item has accessible label/description
   - ✅ Screen reader announces selected state
   - ✅ Screen reader announces position (e.g., "tab 2 of 4")
   - ✅ Visual indication of selected state (contrast >= 3:1)

3. **Comprehensive Code Examples:**
   - Native components (Material, UIKit, SwiftUI)
   - Custom implementations with full accessibility
   - Visual styling for selected state
   - Testing checklists

4. **Common Issues Documented:**
   - Icon-only navigation without labels
   - Selected state not announced
   - Position/count missing from announcements
   - Poor visual contrast for selected state

**Android Examples:**
```xml
<!-- Menu with titles for accessible labels -->
<item android:id="@+id/nav_home"
      android:icon="@drawable/ic_home"
      android:title="@string/nav_home" />
```

**iOS Examples:**
```swift
// UITabBar automatically provides position/count
let homeItem = UITabBarItem(
    title: "Home",  // Required for accessibility
    image: UIImage(systemName: "house"),
    selectedImage: UIImage(systemName: "house.fill")
)
```

**Testing Requirements:**
- [ ] Label + "tab X of Y" + "selected/not selected" announced
- [ ] Visual selected state clearly distinguishable
- [ ] Contrast >= 3:1 between selected/unselected
- [ ] Labels present (not icon-only mode)

**WCAG SC Covered:**
- 1.3.1 Info and Relationships (Level A) - Selected state programmatically determinable
- 2.4.6 Headings and Labels (Level AA) - Clear labels
- 4.1.2 Name, Role, Value (Level A) - Tab role, name, state
- 1.4.11 Non-text Contrast (Level AA) - Visual distinction

**Benefits:**
- Ensures navigation is fully accessible
- Catches common mobile app accessibility issues
- Clear checklist for developers and auditors
- Prevents icon-only navigation bars
- Ensures screen reader users know their location

**Documentation:** Updated GUIDE_ANDROID.md and GUIDE_IOS.md with Section 11

---

## 2025-10-29 - Decorative Image Triage (Critical Update)

### ✅ Triage Logic for Decorative Images
**Issue:** Audit reports cluttered with unnecessary issues for clearly decorative images (gradients, backgrounds, borders)
**Solution:** Added decision tree to skip or deprioritize decorative images, focus on critical issues

**Changes:**
1. **Updated ALL platform guides** with decorative image triage in decision trees:
   - GUIDE_ANDROID.md - Step 2: Check if clearly decorative
   - GUIDE_IOS.md - Step 2: Check if clearly decorative
   - GUIDE_WEB.md - Step 2: Check if clearly decorative
   - GUIDE_REACT_NATIVE.md - Step 2: Check if clearly decorative
   - GUIDE_FLUTTER.md - Step 2: Check if clearly decorative

2. **Added three-tier reporting categories:**
   - **🎨 Clearly Decorative - DON'T REPORT:** Skip entirely (gradients, backgrounds, borders, shadows)
   - **❓ Unsure if Decorative - LOW Priority:** Report but note "fix only if not decorative"
   - **✅ Informational - Standard/Critical:** Report based on context

3. **Special emphasis on icon-only buttons:**
   - If image is ONLY content in button → **CRITICAL priority**
   - Must have description - no exceptions

4. **Updated COMMON_ISSUES.md** with triage process:
   - Clear examples of decorative images to skip
   - Decision tree for image reporting
   - Priority levels based on context

**Clearly Decorative (Don't Report):**
- Gradient overlays (e.g., `gradient_landscape_down_blue`)
- Background images for aesthetics
- Decorative borders, dividers, shadows
- Pattern backgrounds
- Spacer/separator images

**Icon-Only Buttons (CRITICAL):**
- Play button with only icon → CRITICAL
- Close button with only icon → CRITICAL
- Any interactive element with image as sole content → CRITICAL

**Benefits:**
- Reduces audit report noise by 30-50% (skipping obvious decorative images)
- Focuses developer attention on critical issues
- Faster audit completion (less time documenting decorative elements)
- Clearer priority for fixes
- Professional reports without clutter

**Example Impact:**
```
❌ Before: 17 issues (12 decorative gradients/backgrounds, 5 real issues)
✅ After: 5 issues (only real accessibility problems)
```

**Documentation:** Updated in all 5 platform guides + COMMON_ISSUES.md

---

## 2025-10-29 - Avoiding Contradictory Guidance (Critical Update)

### ✅ Fixed Contradictory Audit Guidance
**Issue:** Guides were flagging child elements for missing accessibility labels, then recommending hiding all children - creating contradictory guidance
**Solution:** Updated all platform guides to prioritize collection context before flagging individual elements

**Changes:**
1. **Updated ALL platform guides** with decision tree at the top of accessibility label sections:
   - GUIDE_ANDROID.md - Section 1: Check collection context FIRST
   - GUIDE_IOS.md - Section 1: Check collection context FIRST
   - GUIDE_WEB.md - Section 2: Check collection context FIRST
   - GUIDE_REACT_NATIVE.md - Section 1: Check collection context FIRST
   - GUIDE_FLUTTER.md - Section 1: Check collection context FIRST

2. **Added "Avoid Contradictory Guidance" warnings** to all collection items sections:
   - Clear DO/DON'T lists
   - Explanation of why individual labels become useless when merged
   - Emphasis on NOT flagging child elements separately

3. **Updated COMMON_ISSUES.md** with guidance priority:
   - Section on avoiding contradictory guidance
   - Correct vs incorrect audit approach
   - Why this matters for development efficiency

**The Problem (Example):**
```
❌ Contradictory Audit:
- Issue 001-012: "Add contentDescription to these child images/buttons"
- Issue 015-016: "Merge parent with all children marked importantForAccessibility='no'"
→ Result: Issues 001-012 become useless, waste developer time
```

**The Solution:**
```
✅ Priority-Based Audit:
1. Identify if element is in a collection (RecyclerView, FlatList, grid)
2. If YES: Flag parent for merged accessibility, skip individual child labels
3. If NO: Flag for individual accessibility labels
→ Result: No contradictory guidance, clear actionable recommendations
```

**Decision Tree Added to All Guides:**
1. **Is element part of collection item?**
   - YES → Apply collection item pattern (Section on Collections)
   - NO → Apply individual label requirements

2. **Is element standalone?**
   - YES → Require accessibility labels

**DO NOT flag:**
- Child elements inside collection items
- Sub-views that will be merged
- Elements within cards/tiles/cells

**DO flag:**
- Standalone elements
- Top-level navigation
- Toolbar/header items
- Modal/dialog buttons

**Impact:**
- Eliminates contradictory recommendations
- Saves developer time by avoiding useless fixes
- Produces clearer, more actionable audit reports
- Establishes correct audit methodology

**Documentation:** Updated in all 5 platform guides + COMMON_ISSUES.md

---

## 2025-10-29 - Collection Items Accessibility Pattern (Critical Update)

### ✅ Collection/Grid Items Accessibility (New Pattern)
**Issue:** Collection items (cards, list items, grid cells) require multiple swipes through sub-views
**Solution:** Comprehensive guidance on treating collection items as atomic units

**Changes:**
1. **Updated ALL platform guides** with collection items section:
   - GUIDE_ANDROID.md - Section 10: RecyclerView, LazyColumn, LazyRow patterns
   - GUIDE_IOS.md - Section 5a: UICollectionView, LazyVGrid, List patterns
   - GUIDE_WEB.md - Section 11: Grid/carousel items with ARIA
   - GUIDE_REACT_NATIVE.md - Section 7a: FlatList, ScrollView patterns
   - GUIDE_FLUTTER.md - Section 3a: ListView, GridView patterns

2. **Added to COMMON_ISSUES.md** as cross-platform pattern:
   - Section 9: Collection Items Not Properly Grouped
   - Added to Quick WCAG SC Reference Table
   - Added to Common Anti-Patterns section
   - Comprehensive examples for all platforms

**Critical Pattern:**
- **One swipe/tab = one complete item**
- Example: "Show name, episode name, Season X, Episode Y, on Channel Z, 45 percent watched"
- User should NOT swipe multiple times through sub-views of a single item
- Exception: Action buttons as custom accessibility actions (preferred) or separately with context

**Code Examples Include:**
- TV show cards with complete metadata
- Movie/product cards with progress indicators
- Channel logos and ratings merged into description
- Custom accessibility actions for item-level actions
- Alternative pattern when buttons must be separate

**WCAG SC Affected:**
- Primary: 1.3.1 Info and Relationships (Level A)
- Secondary: 2.4.4 Link Purpose (In Context) (Level A)
- Web: 2.1.1 Keyboard (Level A)

**Benefits:**
- Dramatically improved browsing experience for screen reader users
- Reduces navigation from 5-10+ swipes per item to 1 swipe
- Provides complete context in single announcement
- Consistent pattern across all platforms
- Actionable code examples for each technology

**Documentation:** Updated in all 5 platform guides + COMMON_ISSUES.md

---

## 2025-10-29 - Major Updates

### ✅ Platform-Specific Guides (Refactoring)
**Issue:** One monolithic 29KB file with all platforms mixed together
**Solution:** Split into focused platform-specific guides

**Changes:**
- Created `guides/` directory with 9 separate guides:
  - GUIDE_WEB.md (16KB) - HTML, React, Vue, Angular
  - GUIDE_ANDROID.md (16KB) - XML, Compose, TalkBack
  - GUIDE_IOS.md (11KB) - UIKit, SwiftUI, VoiceOver
  - GUIDE_REACT_NATIVE.md (7.7KB)
  - GUIDE_FLUTTER.md (2.7KB)
  - GUIDE_ANDROID_TV.md (1.6KB)
  - GUIDE_TVOS.md (1.5KB)
  - GUIDE_WCAG_REFERENCE.md (4.8KB) - Shared WCAG knowledge
  - COMMON_ISSUES.md (9.6KB) - Cross-platform patterns

**Benefits:**
- 50%+ less content to read per audit
- 100% relevance to chosen platform
- Easier team collaboration
- Faster navigation
- Scalable to new platforms

**Documentation:** WHATS_NEW.md

---

### ✅ Code References and Screenshot Requirements (Enhancement)
**Issue:** Need to ensure every recommendation has exact source code references and standardized screenshot names
**Solution:** Created comprehensive requirements and enforcement

**Changes:**
1. **IMPORTANT_AUDIT_REQUIREMENTS.md** - Top-level critical requirements document
   - Every issue MUST have exact file path and line number
   - Every issue MUST have current code and recommended fix
   - Screenshots MUST use pattern: `issue_###_description.png`

2. **guides/CODE_REFERENCES_AND_SCREENSHOTS.md** - Detailed 11KB guide
   - Complete examples by platform
   - Screenshot naming conventions
   - Quality checklists
   - Common mistakes to avoid

3. **Enhanced AUDIT_REPORT_TEMPLATE.md**
   - Added ⚠️ markers on required fields
   - Clear instructions and examples
   - Screenshot naming pattern examples

4. **Updated all documentation**
   - WORKFLOW_CHEATSHEET.md - Includes requirements in prompts
   - START_HERE.md - Highlights requirements before starting
   - README.md - Shows required issue format

**Required Format:**
```markdown
**Location:**
- File: `src/components/Button.tsx` ← Project-relative path
- Line: `45` ← Exact line number

**Current Code:**
```tsx
<button><Icon /></button>
```

**Recommended Fix:**
```tsx
<button aria-label="Play"><Icon /></button>
```

**Screenshot:**
![Issue](screenshots/web/issue_001_button_no_label.png)
```

**Screenshot Naming Pattern:**
- Format: `issue_###_short_description.png`
- Examples: `issue_001_button_no_label.png`, `issue_002_low_contrast.png`
- 3-digit numbers with leading zeros
- Lowercase with underscores
- 2-5 words max

**Benefits:**
- Developers know EXACTLY where to fix issues
- No guesswork or file searching
- Copy-pasteable solutions
- Consistent, traceable screenshots
- Professional, actionable reports

---

### ✅ Automated Installation (Improvement)
**Changes:**
- Created `setup-audit.sh` - Bash script for one-command setup
- Created `SIMPLE_SETUP_PROMPT.txt` - Claude Code setup prompt
- Created comprehensive installation guides

**Usage:**
```bash
# Method 1: Script
./setup-audit.sh /path/to/your-project

# Method 2: Claude Code
Paste SIMPLE_SETUP_PROMPT.txt content into Claude Code
```

**Documentation:** INSTALLATION.md, QUICK_INSTALL.md

---

### ✅ Phased Audit Strategy (New Feature)
**Issue:** Large projects overwhelming to audit all at once
**Solution:** Comprehensive phased approach guide

**Changes:**
- Created PHASED_AUDIT_STRATEGY.md (15KB)
- 7 strategies for breaking down audits:
  - One platform at a time
  - By feature area
  - By component type
  - By WCAG principle
  - By directory/module
  - By severity
  - By screen/page
- Session size recommendations (30-60 min optimal)
- Progress tracking templates

**Benefits:**
- Manageable audit sessions
- Quick, actionable results
- Clear progress tracking
- Parallel team work possible

---

## File Structure Summary

```
accessibility-audit-framework/
├── Core Documentation
│   ├── README.md - System overview
│   ├── START_HERE.md - Quick start guide
│   ├── IMPORTANT_AUDIT_REQUIREMENTS.md - ⚠️ Critical requirements
│   ├── QUICK_START.md - Fast reference
│   ├── QUICK_INSTALL.md - Installation methods
│   ├── INSTALLATION.md - Detailed setup
│   ├── WORKFLOW_CHEATSHEET.md - One-page reference
│   ├── PHASED_AUDIT_STRATEGY.md - Breaking down large projects
│   ├── HOW_TO_START_AUDIT.md - Platform-specific prompts
│   ├── AUDIT_REPORT_TEMPLATE.md - Report template
│   ├── WHATS_NEW.md - Refactoring explanation
│   └── CHANGELOG.md - This file
│
├── Platform-Specific Guides (guides/)
│   ├── GUIDE_WEB.md - Web technologies
│   ├── GUIDE_ANDROID.md - Android
│   ├── GUIDE_IOS.md - iOS/tvOS
│   ├── GUIDE_REACT_NATIVE.md - React Native
│   ├── GUIDE_FLUTTER.md - Flutter
│   ├── GUIDE_ANDROID_TV.md - Android TV
│   ├── GUIDE_TVOS.md - tvOS
│   ├── GUIDE_WCAG_REFERENCE.md - WCAG principles
│   ├── COMMON_ISSUES.md - Cross-platform patterns
│   └── CODE_REFERENCES_AND_SCREENSHOTS.md - Requirements guide
│
└── Automation
    ├── setup-audit.sh - Automated setup script
    └── SIMPLE_SETUP_PROMPT.txt - Claude Code setup
```

**Total:** 22 documentation files + 10 guide files + 2 automation files

---

## Migration Guide

### If Using Old Structure

**Before:**
```
Follow ACCESSIBILITY_AUDIT_GUIDE.md
```

**Now:**
```
Follow guides/GUIDE_WEB.md (for web)
Or: guides/GUIDE_ANDROID.md (for Android)
Or: guides/GUIDE_IOS.md (for iOS)
```

### If Starting New

1. Read `START_HERE.md` (2 minutes)
2. Read `IMPORTANT_AUDIT_REQUIREMENTS.md` (3 minutes)
3. Choose platform guide from `guides/`
4. Use prompt from `WORKFLOW_CHEATSHEET.md`
5. Start auditing!

---

## Breaking Changes

**None** - All changes are additive. Old files still exist for backward compatibility.

---

## Future Enhancements

Potential additions:
- Video tutorials
- Example audit reports
- CI/CD integration guides
- Automated fix suggestions
- More platform guides (Unity, Unreal, etc.)

---

## Statistics

**Documentation Size:**
- Before: 1 file (29KB monolithic)
- After: 32 files (~120KB total, focused and organized)

**Time to Find Relevant Info:**
- Before: Scroll through entire 29KB file
- After: Open relevant 4-16KB guide directly

**Content Relevance:**
- Before: ~30% relevant to your platform
- After: 100% relevant to your platform

---

## Contributors

Framework designed for use with Claude Code (Anthropic).

---

## Support

For questions or issues:
- Review documentation in order: START_HERE.md → QUICK_START.md → Platform guide
- Check IMPORTANT_AUDIT_REQUIREMENTS.md for audit rules
- Refer to platform-specific guides for code patterns
