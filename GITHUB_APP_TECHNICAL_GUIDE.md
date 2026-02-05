# GitHub App Review System - Technical Documentation

## Overview

This document describes the technical implementation of the accessibility review system in the GitHub App, including recent improvements to address duplicate comments, improve diff parsing, and add SARIF support.

## Architecture

### Core Components

1. **webhook_server.py** - Flask webhook server that receives GitHub events
2. **pr_reviewer.py** - Core review logic using Scout AI
3. **comment_poster.py** - Posts review comments to GitHub PRs
4. **diff_parser.py** - Parses unified diffs and extracts commentable lines
5. **sarif_generator.py** - Generates SARIF reports for code scanning
6. **guide_loader.py** - Loads platform-specific accessibility guides

## Recent Improvements

### 1. Proper Diff Parsing and File Filtering

**Problem:** The original `_filter_diff_for_files()` was a stub that returned the full diff for every batch, causing duplicate issues and cross-file problems.

**Solution:** Implemented `diff_parser.py` with proper unified diff parsing:

```python
from app.diff_parser import DiffParser

# Parse diff into per-file sections
file_diffs = DiffParser.parse_diff(full_diff)

# Filter to specific files
batch_diff = DiffParser.filter_diff_for_files(full_diff, ['file1.py', 'file2.js'])
```

**Benefits:**
- Each batch now contains only the diff for files in that batch
- Reduces prompt size and prevents model from seeing irrelevant code
- Eliminates duplicate issues across batches

### 2. Accurate Line Mapping

**Problem:** The original `_extract_changed_lines()` treated entire hunk ranges as commentable, not actual added/context lines.

**Solution:** Implemented accurate commentable line extraction:

```python
# Extract only lines that GitHub allows comments on
commentable_lines = DiffParser.extract_commentable_lines(diff_text)

# Returns dict of {file: [line1, line2, ...]}
# Only includes:
# - Added lines (starting with '+')
# - Context lines (starting with ' ')
```

**Benefits:**
- Comments only placed on valid, commentable lines
- Automatic adjustment to nearest commentable line when needed
- Prevents GitHub API 422 errors for invalid line numbers

### 3. Stronger Deduplication Strategy

**Problem:** Simple file+line deduplication allowed near-duplicates with slightly different line numbers.

**Solution:** Implemented fingerprint-based deduplication:

```python
def _compute_issue_fingerprint(issue: Dict) -> str:
    """
    Fingerprint includes:
    - File path
    - WCAG SC (normalized)
    - Title (normalized)
    - Line bucket (rounded to nearest 5)
    """
    fingerprint_str = f"{file_path}|{line_bucket}|{wcag_sc}|{title_key}"
    return hashlib.md5(fingerprint_str.encode()).hexdigest()
```

**Benefits:**
- Catches near-duplicates (e.g., same issue at lines 42 and 44)
- Allows different issues at the same location
- More robust than simple location-based deduplication

### 4. "No Issues" Placeholder Filtering

**Problem:** Model sometimes returns placeholder issues saying "no issues found".

**Solution:** Filter out placeholder issues before posting:

```python
def is_no_issues_placeholder(issue: Dict) -> bool:
    """
    Detects placeholders by:
    - WCAG SC == "N/A" or empty
    - Title/description contains "no issues found"
    """
```

**Benefits:**
- Cleaner PR reviews without noise
- Only real issues are posted

### 5. Semantic Anchor Resolution

**Problem:** Comments could land on valid but semantically wrong lines (e.g., a Slider issue anchored to a Text label line instead of the `Slider(` call).

**Solution:** Implemented `SemanticAnchorResolver` that intelligently resolves issue line numbers to the correct UI element:

```python
from app.semantic_anchor_resolver import SemanticAnchorResolver

# Extract line texts from diff
line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
    diff_text, commentable_lines
)

# Resolve issue to semantic anchor (e.g., Slider( line)
resolved_line = SemanticAnchorResolver.resolve_issue_line(
    issue,
    file_path,
    commentable_lines[file_path],
    line_texts[file_path],
    max_distance=20
)
```

**Algorithm:**
1. Extract anchor candidates from issue metadata:
   - Explicit `anchor_text` field (future-proofing)
   - Keywords from title/description (e.g., "slider" → `Slider(` patterns)
   - UI element names (e.g., "Button" → `Button(`, `<Button`, `UIButton`)

2. Search for candidates in commentable line texts
3. Choose match closest to model-proposed line (within max_distance)
4. Fall back to nearest commentable line if no semantic match found

