# Android Accessibility Audit Guide
## XML Layouts, Jetpack Compose, Mobile & TV

---

## Overview

This guide covers accessibility auditing for Android applications using:
- XML layouts
- Jetpack Compose
- Android Views and ViewGroups
- Material Design components
- Android TV interfaces

**Target:** WCAG 2.2 Level AA compliance adapted for mobile

---

## ⚠️ CRITICAL AUDIT REPORT REQUIREMENTS

**Issue Ordering in Reports:**
1. **ALWAYS order by severity**: Critical → High → Medium → Low
2. **NEVER order by location** or discovery order
3. Within each severity, order by WCAG SC or logical grouping

**Report Content Policy:**
- **ONLY report issues and problems**
- **DO NOT include positive findings** or mention things that work correctly
- **DO NOT say "good practice observed"** or similar
- If something is implemented correctly, omit it from the report entirely
- Focus exclusively on what needs to be fixed

---

## Technology Focus

### Core Android Technologies
- **XML Layouts:** Traditional View-based UI
- **Jetpack Compose:** Modern declarative UI
- **Material Components:** Material Design library
- **TalkBack:** Android screen reader
- **Accessibility APIs:** ContentDescription, semantics, focus management

---

## Key Code Patterns to Check

### 1. Content Descriptions - IMPORTANT: Check Collection Context First

> 📖 **See pattern guide for decorative images:** [Decorative Image Decision Tree](patterns/DECORATIVE_IMAGE_DECISION_TREE.md)

**⚠️ CRITICAL:** Before flagging missing contentDescription, determine if the element is part of a collection item (RecyclerView item, LazyColumn card, grid cell).

**Decision Tree:**
1. **Is this element part of a collection item (card/tile in a list/grid)?**
   - YES → Skip to Section 10 (Collection Items) - merge at parent level, mark children as not important
   - NO → Continue to step 2

2. **Is this image clearly decorative?** (gradient, background, border, divider, shadow)
   - YES → Skip reporting, don't include in audit
   - UNSURE → Create LOW priority issue, note "fix only if not decorative"
   - NO (conveys information) → Continue to step 3
   - **See pattern guide above for complete triage process and platform-specific examples**

3. **Is this the ONLY content in a button/clickable element?**
   - YES → CRITICAL issue, MUST have contentDescription
   - NO → Apply standard contentDescription rules below

4. **Is this element standalone (not in a collection)?**
   - YES → Require contentDescription as shown below

**Issue:** Missing contentDescription on **standalone** interactive elements

```xml
<!-- ❌ ISSUE: Missing contentDescription on standalone ImageButton -->
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!-- ✅ CORRECT: Descriptive contentDescription (standalone button) -->
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:contentDescription="@string/play_button"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!-- ✅ CORRECT: Decorative image -->
<ImageView
    android:src="@drawable/decorative_border"
    android:importantForAccessibility="no"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**❌ DO NOT flag for missing contentDescription:**
- Images/icons/buttons inside RecyclerView items, LazyColumn cards, or grid cells
- Sub-views of collection items that will be merged (see Section 10)
- Elements that are part of a larger grouped component

**✅ DO flag for missing contentDescription:**
- Images that are the ONLY content in buttons (CRITICAL priority)
- Standalone interactive icons not part of collections
- Top-level navigation elements
- Floating action buttons
- Toolbar icons
- Dialog buttons
- Images conveying information (logos with brand identity, status icons, etc.)

**🎨 Clearly Decorative - DON'T Report:**
- Gradient overlays (e.g., `@drawable/gradient_landscape_down_blue`)
- Background images that are purely aesthetic
- Decorative borders or dividers
- Shadow/elevation images
- Pattern backgrounds
- Decorative spacer images

**❓ Unsure if Decorative - LOW Priority:**
- Images that might convey branding but information is elsewhere
- Corner badges/logos when channel info is in text
- Decorative indicators when status is conveyed through text
- **Recommendation text:** "Verify if this image is decorative. If so, mark as `importantForAccessibility='no'`. If it conveys information, add appropriate contentDescription."

**WCAG SC:** 1.1.1 Non-text Content (Level A), 4.1.2 Name, Role, Value (Level A)

**String Resources:**
```xml
<!-- res/values/strings.xml -->
<string name="play_button">Play</string>
<string name="pause_button">Pause</string>
<string name="close_button">Close</string>
```

---

### 2. Content Descriptions (Jetpack Compose)

**Issue:** Missing semantics in Compose

```kotlin
// ❌ ISSUE: Missing content description
Icon(
    painter = painterResource(R.drawable.ic_play),
    contentDescription = null
)

