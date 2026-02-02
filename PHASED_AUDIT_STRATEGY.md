# Phased Audit Strategy
## Breaking Down Large Projects into Manageable Chunks

---

## The Problem with "Complete" Audits

For large multi-platform projects, attempting a comprehensive audit all at once:
- **Overwhelms resources** (time, token usage, attention)
- **Produces massive reports** that are hard to review
- **Delays actionable results** until everything is done
- **Makes it difficult to track progress**

## The Solution: Incremental, Phased Auditing

Break the work into **small, focused phases** that:
- Produce actionable results quickly
- Can be done in separate sessions
- Allow for parallel work (different team members)
- Provide clear stopping points
- Build comprehensive coverage over time

---

## Strategy 1: One Platform at a Time

### ✅ RECOMMENDED APPROACH

**Never audit multiple platforms in one session.**

```
Phase 1: Audit Web platform only
Phase 2: Audit Android platform only
Phase 3: Audit iOS platform only
Phase 4: Audit tvOS platform only
Phase 5: Audit Android TV platform only
```

### Example Prompt (Web Only)
```
I want to audit ONLY the web platform for accessibility issues.

Follow the ACCESSIBILITY_AUDIT_GUIDE.md framework.

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Phase1_2025-01-29.md

Analyze web components for accessibility issues.
Focus ONLY on web - ignore Android, iOS, and other platforms.
```

### Why This Works
- Each platform has different APIs and patterns
- Separate reports prevent confusion
- You can deliver platform-specific results to different teams
- Easier to schedule screenshot capture sessions

---

## Strategy 2: Break Platform by Feature Area

For large platforms, break down by user flows or feature areas.

### Example: Web Platform in Phases

```
Phase 1: Authentication (login, signup, password reset)
Phase 2: Main Navigation (header, sidebar, footer, menus)
Phase 3: Content Pages (home, about, articles, etc.)
Phase 4: Forms (contact, checkout, user settings)
Phase 5: Media (images, videos, carousels, galleries)
Phase 6: Interactive Components (modals, dropdowns, tooltips, tabs)
```

### Example Prompt (Feature-Specific)
```
I want to audit ONLY the authentication flow for accessibility issues (web platform).

This includes:
- Login page (src/pages/Login.tsx)
- Signup page (src/pages/Signup.tsx)
- Password reset flow
- Related components (src/components/auth/)

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Authentication_2025-01-29.md

Analyze for:
- Form labels and error messages
- Keyboard navigation
- Screen reader compatibility
- Focus management

Ignore other parts of the app for now.
```

### Why This Works
- Focus on complete user flows
- Results are immediately testable
- Teams can fix issues in parallel
- Clear scope boundaries

---

## Strategy 3: Break by Component Type

Group similar components together for consistency.

### Example: Web Components by Type

```
Phase 1: Forms and Inputs
Phase 2: Buttons and Links
Phase 3: Images and Icons
Phase 4: Navigation Components
Phase 5: Data Tables and Lists
Phase 6: Modal Dialogs and Overlays
Phase 7: Custom Interactive Widgets
```

### Example Prompt (Component-Specific)
```
I want to audit ONLY form components for accessibility issues (web platform).

Analyze all:
- Form elements (input, select, textarea, checkbox, radio)
- Form validation and error handling
- Labels and instructions
- Submit buttons

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Forms_2025-01-29.md

Check for:
- Missing labels (WCAG 3.3.2)
- Error identification (WCAG 3.3.1)
- Input purpose (WCAG 1.3.5)
- Keyboard accessibility (WCAG 2.1.1)

Ignore navigation, images, and other component types.
```

### Why This Works
- Consistent fixes across similar components
- Easy to create component library guidelines
- Developers can specialize in specific component types
- Patterns emerge quickly

---

## Strategy 4: Break by WCAG Principle

Focus on one WCAG principle at a time across the platform.

### Example: Platform by WCAG Principle

