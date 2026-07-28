"""
YAML Rules Executor — Deterministic, single-tier evaluation.

Loads YAML rules, evaluates conditions against loan data, produces dispositions.
No LLM at runtime — all decisions pre-compiled to YAML, executed deterministically.

Python 3.9 compatible.
"""
from __future__ import annotations

import yaml
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class RuleResult:
    """Result of evaluating one rule against a loan."""
    rule_id: str
    program: str
    title: str
    verdict: str  # PASS, FAIL, WARNING
    action: str   # AUTO_CLEAR, FLAG_FOR_REVIEW
    reason_tags: List[str] = field(default_factory=list)
    citation: Optional[Dict[str, Any]] = None


@dataclass
class LoanDisposition:
    """Final QC disposition for a loan."""
    loan_id: str
    status: str  # AUTO_CLEARED, NEEDS_REVIEW
    review_reasons: List[str]  # Aggregated reason tags
    passed_rules: int
    failed_rules: int
    flagged_rules: int
    details: List[RuleResult]


class YAMLRulesExecutor:
    """Loads and executes YAML rules against loan data."""

    def __init__(self, rules_dir: str):
        """Load all YAML rules from directory."""
        self.rules: List[Dict[str, Any]] = []
        self.rules_by_program: Dict[str, List[Dict[str, Any]]] = {}
        self._load_rules(rules_dir)

    def _load_rules(self, rules_dir: str) -> None:
        """Scan directory, load all *.yaml files."""
        import os
        for root, dirs, files in os.walk(rules_dir):
            for file in files:
                if file.endswith(".yaml"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r") as f:
                            rule = yaml.safe_load(f)
                            self.rules.append(rule)
                            program = rule.get("metadata", {}).get("program", "unknown")
                            if program not in self.rules_by_program:
                                self.rules_by_program[program] = []
                            self.rules_by_program[program].append(rule)
                    except Exception as e:
                        print(f"Failed to load {path}: {e}")

    def evaluate_loan(self, loan_id: str, loan_data: Dict[str, Any], program: Optional[str] = None) -> LoanDisposition:
        """
        Evaluate all rules against a loan.

        Args:
            loan_id: Loan identifier (e.g., "loan 01")
            loan_data: Loan data (extracted fields + MISMO + LOS)
            program: Filter by program (FHA, VA, USDA, Fannie Mae) or None for all

        Returns:
            LoanDisposition with status, reasons, and details
        """
        rules_to_eval = self.rules
        if program:
            rules_to_eval = self.rules_by_program.get(program, [])

        results: List[RuleResult] = []
        passed = 0
        failed = 0
        flagged = 0
        reason_tags: List[str] = []

        for rule in rules_to_eval:
            result = self._evaluate_rule(rule, loan_data)
            if result:
                results.append(result)
                if result.verdict == "PASS":
                    passed += 1
                elif result.verdict == "FAIL":
                    failed += 1
                    reason_tags.extend(result.reason_tags)
                    flagged += 1
                elif result.verdict == "WARNING":
                    flagged += 1
                    reason_tags.extend(result.reason_tags)

        # Determine final disposition
        status = "AUTO_CLEARED" if (failed == 0 and flagged == 0) else "NEEDS_REVIEW"

        # Deduplicate reason tags
        reason_tags = list(set(reason_tags))

        return LoanDisposition(
            loan_id=loan_id,
            status=status,
            review_reasons=reason_tags,
            passed_rules=passed,
            failed_rules=failed,
            flagged_rules=flagged,
            details=results,
        )

    def _evaluate_rule(self, rule: Dict[str, Any], loan_data: Dict[str, Any]) -> Optional[RuleResult]:
        """Evaluate one rule against loan data."""
        try:
            metadata = rule.get("metadata", {})
            rule_def = rule.get("rule", {})

            rule_id = metadata.get("rule_id", "unknown")
            program = metadata.get("program", "unknown")
            title = rule_def.get("title", rule_id)
            verdict = rule_def.get("verdict", "PASS")
            action = rule_def.get("action", "AUTO_CLEAR")
            reason_tags = rule_def.get("reason_tags", [])
            citation = rule_def.get("citation")

            # For now, stub evaluation: rules are marked as PASS by default
            # In real implementation, parse condition and evaluate against loan_data
            # Example: condition = "appraisal_value < (purchase_price * 0.80)"
            # Real evaluation would parse this and check loan_data fields

            return RuleResult(
                rule_id=rule_id,
                program=program,
                title=title,
                verdict=verdict,
                action=action,
                reason_tags=reason_tags,
                citation=citation,
            )
        except Exception as e:
            print(f"Error evaluating rule {rule.get('metadata', {}).get('rule_id')}: {e}")
            return None

    def to_json(self, disposition: LoanDisposition) -> str:
        """Serialize disposition to JSON."""
        return json.dumps(
            {
                "loan_id": disposition.loan_id,
                "status": disposition.status,
                "review_reasons": disposition.review_reasons,
                "metrics": {
                    "passed_rules": disposition.passed_rules,
                    "failed_rules": disposition.failed_rules,
                    "flagged_rules": disposition.flagged_rules,
                },
            },
            indent=2,
        )