// ✅ CORRECT: Descriptive content description
Icon(
    painter = painterResource(R.drawable.ic_play),
    contentDescription = stringResource(R.string.play_button)
)

// ✅ CORRECT: Decorative icon
Icon(
    painter = painterResource(R.drawable.decorative),
    contentDescription = null,
    modifier = Modifier.semantics {
        contentDescription = "" // Explicitly marks as decorative
    }
)

// Or use clearAndSetSemantics to completely hide from TalkBack
Icon(
    painter = painterResource(R.drawable.decorative),
    contentDescription = null,
    modifier = Modifier.clearAndSetSemantics {}
)
```

**WCAG SC:** 1.1.1 Non-text Content (Level A), 4.1.2 Name, Role, Value (Level A)

---

### 3. Touch Target Sizes

**Issue:** Touch targets smaller than minimum size

```xml
<!-- ❌ ISSUE: Touch target too small (32dp) -->
<Button
    android:layout_width="32dp"
    android:layout_height="32dp"
    android:text="X" />

<!-- ✅ CORRECT: Minimum 48dp touch target -->
<Button
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:text="X" />

<!-- ✅ CORRECT: Use minWidth/minHeight for smaller visual with proper touch area -->
<Button
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:minWidth="48dp"
    android:minHeight="48dp"
    android:text="X" />
```

**Compose:**
```kotlin
// ❌ ISSUE: Small touch target
IconButton(
    onClick = { /*...*/  },
    modifier = Modifier.size(32.dp)
) {
    Icon(Icons.Default.Close, "Close")
}

// ✅ CORRECT: Minimum 48dp
IconButton(
    onClick = { /*...*/ },
    modifier = Modifier.size(48.dp)
) {
    Icon(Icons.Default.Close, "Close")
}

// ✅ CORRECT: Visual size different from touch target
Box(
    modifier = Modifier
        .size(48.dp) // Touch target
        .clickable { /*...*/ }
        .semantics { contentDescription = "Close" },
    contentAlignment = Alignment.Center
) {
    Icon(
        Icons.Default.Close,
        contentDescription = null,
        modifier = Modifier.size(24.dp) // Visual size
    )
}
```

**WCAG SC:** 2.5.8 Target Size (Minimum) (Level AA)

**Requirements:** Minimum 48dp × 48dp

---

### 4. Text Sizes Must Use sp (Scalable Pixels)

**⚠️ CRITICAL:** All text sizes MUST use `sp` (scalable pixels), NEVER `dp` (density-independent pixels).

**Issue:** Text using `dp` instead of `sp` does not scale with user's system font size settings.

**Impact:**
- 15-30% of users adjust system font sizes
- Users with low vision cannot read the app
- Violates WCAG 1.4.4 Resize Text (Level AA)
- Creates significant accessibility barrier

**XML:**
```xml
<!-- ❌ CRITICAL ISSUE: Using dp for text size -->
<TextView
    android:text="Welcome"
    android:textSize="20dp" />  <!-- WRONG: dp does not scale -->

<Button
    android:text="Submit"
    android:textSize="16dp" />  <!-- WRONG: dp does not scale -->

<!-- ✅ CORRECT: Using sp for text size -->
<TextView
    android:text="Welcome"
    android:textSize="20sp" />  <!-- CORRECT: sp scales with system settings -->

<Button
    android:text="Submit"
    android:textSize="16sp" />  <!-- CORRECT: sp scales -->

<!-- ✅ BEST: Use text appearances (automatically use sp) -->
<TextView
    android:text="Welcome"
    android:textAppearance="?attr/textAppearanceHeadlineMedium" />