```
Phase 1: Perceivable Issues
  - Alternative text (1.1.1)
  - Color contrast (1.4.3, 1.4.11)
  - Info and relationships (1.3.1)

Phase 2: Operable Issues
  - Keyboard accessibility (2.1.1, 2.1.2)
  - Focus visible (2.4.7)
  - Target size (2.5.8)

Phase 3: Understandable Issues
  - Labels and instructions (3.3.2)
  - Error identification (3.3.1)
  - Consistent navigation (3.2.3)

Phase 4: Robust Issues
  - Name, role, value (4.1.2)
  - Status messages (4.1.3)
  - Parsing (4.1.1)
```

### Example Prompt (Principle-Specific)
```
I want to audit for PERCEIVABLE accessibility issues ONLY (WCAG Principle 1) on the web platform.

Focus on:
- 1.1.1 Non-text Content (alt text)
- 1.3.1 Info and Relationships (semantic structure)
- 1.4.3 Contrast (Minimum)
- 1.4.11 Non-text Contrast

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Perceivable_2025-01-29.md

Ignore keyboard, focus, form labels, and other non-Perceivable issues for now.
```

### Why This Works
- Deep focus on related issues
- Easier to understand WCAG compliance
- Good for training and learning
- Clear compliance metrics per principle

---

## Strategy 5: Break by Directory/Module

For code-organized projects, audit directory by directory.

### Example: Web by Directory

```
Phase 1: src/components/common/
Phase 2: src/components/forms/
Phase 3: src/components/navigation/
Phase 4: src/pages/auth/
Phase 5: src/pages/dashboard/
Phase 6: src/pages/settings/
```

### Example Prompt (Directory-Specific)
```
I want to audit ONLY the src/components/forms/ directory for accessibility issues.

Analyze all files in:
- src/components/forms/

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_FormComponents_2025-01-29.md

Check all WCAG criteria but only for files in this directory.
Ignore other directories for now.
```

### Why This Works
- Aligns with code ownership
- Easy to track code changes
- Clear file boundaries
- Good for large codebases

---

## Strategy 6: Break by Issue Severity

Start with critical issues, then work down.

### Example: Severity-Based Phases

```
Phase 1: Identify ALL Critical and High severity issues (quick scan)
Phase 2: Deep dive on Critical issues with detailed fixes
Phase 3: Deep dive on High severity issues with detailed fixes
Phase 4: Medium severity issues
Phase 5: Low severity issues and enhancements
```

### Example Prompt (Severity-First)
```
I want to do a QUICK SCAN of the web platform to identify ONLY Critical and High severity accessibility issues.

Don't provide detailed fixes yet - just identify:
- Issue location (file and line)
- Brief description
- WCAG SC violated
- Severity (Critical or High only)

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_CriticalScan_2025-01-29.md

This is a rapid assessment to prioritize work.
```

Then follow up:
```
Now provide detailed analysis and fixes for all Critical issues from the previous scan.

Create detailed report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_CriticalDetails_2025-01-29.md
```

### Why This Works
- Fast identification of blockers
- Prioritize fixes that matter most
- Quick wins for stakeholders
- Progressive enhancement approach

---

## Strategy 7: Break by Screen/Page

For apps with distinct screens, audit one screen at a time.

### Example: Android App by Screen

```
Phase 1: Login Screen
Phase 2: Home Screen
Phase 3: Profile Screen
Phase 4: Settings Screen
Phase 5: Content Detail Screen
Phase 6: Search Screen
```

### Example Prompt (Screen-Specific)
```
I want to audit ONLY the Login Screen for accessibility issues (Android platform).

Files to analyze:
- app/src/main/java/com/example/ui/login/LoginActivity.kt
- app/src/main/res/layout/activity_login.xml
- Related composables or fragments

Create report at:
accessibility-audit/reports/android/Accessibility_Audit_Android_LoginScreen_2025-01-29.md

Check all Android accessibility best practices for this screen only.
```

