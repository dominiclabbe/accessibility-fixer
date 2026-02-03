"""
Accessibility Guide Loader

Loads and combines accessibility guides for AI context.
"""

import os
from pathlib import Path
from typing import List, Optional


class GuideLoader:
    """Loads accessibility guides from the guides directory."""

    def __init__(self, guides_dir: Optional[str] = None):
        """
        Initialize guide loader.

        Args:
            guides_dir: Path to guides directory (defaults to ../guides from this file)
        """
        if guides_dir:
            self.guides_dir = Path(guides_dir)
        else:
            # Default to guides/ directory in project root
            self.guides_dir = Path(__file__).parent.parent / "guides"

    def load_all_guides(self) -> str:
        """
        Load all accessibility guides and combine into single string.

        Returns:
            Combined guide content as string
        """
        guides = []

        # Load main guides
        main_guides = [
            "COMMON_ISSUES.md",
            "GUIDE_WCAG_REFERENCE.md",
            "COMPREHENSIVE_AUDIT_WORKFLOW.md",
            "CODE_REFERENCES_AND_SCREENSHOTS.md",
        ]

        for guide_file in main_guides:
            guide_path = self.guides_dir / guide_file
            if guide_path.exists():
                guides.append(f"\n\n# {guide_file}\n\n{guide_path.read_text()}")

        # Load platform-specific guides
        platform_guides = [
            "GUIDE_ANDROID.md",
            "GUIDE_IOS.md",
            "GUIDE_WEB.md",
            "GUIDE_REACT_NATIVE.md",
            "GUIDE_FLUTTER.md",
            "GUIDE_ANDROID_TV.md",
            "GUIDE_TVOS.md",
        ]

        for guide_file in platform_guides:
            guide_path = self.guides_dir / guide_file
            if guide_path.exists():
                guides.append(f"\n\n# {guide_file}\n\n{guide_path.read_text()}")

        # Load WCAG principle guides
        wcag_dir = self.guides_dir / "wcag"
        if wcag_dir.exists():
            for wcag_file in wcag_dir.glob("*.md"):
                guides.append(f"\n\n# wcag/{wcag_file.name}\n\n{wcag_file.read_text()}")

        # Load pattern guides
        patterns_dir = self.guides_dir / "patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                guides.append(
                    f"\n\n# patterns/{pattern_file.name}\n\n{pattern_file.read_text()}"
                )

        return "\n".join(guides)

    def load_platform_specific_guides(self, platforms: List[str]) -> str:
        """
        Load guides for specific platforms only.

        Args:
            platforms: List of platforms (e.g., ['android', 'ios', 'web'])

        Returns:
            Combined guide content
        """
        guides = []

        # Always include common guides
        common_guides = [
            "COMMON_ISSUES.md",
            "GUIDE_WCAG_REFERENCE.md",
        ]

        for guide_file in common_guides:
            guide_path = self.guides_dir / guide_file
            if guide_path.exists():
                guides.append(f"\n\n# {guide_file}\n\n{guide_path.read_text()}")

        # Load platform-specific guides
        platform_map = {
            "android": ["GUIDE_ANDROID.md", "GUIDE_ANDROID_TV.md"],
            "ios": ["GUIDE_IOS.md", "GUIDE_TVOS.md"],
            "web": ["GUIDE_WEB.md", "GUIDE_REACT_NATIVE.md"],
            "flutter": ["GUIDE_FLUTTER.md"],
            "react-native": ["GUIDE_REACT_NATIVE.md"],
        }

        for platform in platforms:
            platform_lower = platform.lower()
            if platform_lower in platform_map:
                for guide_file in platform_map[platform_lower]:
                    guide_path = self.guides_dir / guide_file
                    if guide_path.exists():
                        guides.append(f"\n\n# {guide_file}\n\n{guide_path.read_text()}")

        # Always include WCAG guides
        wcag_dir = self.guides_dir / "wcag"
        if wcag_dir.exists():
            for wcag_file in wcag_dir.glob("*.md"):
                guides.append(f"\n\n# wcag/{wcag_file.name}\n\n{wcag_file.read_text()}")

        # Include pattern guides
        patterns_dir = self.guides_dir / "patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                guides.append(
                    f"\n\n# patterns/{pattern_file.name}\n\n{pattern_file.read_text()}"
                )

        return "\n".join(guides)

    def detect_platforms_from_files(self, files: List[str]) -> List[str]:
        """
        Detect platforms based on file extensions.

        Args:
            files: List of file paths

        Returns:
            List of detected platforms
        """
        platforms = set()

        for file_path in files:
            ext = Path(file_path).suffix.lower()

            # Android
            if ext in [".kt", ".java"] and "android" in file_path.lower():
                platforms.add("android")

            # iOS
            if ext == ".swift" and "ios" in file_path.lower():
                platforms.add("ios")

            # Web
            if ext in [".tsx", ".jsx", ".ts", ".js", ".html", ".css"]:
                # Check if React Native or Web
                if "react-native" in file_path.lower() or "mobile" in file_path.lower():
                    platforms.add("react-native")
                else:
                    platforms.add("web")

            # Flutter
            if ext == ".dart":
                platforms.add("flutter")

        return list(platforms) if platforms else ["web"]  # Default to web


def load_guides_for_pr(changed_files: List[str]) -> str:
    """
    Load relevant guides for a PR based on changed files.

    Args:
        changed_files: List of changed file paths

    Returns:
        Combined guide content
    """
    loader = GuideLoader()
    platforms = loader.detect_platforms_from_files(changed_files)
    return loader.load_platform_specific_guides(platforms)