<TextView
    android:text="Description"
    android:textAppearance="?attr/textAppearanceBodyMedium" />
```

**Jetpack Compose:**
```kotlin
// ❌ CRITICAL ISSUE: Using dp for text
Text(
    text = "Welcome",
    fontSize = 20.dp  // WRONG: Will NOT scale with user settings
)

Text(
    text = "Description",
    fontSize = 14.dp  // WRONG
)

// ✅ CORRECT: Using sp for text
Text(
    text = "Welcome",
    fontSize = 20.sp  // CORRECT: Scales with system settings
)

Text(
    text = "Description",
    fontSize = 14.sp  // CORRECT
)

// ✅ BEST: Use Material Theme typography (automatically uses sp)
Text(
    text = "Welcome",
    style = MaterialTheme.typography.headlineMedium  // BEST practice
)

Text(
    text = "Description",
    style = MaterialTheme.typography.bodyMedium  // BEST practice
)
```

**Detection Pattern:**

Search codebase for:
```
fontSize.*\.dp
textSize="[0-9]+dp"
```

**Fix:**
1. Change all `fontSize = X.dp` to `fontSize = X.sp`
2. Change all `android:textSize="Xdp"` to `android:textSize="Xsp"`
3. Better: Use Material Theme typography styles
4. Ensure text can wrap (use `maxLines` appropriately or no limit)
5. Use flexible container heights (`heightIn(min = ...)` instead of fixed `height()`)

**Testing:**
1. Go to Settings → Display → Font size → Set to "Largest"
2. Open the app
3. Verify:
   - [ ] All text increases proportionally
   - [ ] No text is cut off or overlaps
   - [ ] Layouts adapt to larger text
   - [ ] Buttons remain tappable
   - [ ] Scrollable content still scrolls

**WCAG SC:**
- **Primary:** 1.4.4 Resize Text (Level AA)
- **Secondary:** 1.4.12 Text Spacing (Level AA)

**Severity:** High (affects 15-30% of users)

**See full guide:** `guides/patterns/FONT_SCALING_SUPPORT.md`

---

### 5. Form Input Labels (XML)

**Issue:** EditText with only hint, no persistent label

```xml
<!-- ❌ ISSUE: Placeholder used as label -->
<EditText
    android:id="@+id/emailInput"
    android:hint="Email address"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- ✅ CORRECT: TextInputLayout provides persistent label -->
<com.google.android.material.textfield.TextInputLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:hint="Email address">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/emailInput"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="textEmailAddress" />

</com.google.android.material.textfield.TextInputLayout>

<!-- ✅ CORRECT: Manual label with labelFor -->
<TextView
    android:id="@+id/emailLabel"
    android:text="Email address"
    android:labelFor="@id/emailInput"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<EditText
    android:id="@+id/emailInput"
    android:hint="example@email.com"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**Compose:**
```kotlin
// ❌ ISSUE: No label
OutlinedTextField(
    value = email,
    onValueChange = { email = it }
)

// ✅ CORRECT: With label
OutlinedTextField(
    value = email,
    onValueChange = { email = it },
    label = { Text("Email address") }
)

// ✅ CORRECT: Alternative with explicit semantics
OutlinedTextField(
    value = email,
    onValueChange = { email = it },
    modifier = Modifier.semantics {
        contentDescription = "Email address"
    }
)
```

**WCAG SC:** 3.3.2 Labels or Instructions (Level A), 1.3.1 Info and Relationships (Level A)

---

### 6. Clickable Custom Views

**Issue:** Custom view with click listener but no accessibility setup

```kotlin
// ❌ ISSUE: Custom view not marked as clickable/focusable
customView.setOnClickListener { handleClick() }

// ✅ CORRECT: Proper accessibility setup
customView.apply {
    isClickable = true
    isFocusable = true
    contentDescription = "Custom action button"
    setOnClickListener { handleClick() }
}

// ✅ CORRECT: With ViewCompat for better compatibility
ViewCompat.setAccessibilityDelegate(customView, object : AccessibilityDelegateCompat() {
    override fun onInitializeAccessibilityNodeInfo(
        host: View,
        info: AccessibilityNodeInfoCompat
    ) {
        super.onInitializeAccessibilityNodeInfo(host, info)
        info.addAction(AccessibilityNodeInfoCompat.AccessibilityActionCompat.ACTION_CLICK)
        info.isClickable = true
    }
})
```