### Why This Works
- Matches QA testing approach
- Easy to reproduce issues
- Clear scope for manual testing
- Good for demo/presentation to stakeholders

---

## Hybrid Strategies

Combine multiple strategies for best results:

### Example: Platform → Feature → Component

```
Phase 1: Web → Authentication → Forms
Phase 2: Web → Authentication → Buttons
Phase 3: Web → Authentication → Navigation
Phase 4: Web → Dashboard → Forms
[etc.]
```

### Example: Platform → Severity → Fix

```
Phase 1: Web → Identify all Critical issues
Phase 2: Web → Fix Critical issues (with developer)
Phase 3: Web → Identify High issues
Phase 4: Web → Fix High issues
[repeat for each platform]
```

---

## Practical Workflow Example

### Large E-Commerce App (Web + iOS + Android)

#### Week 1: Web Critical Flow
```
Session 1: Web checkout flow - Critical issues scan
Session 2: Web checkout flow - Detailed audit with fixes
Session 3: Developer fixes issues, tester captures screenshots
```

#### Week 2: Web Secondary Flows
```
Session 4: Web product browsing - Audit
Session 5: Web user account - Audit
Session 6: Screenshot capture and report finalization
```

#### Week 3: iOS Critical Flow
```
Session 7: iOS checkout flow - Audit
Session 8: iOS product browsing - Audit
[etc.]
```

#### Week 4: Android Critical Flow
```
Session 10: Android checkout flow - Audit
Session 11: Android product browsing - Audit
[etc.]
```

#### Week 5: Consolidation
```
Session 13: Create master summary across all platforms
Session 14: Prioritize cross-platform issues
Session 15: Final report for client
```

---

## Recommended Phase Sizes

For optimal sessions with Claude Code:

| Phase Scope | Est. Time | Output Size | When to Use |
|-------------|-----------|-------------|-------------|
| **Single screen/page** | 15-30 min | 5-15 issues | First audit, learning |
| **Feature area** | 30-60 min | 15-30 issues | Standard approach |
| **Component type** | 30-60 min | 20-40 issues | Pattern discovery |
| **Directory** | 30-90 min | 20-50 issues | Code-organized projects |
| **Severity scan** | 15-30 min | Issue list | Quick prioritization |
| **Full platform** | 2-4+ hours | 50-200+ issues | Small apps only |

**Golden Rule:** If a session would take more than 1 hour, break it down further.

---

## Sample Prompts for Phased Audits

### Phase 1: Start with Critical Path
```
I want to audit the most critical user flow for accessibility.

Platform: Web
Flow: User login → Browse products → Add to cart → Checkout

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_CheckoutFlow_Phase1_2025-01-29.md

Focus only on this flow. Identify Critical and High severity issues first.
```

### Phase 2: Deep Dive on Issues
```
Continue the web checkout flow audit.

Now provide detailed analysis for:
- All forms in the flow
- All error handling
- All interactive components

Add to report:
accessibility-audit/reports/web/Accessibility_Audit_Web_CheckoutFlow_Phase2_2025-01-29.md
```

### Phase 3: Next Feature Area
```
Audit the account management area for accessibility (web platform).

This includes:
- Profile editing
- Password change
- Preferences/settings
- Order history

Create new report:
accessibility-audit/reports/web/Accessibility_Audit_Web_Account_Phase3_2025-01-29.md
```

### Phase 4: Move to Next Platform
```
We've completed web. Now audit the iOS app starting with the checkout flow.

Create report:
accessibility-audit/reports/ios/Accessibility_Audit_iOS_CheckoutFlow_Phase1_2025-01-29.md

Focus on VoiceOver, Dynamic Type, and touch targets.
```

---

## Progress Tracking

### Create a Tracking Document

