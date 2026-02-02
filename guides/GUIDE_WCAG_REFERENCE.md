# WCAG 2.2 Reference Guide
## Shared Knowledge for All Platforms

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

## WCAG Documentation Resources

### Official W3C Resources
- **WCAG 2.2 Guidelines:** https://www.w3.org/TR/WCAG22/
- **Understanding WCAG 2.2:** https://www.w3.org/WAI/WCAG22/Understanding/
- **How to Meet WCAG (Quick Reference):** https://www.w3.org/WAI/WCAG22/quickref/
- **WCAG 2.2 JSON Data (Machine-Readable):** https://www.w3.org/WAI/WCAG22/wcag.json
- **WCAG 2.2 on Mobile:** https://www.w3.org/TR/mobile-accessibility-mapping/

### Internal WCAG Reference Library
**Detailed Success Criteria by Principle:**
- [Principle 1: Perceivable](wcag/PRINCIPLE_1_PERCEIVABLE.md) - Images, media, structure, contrast
- [Principle 2: Operable](wcag/PRINCIPLE_2_OPERABLE.md) - Keyboard, navigation, input, timing
- [Principle 3: Understandable](wcag/PRINCIPLE_3_UNDERSTANDABLE.md) - Readability, predictability, input assistance
- [Principle 4: Robust](wcag/PRINCIPLE_4_ROBUST.md) - Compatibility, name/role/value, status messages

**Quick References:**
- [Quick Lookup Tables](wcag/QUICK_LOOKUP.md) - Fast reference by user need, component, platform
- [Component-to-WCAG Mappings](wcag/COMPONENT_WCAG_MAPPINGS.md) - Which SC applies to which components
- [Severity Guidelines](wcag/SEVERITY_GUIDELINES.md) - How to assign severity levels
- [Mobile WCAG Interpretation](wcag/MOBILE_WCAG_INTERPRETATION.md) - Applying web WCAG to native apps

### Community Resources
- **WebAIM Mailing List:** https://webaim.org/discussion/
- **A11y Slack Community:** https://web-a11y.slack.com/
- **Deque Blog:** https://www.deque.com/blog/

---

## Severity Guidelines

**Critical:**
- Blocks core functionality
- Affects many users
- Violates Level A criteria
- Examples: Cannot submit form, cannot navigate with keyboard

**High:**
- Significantly impairs experience
- Affects moderate number of users
- Violates Level AA criteria
- Examples: Low contrast, missing headings, collection items not grouped

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

**For detailed severity assignment rules, see:** [Severity Guidelines](wcag/SEVERITY_GUIDELINES.md)

---

## Best Practices for Auditors

1. **Be Specific:** Always provide file paths, line numbers, and exact locations
2. **Show Impact:** Explain how each issue affects real users
3. **Provide Solutions:** Include working code examples for fixes
4. **Visual Evidence:** Screenshot every issue when possible
5. **Test with Real AT:** Don't rely only on automated tools
6. **Consider Context:** Mobile apps have different patterns than web
7. **Stay Updated:** WCAG and platform guidelines evolve

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

---

## Quick Start: Where to Find Information

**I need to know...**
- **Which WCAG SC applies to a button/image/form?** → [Component-to-WCAG Mappings](wcag/COMPONENT_WCAG_MAPPINGS.md)
- **How severe is this issue?** → [Severity Guidelines](wcag/SEVERITY_GUIDELINES.md)
- **What does WCAG SC 4.1.2 mean for mobile?** → [Mobile WCAG Interpretation](wcag/MOBILE_WCAG_INTERPRETATION.md)
- **All details about Principle 1?** → [Principle 1: Perceivable](wcag/PRINCIPLE_1_PERCEIVABLE.md)
- **Quick implementation examples?** → [Quick Lookup Tables](wcag/QUICK_LOOKUP.md)
- **Collection/list accessibility?** → [Collection Items Pattern](patterns/COLLECTION_ITEMS_PATTERN.md)
- **Text scaling requirements?** → [Font Scaling Support](patterns/FONT_SCALING_SUPPORT.md)
- **Decorative image rules?** → [Decorative Image Decision Tree](patterns/DECORATIVE_IMAGE_DECISION_TREE.md)

---

**For platform-specific guidance, see:**
- [GUIDE_WEB.md](GUIDE_WEB.md)
- [GUIDE_ANDROID.md](GUIDE_ANDROID.md)
- [GUIDE_IOS.md](GUIDE_IOS.md)
- [GUIDE_REACT_NATIVE.md](GUIDE_REACT_NATIVE.md)
- [GUIDE_FLUTTER.md](GUIDE_FLUTTER.md)
- [GUIDE_ANDROID_TV.md](GUIDE_ANDROID_TV.md)
- [GUIDE_TVOS.md](GUIDE_TVOS.md)
- [COMMON_ISSUES.md](COMMON_ISSUES.md)