**Compose:**
```kotlin
// ❌ ISSUE: Clickable without semantics
Box(modifier = Modifier.clickable { handleClick() }) {
    Text("Custom button")
}

// ✅ CORRECT: With proper role
Box(
    modifier = Modifier
        .clickable { handleClick() }
        .semantics {
            role = Role.Button
            contentDescription = "Custom action button"
        }
) {
    Text("Custom button")
}
```

**WCAG SC:** 4.1.2 Name, Role, Value (Level A)

---

### 7. Headings and Structure (Compose)

**Issue:** Section titles not marked as headings

```kotlin
// ❌ ISSUE: No heading structure
Text("Section Title")

// ✅ CORRECT: Marked as heading
Text(
    "Section Title",
    style = MaterialTheme.typography.headlineMedium,
    modifier = Modifier.semantics {
        heading()
    }
)

// ✅ CORRECT: Compose Material 3
Text(
    "Section Title",
    style = MaterialTheme.typography.titleLarge,
    modifier = Modifier.semantics { heading() }
)
```

**XML:**
```xml
<!-- ✅ CORRECT: Mark TextView as heading -->
<TextView
    android:id="@+id/sectionTitle"
    android:text="Section Title"
    android:textAppearance="@style/TextAppearance.MaterialComponents.Headline5"
    android:accessibilityHeading="true"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

**Kotlin (ViewBinding):**
```kotlin
// For API 28+
binding.sectionTitle.isAccessibilityHeading = true

// For backward compatibility
ViewCompat.setAccessibilityHeading(binding.sectionTitle, true)
```

**WCAG SC:** 1.3.1 Info and Relationships (Level A), 2.4.6 Headings and Labels (Level AA)

---

### 8. Live Regions (Compose)

**Issue:** Dynamic content without announcement

```kotlin
// ❌ ISSUE: Dynamic content without announcement
Text(text = statusMessage)

// ✅ CORRECT: Announces changes (polite)
Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite
    }
)

// ✅ CORRECT: Urgent announcements (assertive)
Text(
    text = errorMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Assertive
    }
)
```

**XML:**
```xml
<!-- ✅ CORRECT: Live region in XML -->
<TextView
    android:id="@+id/statusText"
    android:accessibilityLiveRegion="polite"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

**Programmatic Announcements:**
```kotlin
// ✅ One-time announcement
view.announceForAccessibility("Upload complete")

// Or with ViewCompat
ViewCompat.announceForAccessibility(view, "Upload complete")

// Compose
val context = LocalContext.current
LaunchedEffect(uploadComplete) {
    if (uploadComplete) {
        val accessibilityManager = context.getSystemService(Context.ACCESSIBILITY_SERVICE)
            as AccessibilityManager
        if (accessibilityManager.isEnabled) {
            val event = AccessibilityEvent.obtain().apply {
                eventType = AccessibilityEvent.TYPE_ANNOUNCEMENT
                className = javaClass.name
                packageName = context.packageName
                text.add("Upload complete")
            }
            accessibilityManager.sendAccessibilityEvent(event)
        }
    }
}
```

**WCAG SC:** 4.1.3 Status Messages (Level AA)

---

### 9. State Descriptions (Compose)

**Issue:** Toggle or checkbox state not announced

```kotlin
// ❌ ISSUE: State not communicated
Switch(
    checked = isEnabled,
    onCheckedChange = { isEnabled = it }
)

// ✅ CORRECT: State automatically handled by Switch
Switch(
    checked = isEnabled,
    onCheckedChange = { isEnabled = it },
    modifier = Modifier.semantics {
        contentDescription = "Enable notifications"
    }
)

// ✅ CORRECT: Custom state description
var isSelected by remember { mutableStateOf(false) }
Box(
    modifier = Modifier
        .toggleable(
            value = isSelected,
            onValueChange = { isSelected = it }
        )
        .semantics {
            stateDescription = if (isSelected) "Selected" else "Not selected"
        }
) {
    Text(if (isSelected) "✓ Favorite" else "☆ Favorite")
}
```