```markdown
# Accessibility Audit Progress

## Web Platform
- [x] Phase 1: Checkout Flow (Critical) - 2025-01-29
- [x] Phase 2: Checkout Flow (Detailed) - 2025-01-30
- [x] Phase 3: Account Management - 2025-01-31
- [ ] Phase 4: Product Browsing
- [ ] Phase 5: Search and Filters
- [ ] Phase 6: Content Pages

## Android Platform
- [ ] Phase 1: Checkout Flow
- [ ] Phase 2: Account Management
- [ ] Phase 3: Product Browsing

## iOS Platform
- [ ] Phase 1: Checkout Flow
- [ ] Phase 2: Account Management
- [ ] Phase 3: Product Browsing

## Totals
- Issues Found: 47
- Issues Fixed: 12
- Issues Remaining: 35
- Platforms Completed: 0/3
```

---

## Tips for Successful Phased Audits

### 1. Always Start with High-Impact Areas
- Critical user flows first
- Most-used features first
- Revenue-generating paths first

### 2. Maintain Consistency
- Use same report format for all phases
- Number issues consecutively (Issue #001, #002, etc.)
- Keep same naming conventions

### 3. Track Dependencies
- Note when issues appear across multiple areas
- Link related issues
- Identify patterns early

### 4. Document Assumptions
```markdown
## Scope for This Phase
**Included:** Login and signup screens only
**Excluded:** Password reset (will be Phase 2)
**Assumptions:** Using TalkBack version X.X
```

### 5. Set Clear Exit Criteria
```markdown
## Phase Complete When:
- [x] All components in src/auth/ analyzed
- [x] Report generated with issues
- [x] Critical issues have code fixes provided
- [ ] Screenshots captured (pending)
```

---

## When to Consolidate

After completing 3-5 phases, create an interim summary:

```
I've completed these audit phases:
1. Web - Checkout Flow
2. Web - Account Management
3. Web - Product Browsing

Create an interim summary at:
accessibility-audit/reports/web/Accessibility_Audit_Web_InterimSummary_2025-02-05.md

Include:
- Total issues found so far
- Patterns and common issues
- Recommendations for remaining audits
- Estimated remaining work
```

---

## Example: Complete Phased Audit Plan

### Project: Streaming App (Web + Android TV + tvOS)

```
PHASE 1 - CRITICAL PATH - ALL PLATFORMS
├── 1a. Web: Browse → Play video
├── 1b. Android TV: Browse → Play video
└── 1c. tvOS: Browse → Play video
    └── Deliverable: Critical path accessibility report

PHASE 2 - USER ACCOUNTS - ALL PLATFORMS
├── 2a. Web: Login, signup, profile
├── 2b. Android TV: Login, profile
└── 2c. tvOS: Login, profile
    └── Deliverable: Account management accessibility report

PHASE 3 - CONTENT DISCOVERY - ALL PLATFORMS
├── 3a. Web: Search, filters, recommendations
├── 3b. Android TV: Search, navigation
└── 3c. tvOS: Search, navigation
    └── Deliverable: Discovery accessibility report

PHASE 4 - MEDIA CONTROLS - ALL PLATFORMS
├── 4a. Web: Video player controls
├── 4b. Android TV: Video player controls
└── 4c. tvOS: Video player controls
    └── Deliverable: Media player accessibility report

PHASE 5 - CONSOLIDATION
├── 5a. Master summary across all platforms
├── 5b. Cross-platform issue analysis
└── 5c. Prioritized fix roadmap
    └── Deliverable: Final client report
```

---

## Conclusion

**The key to successful accessibility audits on large projects is:**

1. ✅ **ONE PLATFORM AT A TIME** - Never mix platforms
2. ✅ **SMALL PHASES** - 30-60 minute sessions
3. ✅ **CLEAR BOUNDARIES** - Feature, component, or directory
4. ✅ **ACTIONABLE RESULTS** - Each phase produces a usable report
5. ✅ **PROGRESSIVE COVERAGE** - Build comprehensive results over time

**Remember:** It's better to have 5 complete, detailed reports on specific areas than one incomplete report trying to cover everything.