**Framework support:**
- **Compose/Kotlin:** `Slider(`, `Switch(`, `Button(`, `Text(`, `TextField(`, `.clickable`, `.semantics`, `Modifier.`
- **Android XML:** `<SeekBar`, `<Button`, `android:contentDescription`, `android:hint`, `android:text`
- **SwiftUI:** `Slider(`, `Toggle(`, `Button(`, `Text(`, `.accessibilityLabel`, `.accessibilityHint`
- **UIKit:** `UISlider`, `UIButton`, `UILabel`, `UITextField`, `accessibilityLabel`, `accessibilityTraits`
- **React/JSX/TSX/HTML:** `<button`, `<input`, `<img`, `aria-label`, `aria-labelledby`, `role=`, `onClick`

**Benefits:**
- Comments anchor to the actual UI element causing the issue
- Robust across multiple UI frameworks and languages
- Backwards compatible (works with or without explicit anchor hints)
- Falls back gracefully when no semantic match found

### 6. Android XML Layout Support

**Problem:** File filtering excluded ALL `.xml` files, blocking Android layout reviews.

**Solution:** Updated `filter_reviewable_files()`:

```python
# Special handling for XML files
if file_path.endswith('.xml'):
    # Include Android layout files
    if '/res/layout/' in file_path or '/res/layout-' in file_path:
        reviewable.append(file_path)
        continue
    
    # Exclude manifests and config XMLs
    if filename == 'AndroidManifest.xml':
        continue
```

**Benefits:**
- Android layout files (`res/layout/**/*.xml`) are now reviewed
- Excludes AndroidManifest.xml and resource XMLs (values, drawables, etc.)
- Better platform coverage

### 7. Batch Validation

**Problem:** Model could return issues for files not in the current batch.

**Solution:** Added `validate_issues_in_batch()`:

```python
validated_issues = validate_issues_in_batch(
    raw_issues,
    batch_files=['app/file1.py'],
    commentable_lines={'app/file1.py': [1, 2, 5, 10]}
)
```

**Validation steps:**
1. Drop issues for files not in batch
2. Drop issues with invalid line numbers (<= 0)
3. Adjust issues to nearest commentable line
4. Drop issues with no nearby commentable lines

**Benefits:**
- Guarantees issues match the batch being reviewed
- Prevents cross-contamination between batches

### 7. SARIF Output Support

**Problem:** No machine-readable output format for CI/CD integration.

**Solution:** Added SARIF generation:

```python
# Enable via environment variables
OUTPUT_SARIF=1
SARIF_OUTPUT_PATH=accessibility-report.sarif

# Generated SARIF includes:
# - WCAG rules with help URLs
# - Issue locations (file:line)
# - Severity mappings (Critical/High -> error, Medium -> warning, Low -> note)
# - Repository provenance (URI, commit SHA)
```

**Benefits:**
- Compatible with GitHub Code Scanning
- Machine-readable for CI/CD pipelines
- Can be uploaded to GitHub security tab
- Integrates with other SARIF tools

### 8. Comment Posting Fallback

**Problem:** 422 errors from GitHub when line numbers are invalid.

**Solution:** Added fallback in `CommentPoster`:

```python
try:
    # Try to post as inline comments
    post_review_comments(...)
except HTTPError as e:
    if e.response.status_code == 422:
        # Fallback: post as non-inline PR comment
        post_as_fallback_comments(...)
```

**Benefits:**
- Issues still get posted even if inline placement fails
- Fallback comment includes file:line and issue details
- Progressive posting continues to work

## Configuration

### Environment Variables

```bash
# Scout AI Configuration
SCOUT_API_KEY=your_api_key
SCOUT_BASE_URL=https://api.scout.ai
SCOUT_MODEL=gpt-5.2
SCOUT_MAX_TOKENS=2500
SCOUT_TEMPERATURE=0.0
SCOUT_FILES_PER_BATCH=1
SCOUT_MAX_DIFF_CHARS=180000
SCOUT_MAX_SNIPPET_LINES=30
SCOUT_RETRY_ATTEMPTS=4

# GitHub App Configuration
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY=your_private_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# SARIF Output (optional)
OUTPUT_SARIF=1
SARIF_OUTPUT_PATH=accessibility-report.sarif
```

### File Filtering Rules

**Included files:**
- UI code: `.kt`, `.java`, `.swift`, `.m`, `.mm`, `.tsx`, `.jsx`, `.js`, `.dart`
- Android layouts: `res/layout/**/*.xml`

**Excluded files:**
- Documentation: `.md`, `.txt`
- Build files: `.gradle`, `.json`, `.yaml`, `.yml`
- Config files: `AndroidManifest.xml`, `Info.plist`, `Podfile`
- Project files: `.xcodeproj`, `.pbxproj`
- CI/CD: `.github/workflows/**`

## Testing

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

- **test_diff_parser.py** (21 tests)
  - Diff parsing and filtering
  - Commentable line extraction
  - Line adjustment and validation
  - Placeholder detection