**WCAG SC:** 4.1.2 Name, Role, Value (Level A)

---

### 10. Grouping Related Content (Compose)

**Issue:** Related elements announced separately

```kotlin
// ❌ ISSUE: Icon and text announced separately
Row {
    Icon(Icons.Default.Star, contentDescription = "Rating")
    Text("4.5 stars")
}

// ✅ CORRECT: Merged semantics
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("4.5 stars")
}

// ✅ CORRECT: Custom merged description
Row(
    modifier = Modifier.semantics {
        contentDescription = "Rating: 4.5 stars"
    }
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("4.5 stars")
}
```

**WCAG SC:** 1.3.1 Info and Relationships (Level A)

---

### 11. Collection Items (RecyclerView, LazyColumn, LazyRow)

> 📖 **See detailed pattern guide:** [Collection Items Pattern](patterns/COLLECTION_ITEMS_PATTERN.md)
>
> This section provides Android-specific implementation. See the pattern guide for:
> - Complete explanation and examples
> - Cross-platform implementations
> - Testing strategies
> - Impact analysis

**Issue:** Collection items with multiple sub-views require multiple swipes to navigate

**⚠️ CRITICAL Requirements:**
1. Items in grids, rows, or lists should be treated as **a whole unit**
2. Users should NOT have to swipe multiple times through sub-views
3. **Parent container MUST be clickable/tappable** - Use `Card(onClick = ...)` or set `isClickable = true` + `isFocusable = true`

**🚫 Avoid Contradictory Guidance:** DO NOT flag child views for missing descriptions if recommending parent-level merging.

#### Android Implementation

**Jetpack Compose:**
```kotlin
// ✅ CORRECT: Merged semantics for TV show card
Card(
    onClick = { openShow() },
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = buildString {
            append(show.title)
            append(", ${show.episodeName}")
            append(", Season ${show.season}, Episode ${show.episode}")
            append(", on ${channel.name}")
            val percentWatched = (show.watchProgress * 100).toInt()
            append(", $percentWatched percent watched")
        }
    }
) {
    Row {
        Image(painter = rememberAsyncImagePainter(show.posterUrl), contentDescription = null)
        Column {
            Text(show.title)
            Text("Season ${show.season}")
            Text("Episode ${show.episode}")
            Image(painter = painterResource(channel.logo), contentDescription = null)
            LinearProgressIndicator(progress = show.watchProgress)
        }
    }
}
```

**XML (RecyclerView ViewHolder):**
```kotlin
class ShowViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    fun bind(show: Show) {
        itemView.apply {
            isClickable = true
            isFocusable = true
            contentDescription = "${show.title}, ${show.episodeName}, " +
                "Season ${show.season}, Episode ${show.episode}, " +
                "on ${show.channelName}, ${show.watchedPercent} percent watched"

            // Mark all child views as not important for accessibility
            posterImageView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            titleTextView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            seasonTextView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            episodeTextView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            channelLogoView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            progressBar.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }
    }
}
```

**Custom Accessibility Actions (Compose):**
```kotlin
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = getShowDescription(show)
        customActions = listOf(
            CustomAccessibilityAction("Add to favorites") {
                addToFavorites(show)
                true
            }
        )
    }
) { /* content */ }
```

**WCAG SC:** 1.3.1 Info and Relationships (Level A), 2.4.4 Link Purpose (In Context) (Level A)

---

### 12. Bottom Navigation Bar Accessibility

> 📖 **See detailed pattern guide:** [Navigation Bar Accessibility](patterns/NAVIGATION_BAR_ACCESSIBILITY.md)
>
> This section provides Android-specific implementation. See the pattern guide for:
> - Complete requirements checklist
> - Common issues and solutions
> - Cross-platform implementations
> - Testing strategies

**Issue:** Navigation bars with incomplete or missing accessibility features

