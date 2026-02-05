"""
SARIF Generator

Generates SARIF (Static Analysis Results Interchange Format) output
for accessibility findings.

SARIF format: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class SARIFGenerator:
    """Generates SARIF reports from accessibility issues."""

    TOOL_NAME = "accessibility-fixer"
    TOOL_VERSION = "1.0.0"
    TOOL_URI = "https://github.com/dominiclabbe/accessibility-fixer"

    # Map severity levels to SARIF levels
    SEVERITY_MAP = {
        "Critical": "error",
        "High": "error",
        "Medium": "warning",
        "Low": "note",
    }

    @staticmethod
    def generate_sarif(
        issues: List[Dict],
        repo_uri: Optional[str] = None,
        repo_ref: Optional[str] = None,
    ) -> Dict:
        """
        Generate SARIF report from accessibility issues.

        Args:
            issues: List of accessibility issues
            repo_uri: Repository URI (e.g., https://github.com/owner/repo)
            repo_ref: Git ref (e.g., commit SHA or branch name)

        Returns:
            SARIF report as dict
        """
        # Build SARIF structure
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": SARIFGenerator.TOOL_NAME,
                            "version": SARIFGenerator.TOOL_VERSION,
                            "informationUri": SARIFGenerator.TOOL_URI,
                            "rules": SARIFGenerator._generate_rules(issues),
                        }
                    },
                    "results": SARIFGenerator._generate_results(issues),
                }
            ],
        }

        # Add version control provenance if provided
        if repo_uri or repo_ref:
            sarif["runs"][0]["versionControlProvenance"] = []
            if repo_uri:
                provenance = {"repositoryUri": repo_uri}
                if repo_ref:
                    provenance["revisionId"] = repo_ref
                sarif["runs"][0]["versionControlProvenance"].append(provenance)

        return sarif

    @staticmethod
    def _generate_rules(issues: List[Dict]) -> List[Dict]:
        """
        Generate SARIF rules from unique WCAG Success Criteria in issues.

        Args:
            issues: List of accessibility issues

        Returns:
            List of SARIF rule objects
        """
        # Collect unique WCAG SCs
        wcag_scs = set()
        for issue in issues:
            wcag_sc = issue.get("wcag_sc", "")
            if wcag_sc:
                wcag_scs.add(wcag_sc)

        # Generate rules
        rules = []
        for wcag_sc in sorted(wcag_scs):
            rule_id = SARIFGenerator._make_rule_id(wcag_sc)
            rules.append({
                "id": rule_id,
                "name": f"WCAG {wcag_sc}",
                "shortDescription": {
                    "text": f"WCAG Success Criterion {wcag_sc}"
                },
                "fullDescription": {
                    "text": f"Accessibility issue related to WCAG {wcag_sc}"
                },
                "helpUri": f"https://www.w3.org/WAI/WCAG22/Understanding/{wcag_sc.replace('.', '-').lower()}.html",
                "properties": {
                    "tags": ["accessibility", "wcag"],
                },
            })

        # Add a generic rule for issues without WCAG SC
        rules.append({
            "id": "accessibility-generic",
            "name": "Generic Accessibility Issue",
            "shortDescription": {
                "text": "General accessibility concern"
            },
            "fullDescription": {
                "text": "Accessibility issue not mapped to a specific WCAG Success Criterion"
            },
            "properties": {
                "tags": ["accessibility"],
            },
        })

        return rules

    @staticmethod
    def _generate_results(issues: List[Dict]) -> List[Dict]:
        """
        Generate SARIF results from accessibility issues.

        Args:
            issues: List of accessibility issues

        Returns:
            List of SARIF result objects
        """
        results = []

        for issue in issues:
            # Extract fields
            file_path = issue.get("file", "")
            line = issue.get("line", 1)
            severity = issue.get("severity", "Medium")
            wcag_sc = issue.get("wcag_sc", "")
            wcag_level = issue.get("wcag_level", "")
            title = issue.get("title", "Accessibility Issue")
            description = issue.get("description", "")
            impact = issue.get("impact", "")
            suggested_fix = issue.get("suggested_fix", "")

            # Build message
            message_parts = []
            if description:
                message_parts.append(description)
            if impact:
                message_parts.append(f"Impact: {impact}")
            if suggested_fix:
                message_parts.append(f"Suggested fix: {suggested_fix}")

            message_text = "\n\n".join(message_parts) if message_parts else title

            # Determine rule ID
            rule_id = SARIFGenerator._make_rule_id(wcag_sc) if wcag_sc else "accessibility-generic"

            # Map severity
            sarif_level = SARIFGenerator.SEVERITY_MAP.get(severity, "warning")

            # Build result
            result = {
                "ruleId": rule_id,
                "level": sarif_level,
                "message": {
                    "text": message_text
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_path,
                            },
                            "region": {
                                "startLine": line,
                            },
                        }
                    }
                ],
            }

            # Add properties
            properties = {
                "severity": severity,
                "title": title,
            }
            if wcag_sc:
                properties["wcag_sc"] = wcag_sc
            if wcag_level:
                properties["wcag_level"] = wcag_level

            result["properties"] = properties

            results.append(result)

        return results

    @staticmethod
    def _make_rule_id(wcag_sc: str) -> str:
        """
        Make a SARIF rule ID from WCAG SC.

        Args:
            wcag_sc: WCAG SC string (e.g., "1.1.1", "2.4.6; 3.3.2")

        Returns:
            Rule ID string
        """
        # Handle multiple SCs separated by ';'
        if ";" in wcag_sc:
            # Use first SC
            wcag_sc = wcag_sc.split(";")[0].strip()

        # Clean and format
        cleaned = wcag_sc.replace(".", "-").replace(" ", "")
        return f"wcag-{cleaned}"

    @staticmethod
    def write_sarif_file(sarif: Dict, output_path: str) -> bool:
        """
        Write SARIF report to file.

        Args:
            sarif: SARIF report dict
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open('w') as f:
                json.dump(sarif, f, indent=2)

            print(f"✅ SARIF report written to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error writing SARIF file: {e}")
            return False


def generate_and_write_sarif(
    issues: List[Dict],
    output_path: str,
    repo_uri: Optional[str] = None,
    repo_ref: Optional[str] = None,
) -> bool:
    """
    Generate SARIF report and write to file (convenience function).

    Args:
        issues: List of accessibility issues
        output_path: Output file path
        repo_uri: Repository URI (optional)
        repo_ref: Git ref (optional)

    Returns:
        True if successful, False otherwise
    """
    generator = SARIFGenerator()
    sarif = generator.generate_sarif(issues, repo_uri, repo_ref)
    return generator.write_sarif_file(sarif, output_path)
