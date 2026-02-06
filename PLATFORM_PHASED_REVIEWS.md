# Platform-Phased Reviews

## Overview

Platform-phased reviews reduce Scout LLM prompt context size by reviewing files platform-by-platform rather than all at once. This approach:

1. **Reduces memory/context usage** - Only loads guides and reviews files for one platform at a time
2. **Improves accuracy** - Scout focuses on one platform's accessibility patterns per phase
3. **Maintains consistency** - Global comment tracking prevents duplicates across phases

## How It Works

### Phase Order

When a PR contains files from multiple platforms, they are reviewed in this strict order:

1. **Android** (`.kt`, `.java`)
2. **iOS** (`.swift`, `.m`, `.mm`)
3. **Web** (`.css`, `.html`, and content-detected `.tsx`/`.jsx`/`.ts`/`.js`)
4. **React Native** (content-detected `.tsx`/`.jsx`/`.ts`/`.js`)
5. **Flutter** (`.dart`)

### Content-Based Detection

For `.tsx`, `.jsx`, `.ts`, and `.js` files, the system analyzes the diff content to distinguish between Web and React Native:

**React Native Detection (strong signals):**
- Imports from `'react-native'`: `import { View } from 'react-native'`
- Requires from `'react-native'`: `require('react-native')`
- React Native component tags: `<View>`, `<Text>`, `<TouchableOpacity>`, `<ScrollView>`, etc.

**Web Detection (default):**
- No React Native signals found
- Uses standard HTML elements: `<button>`, `<div>`, `<input>`, etc.
- `.css` and `.html` files are always Web

### Per-Phase Processing

For each platform phase:

1. **File Filtering** - Only files belonging to that platform are included
2. **Guide Loading** - Only that platform's guides are loaded (e.g., `load_platform_specific_guides(["Android"])`)
3. **Comment Filtering** - `existing_comments` and `review_threads` are filtered to only include entries for files in this phase
4. **Review** - `PRReviewer.review_pr_diff()` is called with:
   - Platform-specific files
   - Single platform in the platforms list
   - Platform-specific guides
   - Filtered existing comments and threads

### Global Comment Tracking

While phases are independent, comment deduplication remains global:

- `posted_locations` is maintained across all phases
- Prevents posting duplicate comments even if they would appear in different phases
- The `on_batch_complete` callback continues to work across phases
- Final status is based on all issues found across all phases

## Example Flow

### Multi-Platform PR

Consider a PR with these files:
```
android/MainActivity.kt
ios/ViewController.swift
web/styles.css
mobile/App.tsx (React Native)
lib/main.dart
```

**Phase 1: Android**
- Files: `android/MainActivity.kt`
- Guides: `GUIDE_ANDROID.md`, `COMMON_ISSUES.md`, `GUIDE_WCAG_REFERENCE.md`
- Reviews: Only Android-specific issues

**Phase 2: iOS**
- Files: `ios/ViewController.swift`
- Guides: `GUIDE_IOS.md`, `COMMON_ISSUES.md`, `GUIDE_WCAG_REFERENCE.md`
- Reviews: Only iOS-specific issues

**Phase 3: Web**
- Files: `web/styles.css`
- Guides: `GUIDE_WEB.md`, `COMMON_ISSUES.md`, `GUIDE_WCAG_REFERENCE.md`
- Reviews: Only Web-specific issues

**Phase 4: React Native**
- Files: `mobile/App.tsx`
- Guides: `GUIDE_REACT_NATIVE.md`, `COMMON_ISSUES.md`, `GUIDE_WCAG_REFERENCE.md`
- Reviews: Only React Native-specific issues

**Phase 5: Flutter**
- Files: `lib/main.dart`
- Guides: `GUIDE_FLUTTER.md`, `COMMON_ISSUES.md`, `GUIDE_WCAG_REFERENCE.md`
- Reviews: Only Flutter-specific issues

### Single-Platform PR

If a PR only contains Android files, only the Android phase runs:

```
android/MainActivity.kt
android/Fragment.java
```

**Phase 1: Android (only phase)**
- Files: Both Android files
- Guides: Android-specific guides
- Reviews: All issues found

## Implementation Details

### Key Files

- **`app/platform_bucketing.py`** - Platform detection and file bucketing logic
- **`app/webhook_server.py`** - Phased review orchestration in `handle_pull_request()`
- **`app/guide_loader.py`** - Already supports `load_platform_specific_guides(platforms)`

### Key Functions

#### `bucket_files_by_platform(changed_files, pr_diff)`
Buckets files by platform based on extension and content analysis.

**Returns:** Dict mapping platform names to file lists
```python
{
    "Android": ["MainActivity.kt"],
    "iOS": ["ViewController.swift"],
    "Web": ["styles.css"],
    "React Native": ["App.tsx"],
    "Flutter": ["main.dart"]
}
```

#### `get_platforms_in_order(buckets)`
Returns platforms that have files, in strict order.

**Returns:** List of platform names
```python
["Android", "iOS", "React Native"]  # Only these have files
```

#### `filter_locations_for_files(locations, file_paths)`
Filters existing_comments or review_threads to only include entries for specified files.

**Supports:**
- Tuples: `(file, line)`, `(file, line, snippet)`, etc.
- Dicts: `{"file": ..., "line": ...}` or `{"path": ..., "line": ...}`

#### `detect_react_native_in_diff(file_path, pr_diff)`
Analyzes a file's diff content to determine if it's React Native.

**Returns:** `True` if React Native signals found, `False` otherwise

## Testing

### Test Files

- **`tests/test_platform_bucketing.py`** - 21 tests for platform detection and bucketing
- **`tests/test_phased_review_integration.py`** - 8 integration tests for phased review flow
- All existing tests (143 total) pass without regression

### Running Tests

```bash
# Platform bucketing tests
pytest tests/test_platform_bucketing.py -v

# Integration tests
pytest tests/test_phased_review_integration.py -v

# All tests
pytest tests/ -v
```

## Logging

The phased review process includes detailed logging:

```
Bucketing files by platform...
Platforms detected (in review order): ['Android', 'iOS', 'Web']
  Android: 2 files
  iOS: 3 files
  Web: 5 files

Starting platform-phased accessibility review...

================================================================================
PHASE 1/3: Reviewing Android
================================================================================
Files in this phase: 2
Loading Android-specific guides...
Loaded guides: 45000 characters
Filtered existing comments: 5 (out of 20 total)
Filtered review threads: 3 (out of 15 total)
...
Phase 1 complete. Total issues so far: 12

================================================================================
PHASE 2/3: Reviewing iOS
================================================================================
...
```

## Benefits

### Context Size Reduction

**Before (single-phase):**
- All platform guides loaded: ~200KB
- All files in prompt: 10 files × 5KB = 50KB
- Total: ~250KB per Scout call

**After (phased):**
- Per-phase guides: ~50KB each
- Per-phase files: 2-3 files × 5KB = 10-15KB
- Total per phase: ~60-65KB per Scout call
- **~75% reduction in context size per call**

### Improved Accuracy

Scout can focus on one platform's patterns at a time, reducing confusion between:
- Android's `contentDescription` vs iOS's `accessibilityLabel`
- React Native's `accessible` vs Web's `aria-label`
- Platform-specific components and APIs

### Scalability

Phased reviews enable reviewing larger PRs that would exceed Scout's context window if done in a single phase.

## Migration

No configuration changes needed. The phased review logic is automatically used for all PRs.

**Backward Compatibility:**
- Single-platform PRs work exactly as before
- Multi-platform PRs now use phased approach
- All existing tests pass
- Comment deduplication logic unchanged