**⚠️ CRITICAL:** Bottom navigation bars must meet ALL 4 requirements: labels, selected state, position/count, visual contrast.

#### Android Implementation

**XML - BottomNavigationView:**
```xml
<!-- Menu with proper titles (used as accessible labels) -->
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/nav_home"
        android:icon="@drawable/ic_home"
        android:title="@string/nav_home" />
    <item
        android:id="@+id/nav_search"
        android:icon="@drawable/ic_search"
        android:title="@string/nav_search" />
</menu>

<!-- Layout -->
<com.google.android.material.bottomnavigation.BottomNavigationView
    android:id="@+id/bottom_navigation"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:itemIconTint="@color/bottom_nav_color_selector"
    app:itemTextColor="@color/bottom_nav_color_selector"
    app:menu="@menu/bottom_nav_menu" />
```

**Jetpack Compose - NavigationBar:**
```kotlin
@Composable
fun AppBottomNavigation(selectedIndex: Int, onItemSelected: (Int) -> Unit) {
    NavigationBar {
        navItems.forEachIndexed { index, item ->
            NavigationBarItem(
                selected = selectedIndex == index,
                onClick = { onItemSelected(index) },
                icon = { Icon(item.icon, contentDescription = null) },
                label = { Text(item.label) } // REQUIRED
            )
        }
    }
}
```

**Custom Implementation (Compose):**
```kotlin
@Composable
fun CustomNavItem(label: String, icon: ImageVector, selected: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clickable(onClick = onClick, role = Role.Tab)
            .semantics(mergeDescendants = true) {
                contentDescription = label
                stateDescription = if (selected) "Selected" else "Not selected"
            }
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(icon, contentDescription = null, tint = if (selected) SelectedColor else UnselectedColor)
            Text(label, color = if (selected) SelectedColor else UnselectedColor)
        }
    }
}
```

**WCAG SC:** 1.3.1, 2.4.6, 4.1.2, 1.4.11 (see pattern guide for details)

---

### 13. Context for Repeated Elements

> 📖 **See detailed pattern guide:** [Repeated Elements Context](patterns/REPEATED_ELEMENTS_CONTEXT.md)
>
> This section provides Android-specific implementation. See the pattern guide for:
> - Complete explanation with examples
> - Common scenarios (View all, Delete, Play, Share, Edit buttons)
> - Cross-platform implementations
> - Best practices and format patterns

**Issue:** Multiple elements with identical accessible descriptions, making them indistinguishable

**⚠️ CRITICAL:** Always include context to make repeated actions unique. Pattern: `"[Action] [item identifier]"`

#### Android Implementation

**XML:**
```xml
<!-- ✅ CORRECT: Category "View all" buttons with context -->
<Button
    android:text="View all"
    android:contentDescription="View all comedy" />
<Button
    android:text="View all"
    android:contentDescription="View all horror" />
```

**RecyclerView ViewHolder:**
```kotlin
// ✅ CORRECT: Email list with contextual labels
class EmailViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    fun bind(email: Email) {
        deleteButton.contentDescription = "Delete ${email.subject}"
        replyButton.contentDescription = "Reply to ${email.subject}"
    }
}

// Category "View all" buttons
fun bindCategoryHeader(category: Category, viewAllButton: Button) {
    viewAllButton.contentDescription = "View all ${category.name}"
}
```

**Jetpack Compose:**
```kotlin
// ✅ CORRECT: Movie grid with contextual play buttons
@Composable
fun MovieCard(movie: Movie, onPlayClick: () -> Unit) {
    Card {
        IconButton(
            onClick = onPlayClick,
            modifier = Modifier.semantics {
                contentDescription = "Play ${movie.title}"
            }
        ) {
            Icon(Icons.Default.PlayArrow, contentDescription = null)
        }
    }
}

// Category "View all" with context
@Composable
fun CategoryRow(category: Category) {
    TextButton(
        onClick = { viewAllCategory(category) },
        modifier = Modifier.semantics {
            contentDescription = "View all ${category.name}"
        }
    ) {
        Text("View all")
    }
}
```

**WCAG SC:** 2.4.4, 2.4.9, 4.1.2 (see pattern guide for details)