- **test_sarif_generator.py** (12 tests)
  - SARIF structure generation
  - Rule and result mapping
  - Severity conversion
  - File I/O

## API Reference

### DiffParser

```python
from app.diff_parser import DiffParser

# Parse diff into file sections
file_diffs = DiffParser.parse_diff(diff_text)
# Returns: Dict[str, str] mapping file paths to diff sections

# Filter to specific files
filtered = DiffParser.filter_diff_for_files(diff_text, file_list)
# Returns: str containing only requested files

# Extract commentable lines
commentable = DiffParser.extract_commentable_lines(diff_text)
# Returns: Dict[str, List[int]] mapping files to line numbers

# Find nearest commentable line
nearest = DiffParser.find_nearest_commentable_line(42, [1, 5, 10, 50])
# Returns: int (nearest line) or None
```

### SARIFGenerator

```python
from app.sarif_generator import SARIFGenerator, generate_and_write_sarif

# Generate SARIF from issues
generator = SARIFGenerator()
sarif = generator.generate_sarif(
    issues,
    repo_uri="https://github.com/owner/repo",
    repo_ref="abc123"
)

# Write to file
success = generator.write_sarif_file(sarif, "report.sarif")

# Or use convenience function
success = generate_and_write_sarif(issues, "report.sarif")
```

## Troubleshooting

### Issue: Comments appear on wrong lines

**Cause:** Diff parsing or line mapping issue

**Solution:**
1. Check that `extract_commentable_lines()` is being used
2. Verify batch filtering is working
3. Check test coverage with `test_diff_parser.py`

**New:** The system now uses semantic anchor resolution to intelligently place comments on the correct UI element declaration/call site rather than just the nearest commentable line. This is handled automatically by `validate_issues_in_batch()` when passed the diff text.

### Issue: Comment mis-anchoring on semantically wrong lines

**Cause:** Model proposes line number that's valid but not the correct UI element

**Solution:** The semantic anchor resolver (introduced in this release) automatically handles this:

1. **How it works:**
   - Extracts anchor candidates from issue metadata (title, description, WCAG SC)
   - Searches for UI element patterns (e.g., `Slider(`, `<button`, `UIButton`) in commentable lines
   - Resolves to the closest matching UI element within 20 lines of the proposed line
   - Falls back to nearest commentable line if no semantic match found

2. **Supported frameworks:**
   - Android Compose/Kotlin: `Slider(`, `Button(`, `Text(`, `TextField(`, `.clickable`, `.semantics`
   - Android XML: `<SeekBar`, `<Button`, `android:contentDescription`, `android:hint`
   - iOS SwiftUI: `Slider(`, `Toggle(`, `Button(`, `.accessibilityLabel`
   - iOS UIKit: `UISlider`, `UIButton`, `accessibilityLabel`
   - Web React/JSX/TSX/HTML: `<button`, `<input`, `aria-label`, `onClick`

3. **Verification:**
   - Check logs for "semantic anchor" adjustment messages
   - Run tests: `pytest tests/test_semantic_anchor_resolver.py -v`

4. **Customization:**
   - Add patterns to `SemanticAnchorResolver` class in `app/semantic_anchor_resolver.py`
   - Adjust `max_distance` parameter in `validate_issues_in_batch()` call

### Issue: Duplicate comments

**Cause:** Deduplication not working

**Solution:**
1. Verify fingerprinting is enabled in `_compute_issue_fingerprint()`
2. Check that diff filtering is working (not sending full diff to each batch)
3. Increase line bucket size if needed (currently 5)

### Issue: No Android XML files reviewed

**Cause:** File filtering issue

**Solution:**
1. Check `filter_reviewable_files()` in `webhook_server.py`
2. Verify files match pattern `/res/layout/`
3. Check logs for "Skipping non-reviewable file" messages

### Issue: 422 errors when posting comments

**Cause:** Invalid line numbers

**Solution:**
1. Verify fallback is enabled in `CommentPoster`
2. Check that `validate_issues_in_batch()` is being called
3. Issues should be posted as non-inline comments as fallback

## Future Improvements

### Planned Enhancements

1. **Code scanning integration** - Automatic upload of SARIF to GitHub
2. **Smarter batching** - Group related files (e.g., component + test)
3. **Context awareness** - Use git blame to identify file experts
4. **Progressive hints** - Show progress in PR status checks
5. **Auto-fix suggestions** - Generate PR with fixes for common issues

### Contributing

To contribute improvements:

1. Add tests in `tests/` for new functionality
2. Update this documentation
3. Ensure all tests pass: `pytest tests/ -v`
4. Run linting: `black app/ tests/` and `flake8 app/ tests/`
5. Open a PR with clear description of changes

## References

- [GitHub REST API - Pull Reviews](https://docs.github.com/en/rest/pulls/reviews)
- [SARIF Format Spec](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/Understanding/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
