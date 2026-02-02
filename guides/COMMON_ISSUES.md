# Common Accessibility Issues Reference
## Cross-Platform Patterns and WCAG Mappings

---

## Quick WCAG SC Reference Table

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
| Collection items not grouped | 1.3.1 | 2.4.4, 2.1.1 | High |
| Repeated elements without context | 2.4.4 | 2.4.9, 4.1.2 | High |
| Buttons acting as tabs | 1.3.1 | 4.1.2, 2.4.6 | High |
| Role name in accessible label | 4.1.2 | 2.4.6 | Low-Medium |
| Text not scalable with settings | 1.4.4 | 1.4.12 | High |
| Incorrect language attribute | 3.1.1 | 3.1.2 | Medium |

---

## Common Patterns by Issue Type

### 1. Missing Alternative Text

**WCAG SC:**
- 1.1.1 Non-text Content (Level A)
- 4.1.2 Name, Role, Value (Level A)

**Platforms Affected:** All

**⚠️ IMPORTANT - Triage Before Reporting:**

**Decision Process:**
1. **Is the image clearly decorative?** (gradient, background, border, divider, spacer)
   - YES → **DON'T REPORT** - Skip this issue entirely
   - UNSURE → Report as **LOW priority**, note "fix only if not decorative"
   - NO → Continue to step 2

2. **Is this the ONLY content in an interactive element?** (button with only an icon)
   - YES → **CRITICAL priority** - MUST have description
   - NO → Report as standard priority

**Detection:**
- Web: `<img>` without `alt` attribute (check if decorative first)
- Android: `ImageView`/`Icon` without `contentDescription` (check if in collection or decorative)
- iOS: `UIImageView`/`Image` without `accessibilityLabel` (check context)
- React Native: `<Image>` without `accessibilityLabel` (check context)
- Flutter: `Image` without `Semantics` (check context)

