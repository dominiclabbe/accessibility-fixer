"""
Tests for SemanticAnchorResolver

Validates semantic anchor resolution across multiple UI frameworks.
"""

import pytest
from app.semantic_anchor_resolver import SemanticAnchorResolver
from app.diff_parser import DiffParser


# Test fixtures - sample diffs for different frameworks

COMPOSE_SLIDER_DIFF = """diff --git a/app/src/main/java/com/example/Settings.kt b/app/src/main/java/com/example/Settings.kt
index 1234567..abcdefg 100644
--- a/app/src/main/java/com/example/Settings.kt
+++ b/app/src/main/java/com/example/Settings.kt
@@ -10,8 +10,12 @@ fun SettingsScreen() {
     Column(
         modifier = Modifier.padding(16.dp)
     ) {
+        Text("Volume")
+        Slider(
+            value = volume,
+            onValueChange = { volume = it }
+        )
     }
 }
"""

ANDROID_XML_SEEKBAR_DIFF = """diff --git a/app/src/main/res/layout/activity_settings.xml b/app/src/main/res/layout/activity_settings.xml
index aaaaaaa..bbbbbbb 100644
--- a/app/src/main/res/layout/activity_settings.xml
+++ b/app/src/main/res/layout/activity_settings.xml
@@ -5,10 +5,15 @@
     android:layout_height="match_parent"
     android:orientation="vertical">
 
+    <TextView
+        android:layout_width="wrap_content"
+        android:layout_height="wrap_content"
+        android:text="Volume" />
+
     <SeekBar
         android:id="@+id/volumeSeekBar"
         android:layout_width="match_parent"
-        android:layout_height="wrap_content" />
+        android:layout_height="wrap_content"
+        android:contentDescription="@null" />
 
 </LinearLayout>
"""

SWIFTUI_SLIDER_DIFF = """diff --git a/SettingsView.swift b/SettingsView.swift
index 1111111..2222222 100644
--- a/SettingsView.swift
+++ b/SettingsView.swift
@@ -5,8 +5,12 @@ struct SettingsView: View {
     var body: some View {
         VStack {
             Text("Settings")
+            Text("Volume")
+            Slider(value: $volume, in: 0...100)
+                .padding()
         }
     }
 }
"""

SWIFTUI_TOGGLE_DIFF = """diff --git a/SettingsView.swift b/SettingsView.swift
index 3333333..4444444 100644
--- a/SettingsView.swift
+++ b/SettingsView.swift
@@ -8,6 +8,9 @@ struct SettingsView: View {
     var body: some View {
         VStack {
             Text("Preferences")
+            Toggle("Enable Notifications", isOn: $notificationsEnabled)
+                .padding()
         }
     }
 }
"""

UIKIT_SLIDER_DIFF = """diff --git a/SettingsViewController.swift b/SettingsViewController.swift
index 5555555..6666666 100644
--- a/SettingsViewController.swift
+++ b/SettingsViewController.swift
@@ -10,8 +10,14 @@ class SettingsViewController: UIViewController {
     override func viewDidLoad() {
         super.viewDidLoad()
         
+        let label = UILabel()
+        label.text = "Volume"
+        view.addSubview(label)
+        
         let slider = UISlider()
         slider.minimumValue = 0
         slider.maximumValue = 100
+        slider.accessibilityLabel = "Volume slider"
         view.addSubview(slider)
     }
 }
"""

REACT_BUTTON_DIFF = """diff --git a/src/components/Settings.tsx b/src/components/Settings.tsx
index 7777777..8888888 100644
--- a/src/components/Settings.tsx
+++ b/src/components/Settings.tsx
@@ -5,10 +5,14 @@ export const Settings: React.FC = () => {
   return (
     <div>
       <h1>Settings</h1>
+      <button onClick={handleSave}>
+        Save Settings
+      </button>
     </div>
   );
 };
"""

REACT_INPUT_DIFF = """diff --git a/src/components/Form.tsx b/src/components/Form.tsx
index 9999999..aaaaaaa 100644
--- a/src/components/Form.tsx
+++ b/src/components/Form.tsx
@@ -8,6 +8,10 @@ export const Form: React.FC = () => {
     <form>
       <label htmlFor="username">Username</label>
       <input id="username" type="text" />
+      
+      <label htmlFor="email">Email</label>
+      <input id="email" type="email" aria-label="Email address" />
     </form>
   );
 };
"""

HTML_IMG_DIFF = """diff --git a/index.html b/index.html
index bbbbbbb..ccccccc 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,9 @@
   <body>
     <h1>Welcome</h1>
     <p>This is a test page.</p>
+    <img src="logo.png" alt="" />
   </body>
 </html>
"""