---

## Android TV Specific

### D-pad Navigation

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

**Additional TV Considerations:**
- All interactive elements must be focusable
- Focus order should be logical (usually left-to-right, top-to-bottom)
- Focus indicators must be clearly visible
- Content descriptions still required for TalkBack on TV

---

## Files to Analyze

### XML-Based Projects
- `res/layout/*.xml` - All layout files
- `res/layout-land/*.xml` - Landscape layouts
- `res/menu/*.xml` - Menu definitions
- `res/values/strings.xml` - Check for contentDescription strings
- Custom View classes (`.kt`, `.java`)

### Compose Projects
- `*Screen.kt` - Screen composables
- `*Composable.kt` - Reusable composables
- `ui/**/*.kt` - UI components
- `theme/*.kt` - Theme and styling

### Other Files
- `Activity.kt` / `Fragment.kt` - Lifecycle and view setup
- Adapters (`*Adapter.kt`, `*ViewHolder.kt`)
- `navigation/*.xml` or navigation Compose files

---

## Testing Tools

### Automated
- **Accessibility Scanner** - Android app for scanning running apps
- **Espresso with Accessibility Checks** - Automated UI testing
  ```kotlin
  AccessibilityChecks.enable()
  ```
- **Layout Inspector** - Android Studio tool

### Manual Testing
- **TalkBack** - Enable in Settings > Accessibility
- **Switch Access** - For motor impairments
- **Select to Speak** - Text-to-speech
- **Font Size** - Test with large text (Settings > Display > Font size)

### TalkBack Gestures
- Swipe right/left: Next/previous item
- Double-tap: Activate
- Two-finger swipe down: Read from top
- Three-finger swipe: Navigate by headings

---

## Common Android-Specific Issues

### 1. RecyclerView Items

```kotlin
// ✅ CORRECT: Accessible RecyclerView item
class ItemViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    fun bind(item: Item) {
        itemView.apply {
            contentDescription = "${item.title}, ${item.description}"
            isClickable = true
            isFocusable = true
        }
    }
}
```

### 2. Bottom Navigation

```kotlin
// ✅ CORRECT: Label always shown for accessibility
<com.google.android.material.bottomnavigation.BottomNavigationView
    android:id="@+id/bottomNav"
    app:labelVisibilityMode="labeled"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

### 3. FAB (Floating Action Button)

```xml
<!-- ✅ CORRECT: FAB with content description -->
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/fab"
    android:src="@drawable/ic_add"
    android:contentDescription="@string/add_item"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

---

## Resources

### Official Documentation
- **Android Accessibility:** https://developer.android.com/guide/topics/ui/accessibility
- **Testing:** https://developer.android.com/guide/topics/ui/accessibility/testing
- **Compose Accessibility:** https://developer.android.com/jetpack/compose/accessibility
- **TalkBack:** https://support.google.com/accessibility/android/answer/6283677

### Code Labs
- **Basic Accessibility:** https://developer.android.com/codelabs/basic-android-accessibility
- **Jetpack Compose Accessibility:** https://developer.android.com/codelabs/jetpack-compose-accessibility

---

## Quick Checklist

- [ ] All ImageButton/ImageView elements have contentDescription or are marked decorative
- [ ] All Compose Icons have contentDescription or are properly marked as decorative
- [ ] Touch targets are minimum 48dp × 48dp
- [ ] EditText fields have persistent labels (not just hints)
- [ ] Section titles are marked as headings
- [ ] Custom clickable views have proper accessibility setup
- [ ] Dynamic content uses live regions or announcements
- [ ] Toggle states are properly announced
- [ ] Related content is grouped with mergeDescendants (Compose)
- [ ] Tested with TalkBack enabled
- [ ] Font scaling tested (up to largest size)
- [ ] D-pad navigation works (for TV)

---

**Related Guides:**
- GUIDE_WCAG_REFERENCE.md - WCAG principles
- GUIDE_ANDROID_TV.md - TV-specific guidance
- COMMON_ISSUES.md - Cross-platform patterns
- AUDIT_REPORT_TEMPLATE.md - Report format