**Clearly Decorative Examples (DON'T REPORT):**
- Gradient overlays
- Background images for aesthetic purposes
- Decorative borders, dividers, shadows
- Pattern backgrounds
- Spacer images

**MUST Report (CRITICAL):**
- Icon-only buttons without labels
- Interactive images with no text alternative
- Informational graphics without descriptions

**Fix Pattern:**
- Informational images: Add descriptive text alternative
- Decorative images: Mark as not important for accessibility
- Icon-only buttons: Add comprehensive label including action

**Impact:** Screen reader users cannot understand the purpose or content of images.

---

### 2. Unlabeled Interactive Elements

**WCAG SC:**
- 4.1.2 Name, Role, Value (Level A)
- 2.4.4 Link Purpose (In Context) (Level A)

**Platforms Affected:** All

**Detection:**
- Buttons with only icons
- Links with generic text ("click here")
- Custom interactive elements without semantic information

**Fix Pattern:** Add explicit accessible label describing the action

**Impact:** Screen reader users cannot determine what the button/link does.

---

### 3. Insufficient Color Contrast

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

**Impact:** Users with low vision or color blindness cannot read text or see UI elements.

---

### 4. Missing Form Labels

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

**Impact:** Screen reader users and users with cognitive disabilities cannot understand what information to enter.

---

### 5. Keyboard Accessibility Issues

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

**Impact:** Keyboard-only users cannot access all functionality or cannot navigate efficiently.

---

### 6. Touch Target Size Issues

**WCAG SC:**
- 2.5.8 Target Size (Minimum) (Level AA)

**Platforms Affected:** Mobile (Android, iOS, React Native, Flutter)

**Requirements:**
- Minimum 24×24 CSS pixels
- Recommended: 48×48 dp (Android), 44×44 pt (iOS)

**Detection:**
- Small buttons or tap areas
- Close-together interactive elements

**Fix Pattern:** Increase touch target size or add spacing

**Impact:** Users with motor impairments or large fingers have difficulty tapping small targets accurately.

---

### 7. Heading Structure Issues

**WCAG SC:**
- 1.3.1 Info and Relationships (Level A)
- 2.4.6 Headings and Labels (Level AA)

**Platforms Affected:** Web, Mobile

**Detection:**
- Skipped heading levels (h1 → h3)
- Text styled to look like heading but not marked as such
- Multiple h1 elements (web)

**Fix Pattern:** Use proper semantic heading hierarchy

**Impact:** Screen reader users cannot efficiently navigate page structure or understand content organization.

---

### 8. Dynamic Content Not Announced

**WCAG SC:**
- 4.1.3 Status Messages (Level AA)

**Platforms Affected:** All

**Detection:**
- Content updates without screen reader notification
- Loading states not announced
- Error messages appearing silently
- Success notifications not communicated

**Fix Pattern:**
- Web: ARIA live regions (`aria-live="polite"` or `aria-live="assertive"`)
- Android: `LiveRegion` semantics
- iOS: `UIAccessibility.post(notification:)` announcements
- React Native: `accessibilityLiveRegion`
- Flutter: `SemanticsProperties.liveRegion`

**Impact:** Screen reader users miss important updates, errors, or status changes.

---

### 9. Collection Items Not Properly Grouped

**WCAG SC:**
- 1.3.1 Info and Relationships (Level A)
- 2.4.4 Link Purpose (In Context) (Level A)
- 2.1.1 Keyboard (Level A) - Web

**Platforms Affected:** All

**⚠️ CRITICAL PATTERN:** Items in grids, rows, carousels, or lists should be treated as **a whole unit**. Users should NOT have to swipe/tab through multiple sub-elements to understand a single item.

**🚫 AVOIDING CONTRADICTORY GUIDANCE:**
When auditing, **prioritize collection items FIRST** before flagging individual sub-elements:

**Correct Approach:**
1. **Identify collection items** (RecyclerView items, FlatList items, grid cells, list items)
2. **For collection items:** Flag the parent for lacking merged accessibility, recommend marking ALL children as not accessible
3. **For standalone elements:** Flag missing accessibility labels

**Incorrect Approach (Avoid This):**
1. ❌ Flagging child images in collection items for missing contentDescription/alt text
2. ❌ Then separately flagging the collection item for needing merged accessibility
3. ❌ This creates contradictory guidance: "Add labels to children" + "Hide all children"

**Why This Matters:**
If children will be hidden from accessibility tree (which they should be in collections), individual accessibility labels on them are useless and waste development time.

**Detection:**
- Collection item with multiple interactive sub-elements (image, title, metadata, buttons)
- User must swipe/tab 5+ times through a single card
- Each sub-element announced separately instead of as a cohesive unit
- Common in: Movie/TV show grids, product listings, news feeds, social media posts

**Example Issue:**
```
User navigates through a TV show card:
Swipe 1: "Show poster image"
Swipe 2: "Breaking Bad"
Swipe 3: "Season 5"
Swipe 4: "Episode 14"
Swipe 5: "AMC logo"
Swipe 6: "Progress bar, 45 percent"
Swipe 7: "Play button"
```

**Fix Pattern - Merge All Information:**

**Web:**
```javascript
// ✅ Single tab stop with complete information
<a href="/show/123" aria-label="Breaking Bad, Ozymandias, Season 5, Episode 14, on AMC, 45 percent watched">
  <img src="poster.jpg" alt="" aria-hidden="true" />
  <div aria-hidden="true">
    <h3>Breaking Bad</h3>
    <p>S5 E14</p>
  </div>
</a>
```

**Android (Compose):**
```kotlin
// ✅ Single swipe announces everything
Card(
    onClick = { openShow() },
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "Breaking Bad, Ozymandias, Season 5, Episode 14, on AMC, 45 percent watched"
    }
) {
    // Visual content with contentDescription = null
}
```

**iOS (SwiftUI):**
```swift
// ✅ Single swipe announces everything
HStack {
    // Content
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Breaking Bad, Ozymandias, Season 5, Episode 14, on AMC, 45 percent watched")
```

**React Native:**
```javascript
// ✅ Single swipe announces everything
<TouchableOpacity
  accessible={true}
  accessibilityLabel="Breaking Bad, Ozymandias, Season 5, Episode 14, on AMC, 45 percent watched"
>
  <Image accessible={false} />
  <Text accessible={false}>Breaking Bad</Text>
</TouchableOpacity>
```

**Flutter:**
```dart
// ✅ Single swipe announces everything
Semantics(
  button: true,
  label: 'Breaking Bad, Ozymandias, Season 5, Episode 14, on AMC, 45 percent watched',
  child: GestureDetector(
    child: ExcludeSemantics(child: /* content */)
  ),
)
```

**Key Implementation Points:**
- **One interaction = one complete item description**
- Include ALL relevant information: title, subtitle/episode, metadata, channel, progress
- Mark child elements as not accessible/hidden
- Action buttons → use custom accessibility actions (preferred)
- If action buttons must be separate, include item context in their label

**Action Buttons Pattern:**
- **Preferred:** Custom accessibility actions (no additional swipes needed)
- **Alternative:** Separate focusable buttons with context ("Add Breaking Bad to favorites")

**Impact:** Screen reader users have to navigate through 5-10+ elements per item, making browsing collections extremely tedious and time-consuming. They may miss information or lose context about which item they're on.

**Testing:**
- Enable screen reader (TalkBack, VoiceOver, NVDA)
- Navigate through collection items
- Count number of swipes/tabs required per item
- Verify all information is communicated in single announcement
- Check that action buttons provide item context

---

### 10. Repeated Elements Without Context

**WCAG SC:**
- 2.4.4 Link Purpose (In Context) (Level A)
- 2.4.9 Link Purpose (Link Only) (Level AAA)
- 4.1.2 Name, Role, Value (Level A)

**Platforms Affected:** All

**⚠️ CRITICAL PATTERN:** When multiple interactive elements have identical labels/descriptions, screen reader users cannot differentiate between them.

**Common Scenarios:**
1. **"View all" buttons** in category rows (Comedy, Horror, Drama - all say "View all")
2. **"Delete" buttons** in email/message lists (20 emails = 20 identical "Delete" buttons)
3. **"Play" buttons** in content grids (hundreds of movies with same "Play" label)
4. **"Share" buttons** for multiple items
5. **"Edit" buttons** for multiple entries

**Detection:**
- Multiple buttons/links with same accessible label on same screen
- Action buttons in lists/grids without item context
- Generic labels like "Delete", "Edit", "Share" repeated multiple times
- "View all" or "See more" buttons in multiple category sections

**Example Problem:**

```
Page with movie categories:

Comedy section:
- "View all" button → Opens comedy movies

Horror section:
- "View all" button → Opens horror movies

Drama section:
- "View all" button → Opens drama movies

Screen reader announces: "View all, button" three times
→ User has NO IDEA which category each button opens
```

**Fix Pattern - Include Item Context:**

**Web:**
```javascript
// ❌ ISSUE
<button onClick={() => viewAll('comedy')}>View all</button>
<button onClick={() => viewAll('horror')}>View all</button>

// ✅ CORRECT
<button aria-label="View all comedy">View all</button>
<button aria-label="View all horror">View all</button>
```

**Android:**
```kotlin
// ❌ ISSUE
deleteButton.contentDescription = "Delete"  // For every email

// ✅ CORRECT
deleteButton.contentDescription = "Delete ${email.subject}"
// Examples:
// "Delete Meeting notes"
// "Delete Project update"
// "Delete Invoice from supplier"
```

**iOS:**
```swift
// ❌ ISSUE
button.accessibilityLabel = "Play"  // For every movie

// ✅ CORRECT
button.accessibilityLabel = "Play \(movie.title)"
// Examples:
// "Play Breaking Bad"
// "Play The Godfather"
// "Play Inception"
```

**React Native:**
```javascript
// ❌ ISSUE
<TouchableOpacity accessibilityLabel="Share">

// ✅ CORRECT
<TouchableOpacity accessibilityLabel={`Share ${item.title}`}>
```

**Flutter:**
```dart
// ❌ ISSUE
Semantics(label: 'Delete', child: IconButton(...))

// ✅ CORRECT
Semantics(label: 'Delete ${email.subject}', child: IconButton(...))
```

**Format Patterns:**
- Action buttons: `"[Action] [item]"` → "Delete Meeting notes", "Edit Contact info"
- View more/all: `"View all [category]"` → "View all comedy", "See more electronics"
- Play/Watch: `"Play [title]"` → "Play Breaking Bad", "Watch trailer for Inception"
- Share buttons: `"Share [item]"` → "Share recipe for chocolate cake"

**Real-World Example:**

**Email List (Before):**
```
Email 1: "Project update" | Delete button → "Delete"
Email 2: "Meeting notes" | Delete button → "Delete"
Email 3: "Invoice" | Delete button → "Delete"
...
Email 20: "Team lunch" | Delete button → "Delete"

→ User hears "Delete" 20 times, doesn't know what they're deleting!
```

**Email List (After):**
```
Email 1: "Project update" | Delete button → "Delete Project update"
Email 2: "Meeting notes" | Delete button → "Delete Meeting notes"
Email 3: "Invoice" | Delete button → "Delete Invoice"
...
Email 20: "Team lunch" | Delete button → "Delete Team lunch"

→ User knows exactly what each button will delete
```

**Testing:**
- [ ] Identify screens with repeated actions (lists, grids, categories)
- [ ] Navigate through repeated elements with screen reader
- [ ] Verify each label uniquely identifies its target
- [ ] Ensure context is meaningful without visual reference
- [ ] Check that labels aren't overly verbose

**Key Points:**
- **Identify item with:** title, name, subject, category, type
- **Keep it concise:** Include enough context but not excessive detail
- **Test navigation:** Use screen reader to verify labels are distinguishable
- **Dynamic content:** Build labels programmatically from item data

**Impact:** Screen reader users navigating lists/grids with dozens or hundreds of similar items cannot determine which item each action applies to, making the interface effectively unusable.

---

### 11. Buttons Acting as Tabs Without Tab Semantics

> 📖 **See detailed pattern guide:** [Buttons Acting as Tabs](patterns/BUTTONS_ACTING_AS_TABS.md)

**WCAG SC:**
- 1.3.1 Info and Relationships (Level A)
- 4.1.2 Name, Role, Value (Level A)
- 2.4.6 Headings and Labels (Level AA)

**Platforms Affected:** All

**⚠️ CRITICAL PATTERN:** Buttons that switch between different content views (fragments, panels, sections) without navigation should be semantically marked as **tabs**, not buttons.

**The Problem:**

When buttons functionally act like tabs (switching content) but use button semantics:
- Screen reader users don't understand the page structure
- No indication which view is currently active
- No position information ("tab 2 of 4")
- Users must guess relationship between buttons and content

**Common Scenarios:**
1. **Fragment/View Switchers:** Buttons that change displayed fragment ("Home", "Search", "Favorites")
2. **Content Filters:** Buttons like "All", "Active", "Completed" that swap content
3. **View Mode Toggles:** "List" / "Grid" buttons that change display mode
4. **Category Selectors:** "News", "Sports", "Entertainment" buttons showing different categories
5. **Time Period Selectors:** "Day", "Week", "Month", "Year" buttons changing date range

**Detection Criteria:**

Use tab semantics when buttons/controls:
- ✅ Switch between different content fragments
- ✅ Change a portion of the screen (not full navigation)
- ✅ Show different data sets or views
- ✅ Only one can be active at a time
- ✅ Content below/beside changes based on selection

Do NOT use tab semantics when:
- ❌ Navigate to completely different screens
- ❌ Perform actions (submit, delete, save)
- ❌ Open dialogs or modals
- ❌ Multiple can be active simultaneously

**Example Problem:**

```
Screen with 4 buttons at top:
- "Home" button (showing home content)
- "Search" button
- "Favorites" button
- "Profile" button

Screen reader announces:
→ "Home, button"
→ "Search, button"
→ "Favorites, button"
→ "Profile, button"

Issues:
→ No indication which is currently active
→ No indication these form a tab group
→ User doesn't understand page structure
```

**Required Fix:**

```
Should announce as:
→ "Home, tab 1 of 4, selected"
→ "Search, tab 2 of 4"
→ "Favorites, tab 3 of 4"
→ "Profile, tab 4 of 4"

Benefits:
→ Clear which tab is active ("selected")
→ Understand position in group ("2 of 4")
→ Recognize tab structure
→ Matches sighted user's mental model
```

**Platform-Specific Implementation:**

**Android (Compose):**
```kotlin
// ❌ ISSUE
Button(onClick = { switchToHome() }) { Text("Home") }

// ✅ CORRECT
Box(
    modifier = Modifier
        .clickable(role = Role.Tab, onClick = { switchToHome() })
        .semantics {
            stateDescription = if (isSelected) "Selected" else "Not selected"
        }
) { Text("Home") }

// ✅ BEST: Use TabRow
TabRow(selectedTabIndex = selectedIndex) {
    Tab(selected = isSelected, onClick = onClick, text = { Text("Home") })
}
```

**iOS (SwiftUI):**
```swift
// ❌ ISSUE
Button("Home") { switchToHome() }

// ✅ CORRECT
Button("Home") { switchToHome() }
    .accessibilityLabel("Home, tab 1 of 4")
    .accessibilityAddTraits(isSelected ? .isSelected : [])

// ✅ BEST: Use TabView
TabView(selection: $selectedTab) {
    HomeView().tabItem { Label("Home", systemImage: "house") }
}
```

**Web:**
```javascript
// ❌ ISSUE
<button onClick={switchToHome}>Home</button>

// ✅ CORRECT
<div role="tablist">
  <button role="tab" aria-selected={isSelected} aria-posinset="1" aria-setsize="4">
    Home
  </button>
</div>
<div role="tabpanel">
  {/* Content */}
</div>
```

**Audit Recommendations (Priority Order):**

1. **Best:** Refactor to native tab components (TabRow, TabView, ARIA tabs)
2. **Good:** Add tab semantics to existing buttons (Role.Tab, role="tab", selected state)
3. **Minimum:** Add selected state announcement and visual distinction

**Testing:**
- [ ] Identify buttons that switch content without full navigation
- [ ] Enable screen reader
- [ ] Verify tabs announce as "tab" not "button"
- [ ] Verify selected tab announces "selected"
- [ ] Verify position announced ("tab 2 of 4")
- [ ] Test visual distinction of selected state (contrast >= 3:1)

**Key Points:**
- **Structure matters:** Tab semantics communicate page structure
- **Selection state:** Users must know which tab is active
- **Position info:** "tab X of Y" helps navigation
- **Native preferred:** Use platform tab components when possible

**Impact:** Without proper tab semantics, screen reader users cannot understand the page structure, don't know which view is active, and struggle to navigate between content sections efficiently.

---

### 12. Role Names in Accessible Labels (Redundant Announcements)

> 📖 **See detailed pattern guide:** [Avoid Role in Label](patterns/AVOID_ROLE_IN_LABEL.md)

**WCAG SC:**
- 4.1.2 Name, Role, Value (Level A)
- 2.4.6 Headings and Labels (Level AA)

**Platforms Affected:** All

**⚠️ COMMON MISTAKE:** Including the role name in accessible labels creates redundant, annoying screen reader announcements.

**The Problem:**

Screen readers automatically announce element roles. Including the role in the label causes double announcements:

- ❌ "Close Button" → **"Close Button, button"**
- ❌ "Home Link" → **"Home Link, link"**
- ❌ "Agree Checkbox" → **"Agree Checkbox, checkbox"**
- ❌ "Search Input" → **"Search Input, text field"**

**The Solution:**

Remove role names from labels. Screen reader announces role automatically:

- ✅ "Close" → **"Close, button"**
- ✅ "Home" → **"Home, link"**
- ✅ "Agree" → **"Agree, checkbox"**
- ✅ "Search" → **"Search, text field"**

**Common Offenders:**

1. **Button labels:** "Submit Button", "Cancel Button", "Menu Button", "Close Button"
2. **Link labels:** "Read More Link", "Home Link", "Privacy Policy Link"
3. **Form controls:** "Email Text Field", "Password Input", "Agree Checkbox"
4. **Tab labels:** "Home Tab", "Settings Tab", "Profile Tab"
5. **Other controls:** "File Menu", "Enable Toggle", "Volume Slider"

**Detection Pattern:**

Search codebase for labels containing these words:
- `.*Button` (button, Button, btn)
- `.*Link` (link, Link)
- `.*Tab` (tab, Tab)
- `.*Checkbox` (checkbox, Checkbox, check box)
- `.*Input` (input, Input, textfield, text field)
- `.*Menu` (menu, Menu)

**Example Problem:**

```
Login form with screen reader:
→ "Email Text Field, text field"
→ "Password Text Field, text field"
→ "Remember Me Checkbox, checkbox"
→ "Login Button, button"
→ "Forgot Password Link, link"

Every element announces the role TWICE!
```

**Example Fixed:**

```
Login form with screen reader:
→ "Email, text field"
→ "Password, text field"
→ "Remember Me, checkbox"
→ "Login, button"
→ "Forgot Password, link"

Clean, concise, professional.
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

**When Role Words ARE Acceptable:**

Only when the word describes what the element **does** or **affects**, not what it **is**:

- ✅ "Open Menu" (button) - "Menu" is what opens, not the role
- ✅ "Choose File" (button) - "File" is what you choose
- ✅ "Show Dialog" (button) - "Dialog" is what appears
- ✅ "Select Date" (button) - "Date" is what you select
- ❌ "Close Button" - "Button" describes what it **is**

**Testing:**
- [ ] Enable screen reader (TalkBack, VoiceOver, NVDA)
- [ ] Navigate through interactive elements
- [ ] Listen for redundant announcements (role said twice)
- [ ] Search codebase for common patterns
- [ ] Document all instances

**Fix Priority:**
- **Medium:** If widespread (affects many elements)
- **Low:** If isolated (only a few elements)

**Key Points:**
- Screen readers announce roles automatically
- Labels should describe purpose/action, not type
- Focus on "what it does", not "what it is"
- Test with actual screen reader to verify

**Impact:**
- **Annoyance:** Every element announces role twice
- **Cognitive load:** Extra words to process
- **Unprofessional:** Indicates poor accessibility implementation
- **Slower navigation:** Takes longer to hear each element

**After fix:**
- Clean, concise announcements
- Professional implementation
- Faster navigation
- Better user experience

---

### 13. Text Not Scalable with System Font Settings

**WCAG SC:**
- **Primary:** 1.4.4 Resize Text (Level AA)
- **Secondary:** 1.4.12 Text Spacing (Level AA)

**Platforms Affected:** All

**Description:**
Text in the application uses fixed units that do not scale with the user's system font size preferences. This prevents users with visual impairments from reading content comfortably.

**Critical Issue:**
- **Android:** Using `dp` instead of `sp` for text sizes
- **iOS:** Using fixed font sizes instead of Dynamic Type
- **Web:** Using `px` instead of `rem`/`em`
- **All platforms:** Not respecting user font size preferences

**Common Mistakes:**

Android:
```kotlin
❌ Text(text = "Hello", fontSize = 16.dp)  // WRONG: dp instead of sp
✅ Text(text = "Hello", fontSize = 16.sp)  // CORRECT: sp scales with settings
✅ Text(text = "Hello", style = MaterialTheme.typography.bodyLarge)  // BEST
```

iOS:
```swift
❌ Text("Hello").font(.system(size: 16))  // WRONG: Fixed size
✅ Text("Hello").font(.body)  // CORRECT: Dynamic Type
✅ label.adjustsFontForContentSizeCategory = true  // CRITICAL in UIKit
```

Web:
```css
❌ font-size: 16px;  /* WRONG: Fixed pixels */
✅ font-size: 1rem;  /* CORRECT: Scalable relative units */
✅ font-size: 1em;   /* CORRECT: Relative to parent */
```

**Detection Patterns:**

Android - Search for:
```
fontSize.*\.dp
textSize="[0-9]+dp"
```

iOS - Search for:
```swift
UIFont.systemFont(ofSize:
.font(.system(size:
```
Then verify: UIKit has `adjustsFontForContentSizeCategory = true`, SwiftUI uses text styles

Web - Search for:
```css
font-size:.*px;
```

**Fix Pattern:**
- Android: Change all `fontSize = X.dp` to `fontSize = X.sp` or use Material Typography
- iOS: Use Dynamic Type styles (`.body`, `.title`, etc.) and set `adjustsFontForContentSizeCategory = true`
- Web: Use `rem` or `em` units instead of `px`
- Allow text to wrap (multiline) instead of truncating
- Use flexible container heights that adapt to content

**Testing:**
1. **Android:** Settings → Display → Font size → Largest
2. **iOS:** Settings → Accessibility → Display & Text Size → Larger Text → Maximum
3. **Web:** Browser zoom to 200% (Cmd/Ctrl + +)
4. Verify:
   - [ ] All text scales proportionally
   - [ ] No text is cut off or overlaps
   - [ ] Layouts adapt to larger text
   - [ ] All functionality remains usable
   - [ ] No horizontal scrolling required

**Impact:**
- **15-30% of users** adjust system font sizes
- Users with low vision **cannot read the app** if text doesn't scale
- Older users who need larger text are excluded
- Violates WCAG Level AA conformance

**Severity:** High

**WCAG References:**
- 1.4.4 Resize Text (Level AA) - Text can be resized up to 200% without loss of content
- 1.4.12 Text Spacing (Level AA) - No loss of content when text spacing is adjusted

**Related Issues:**
- Fixed container heights that clip text
- Single-line text that truncates instead of wrapping
- Layouts that break with larger text

**See full guide:** `guides/patterns/FONT_SCALING_SUPPORT.md`

---

## Platform-Specific Detection Patterns

### Web
- **Missing alt text:** `<img src="..." />` without `alt` attribute
- **Unlabeled button:** `<button><i class="icon"></i></button>` without text or `aria-label`
- **Form without label:** `<input>` without associated `<label>` or `aria-label`
- **Keyboard trap:** Modal/dropdown that captures focus without escape method
- **No ARIA for custom widgets:** Custom dropdown/tab/accordion without proper ARIA

### Android
- **Missing contentDescription:** `ImageButton`, `ImageView`, `Icon` without `contentDescription`
- **Small touch target:** Button with `layout_width`/`height` < 48dp
- **EditText without label:** `EditText` with only `hint` attribute
- **Clickable without accessibility:** Custom view with `setOnClickListener` but no `contentDescription` or `isFocusable`
- **No heading semantics:** Section title without `accessibilityHeading=true`

### iOS
- **Missing accessibilityLabel:** `UIButton`, `UIImageView` without label
- **Missing accessibilityTraits:** Custom interactive view without `.button`, `.header`, etc.
- **No grouping:** Related elements not grouped with `accessibilityElement(children:)`
- **Placeholder as label:** `UITextField` with only `placeholder`, no `accessibilityLabel`
- **Missing custom actions:** Swipe-to-delete without `accessibilityCustomActions`

### React Native
- **Missing accessibilityLabel:** `<Image>`, `<TouchableOpacity>` without label
- **Missing accessibilityRole:** Custom interactive component without role
- **No accessibilityState:** Toggle/checkbox without `accessibilityState`
- **Small touch target:** Touchable area < 44pt
- **No accessibilityHint:** Complex interaction without hint

### Flutter
- **Missing Semantics:** `Image`, `GestureDetector` without `Semantics` widget
- **Decorative not excluded:** Decorative elements not wrapped in `ExcludeSemantics`
- **No semantic label:** Interactive widget without `label` property
- **No merge semantics:** Related elements not wrapped in `MergeSemantics`

---

## Testing Tools by Platform

### Web
- **Automated:** axe DevTools, WAVE, Lighthouse, Pa11y
- **Screen Readers:** NVDA (Windows), JAWS (Windows), VoiceOver (Mac), ChromeVox (Chrome)
- **Contrast:** WebAIM Contrast Checker, TPGI Color Contrast Analyzer
- **Keyboard:** Manual keyboard-only testing

### Android
- **Automated:** Accessibility Scanner app
- **Screen Reader:** TalkBack
- **Switch:** Switch Access
- **Testing Framework:** Espresso with AccessibilityChecks
- **Inspection:** Layout Inspector in Android Studio

### iOS
- **Automated:** Xcode Accessibility Inspector
- **Screen Reader:** VoiceOver (iOS/tvOS)
- **Switch:** Switch Control
- **Voice:** Voice Control
- **Inspection:** Accessibility Inspector in Xcode

### React Native
- Use platform-specific tools (TalkBack for Android, VoiceOver for iOS)
- Test on both platforms as behavior may differ

### Flutter
- Use platform-specific tools (TalkBack for Android, VoiceOver for iOS)
- Flutter DevTools for widget inspection

---

## Common Anti-Patterns to Avoid

### All Platforms
❌ Using placeholder text as the only label
❌ Icon-only buttons without accessible labels
❌ Low contrast text (gray on white)
❌ Relying only on color to convey information
❌ Hiding important content from screen readers
❌ Using generic link text like "click here" or "read more"
❌ Not announcing dynamic content updates
❌ Making non-focusable elements clickable
❌ Breaking semantic structure (skipping heading levels)
❌ Collection items requiring multiple swipes/tabs through sub-elements
❌ Not merging related information in list/grid items
❌ Repeated action buttons without item context ("Delete" x 20 times)
❌ Multiple "View all" buttons without category names
❌ **Text not scalable with system font settings** (dp instead of sp, fixed px, etc.)

### Web Specific
❌ `<div>` or `<span>` as buttons instead of `<button>`
❌ Missing form labels (using placeholder only)
❌ Empty `alt=""` on meaningful images
❌ Missing `alt` attribute entirely
❌ Keyboard traps in modals or dropdowns
❌ Custom widgets without ARIA roles
❌ Auto-playing media without controls

### Mobile Specific (Android/iOS)
❌ Touch targets smaller than 44-48pt/dp
❌ `contentDescription`/`accessibilityLabel` on decorative images
❌ Using `hint`/`placeholder` as the only form label
❌ Gesture-only interactions without alternatives
❌ Not marking section titles as headings
❌ Missing state information (selected, checked, expanded)
❌ **Android:** Using `dp` for text sizes instead of `sp`
❌ **iOS:** Not supporting Dynamic Type or using fixed font sizes

---

**For platform-specific code examples, see:**
- GUIDE_WEB.md
- GUIDE_ANDROID.md
- GUIDE_IOS.md
- GUIDE_REACT_NATIVE.md
- GUIDE_FLUTTER.md