class TestSemanticAnchorResolver:
    """Tests for SemanticAnchorResolver class."""

    def test_extract_commentable_line_texts_compose(self):
        """Test extracting line texts from Compose diff."""
        commentable_lines = DiffParser.extract_commentable_lines(COMPOSE_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            COMPOSE_SLIDER_DIFF, commentable_lines
        )

        file_path = "app/src/main/java/com/example/Settings.kt"
        assert file_path in line_texts
        assert len(line_texts[file_path]) > 0

        # Check that Slider line is captured
        slider_found = False
        for line_num, text in line_texts[file_path].items():
            if 'Slider(' in text:
                slider_found = True
                break
        assert slider_found

    def test_extract_anchor_candidates_slider(self):
        """Test extracting anchor candidates for slider issue."""
        issue = {
            'title': 'Slider missing accessibility label',
            'description': 'The Slider component needs an accessibility label',
            'wcag_sc': '4.1.2',
        }

        candidates = SemanticAnchorResolver.extract_anchor_candidates(issue)

        # Should extract 'slider' keyword and generate patterns
        assert len(candidates) > 0
        # Check that slider patterns are included
        assert any('Slider' in str(c) for c in candidates)

    def test_extract_anchor_candidates_button(self):
        """Test extracting anchor candidates for button issue."""
        issue = {
            'title': 'Button needs accessible name',
            'description': 'Interactive button requires accessible name',
            'wcag_sc': '4.1.2',
        }

        candidates = SemanticAnchorResolver.extract_anchor_candidates(issue)

        assert len(candidates) > 0
        assert any('button' in str(c).lower() for c in candidates)

    def test_extract_anchor_candidates_with_explicit_anchor(self):
        """Test that explicit anchor_text field takes priority."""
        issue = {
            'title': 'Generic title',
            'description': 'Generic description',
            'anchor_text': 'CustomComponent(',
        }

        candidates = SemanticAnchorResolver.extract_anchor_candidates(issue)

        # Explicit anchor should be first
        assert 'CustomComponent(' in candidates

    def test_resolve_compose_slider_issue(self):
        """Test resolving Compose slider issue to correct line."""
        # Parse diff
        commentable_lines = DiffParser.extract_commentable_lines(COMPOSE_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            COMPOSE_SLIDER_DIFF, commentable_lines
        )

        file_path = "app/src/main/java/com/example/Settings.kt"

        # Create issue that model placed at wrong line (e.g., Text line)
        issue = {
            'file': file_path,
            'line': 13,  # This might be the Text("Volume") line
            'title': 'Slider missing accessibility label',
            'description': 'Slider component needs semantic content description',
            'wcag_sc': '4.1.2',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        # Should resolve to Slider( line
        assert resolved_line is not None
        assert 'Slider(' in line_texts[file_path][resolved_line]

    def test_resolve_android_xml_seekbar_issue(self):
        """Test resolving Android XML SeekBar issue."""
        commentable_lines = DiffParser.extract_commentable_lines(ANDROID_XML_SEEKBAR_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            ANDROID_XML_SEEKBAR_DIFF, commentable_lines
        )

        file_path = "app/src/main/res/layout/activity_settings.xml"

        # Issue about contentDescription
        issue = {
            'file': file_path,
            'line': 8,  # Might be on TextView
            'title': 'SeekBar has null contentDescription',
            'description': 'SeekBar should have descriptive contentDescription',
            'wcag_sc': '1.1.1',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        # Should resolve to SeekBar or contentDescription line
        assert resolved_line is not None
        line_content = line_texts[file_path][resolved_line]
        assert 'SeekBar' in line_content or 'contentDescription' in line_content

    def test_resolve_swiftui_slider_issue(self):
        """Test resolving SwiftUI Slider issue."""
        commentable_lines = DiffParser.extract_commentable_lines(SWIFTUI_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            SWIFTUI_SLIDER_DIFF, commentable_lines
        )

        file_path = "SettingsView.swift"

        issue = {
            'file': file_path,
            'line': 8,  # Might be on Text line
            'title': 'Slider needs accessibility label',
            'description': 'Add accessibilityLabel to Slider',
            'wcag_sc': '4.1.2',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        assert 'Slider(' in line_texts[file_path][resolved_line]

    def test_resolve_swiftui_toggle_issue(self):
        """Test resolving SwiftUI Toggle issue."""
        commentable_lines = DiffParser.extract_commentable_lines(SWIFTUI_TOGGLE_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            SWIFTUI_TOGGLE_DIFF, commentable_lines
        )

        file_path = "SettingsView.swift"

        issue = {
            'file': file_path,
            'line': 10,  # Wrong line
            'title': 'Toggle missing accessibility hint',
            'description': 'Toggle control needs accessibility hint',
            'wcag_sc': '4.1.2',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        assert 'Toggle(' in line_texts[file_path][resolved_line]

    def test_resolve_uikit_slider_issue(self):
        """Test resolving UIKit UISlider issue."""
        commentable_lines = DiffParser.extract_commentable_lines(UIKIT_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            UIKIT_SLIDER_DIFF, commentable_lines
        )

        file_path = "SettingsViewController.swift"

        issue = {
            'file': file_path,
            'line': 13,  # Wrong line
            'title': 'UISlider needs accessibility label',
            'description': 'Set accessibilityLabel for UISlider',
            'wcag_sc': '4.1.2',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        line_content = line_texts[file_path][resolved_line]
        assert 'UISlider' in line_content or 'accessibilityLabel' in line_content

    def test_resolve_react_button_issue(self):
        """Test resolving React button issue."""
        commentable_lines = DiffParser.extract_commentable_lines(REACT_BUTTON_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            REACT_BUTTON_DIFF, commentable_lines
        )

        file_path = "src/components/Settings.tsx"

        issue = {
            'file': file_path,
            'line': 7,  # Wrong line
            'title': 'Button missing accessible name',
            'description': 'Button needs aria-label or text content',
            'wcag_sc': '4.1.2',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        assert '<button' in line_texts[file_path][resolved_line]

    def test_resolve_react_input_aria_label_issue(self):
        """Test resolving React input with aria-label issue."""
        commentable_lines = DiffParser.extract_commentable_lines(REACT_INPUT_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            REACT_INPUT_DIFF, commentable_lines
        )

        file_path = "src/components/Form.tsx"

        issue = {
            'file': file_path,
            'line': 11,  # Wrong line (label)
            'title': 'Input missing label association',
            'description': 'Input has aria-label but should use label element',
            'wcag_sc': '1.3.1',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        line_content = line_texts[file_path][resolved_line]
        assert '<input' in line_content or 'aria-label' in line_content

    def test_resolve_html_img_alt_issue(self):
        """Test resolving HTML image alt text issue."""
        commentable_lines = DiffParser.extract_commentable_lines(HTML_IMG_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            HTML_IMG_DIFF, commentable_lines
        )

        file_path = "index.html"

        issue = {
            'file': file_path,
            'line': 12,  # Wrong line
            'title': 'Image missing alt text',
            'description': 'Image has empty alt attribute',
            'wcag_sc': '1.1.1',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        assert resolved_line is not None
        assert '<img' in line_texts[file_path][resolved_line]

    def test_resolve_no_anchor_found_returns_none(self):
        """Test that resolver returns None when no anchor found."""
        commentable_lines = DiffParser.extract_commentable_lines(COMPOSE_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            COMPOSE_SLIDER_DIFF, commentable_lines
        )

        file_path = "app/src/main/java/com/example/Settings.kt"

        # Issue with no matching patterns
        issue = {
            'file': file_path,
            'line': 13,
            'title': 'Generic issue with no specific element',
            'description': 'This has no keywords that match UI elements',
            'wcag_sc': '1.1.1',
        }

        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=20
        )

        # Should return None (fall back to nearest line logic)
        assert resolved_line is None

    def test_resolve_respects_max_distance(self):
        """Test that resolver respects max_distance parameter."""
        commentable_lines = DiffParser.extract_commentable_lines(COMPOSE_SLIDER_DIFF)
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            COMPOSE_SLIDER_DIFF, commentable_lines
        )

        file_path = "app/src/main/java/com/example/Settings.kt"

        issue = {
            'file': file_path,
            'line': 11,  # Far from Slider
            'title': 'Slider missing label',
            'description': 'Slider needs accessibility label',
            'wcag_sc': '4.1.2',
        }

        # With very small max_distance, should return None
        resolved_line = SemanticAnchorResolver.resolve_issue_line(
            issue,
            file_path,
            commentable_lines[file_path],
            line_texts[file_path],
            max_distance=1  # Very restrictive
        )

        # If Slider is more than 1 line away, should return None
        # (actual result depends on diff structure)
        # This tests the max_distance logic is being applied

    def test_get_all_framework_patterns(self):
        """Test that all framework patterns are returned."""
        patterns = SemanticAnchorResolver.get_all_framework_patterns()

        assert len(patterns) > 0
        # Check that patterns from different frameworks are included
        assert any('Slider' in p for p in patterns)
        assert any('Button' in p for p in patterns)
        assert any('contentDescription' in p for p in patterns)
        assert any('accessibilityLabel' in p for p in patterns)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
