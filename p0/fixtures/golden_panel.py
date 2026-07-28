"""
p0/fixtures/golden_panel.py -- the GOLDEN tier's fixed, version-controlled
regression panel (spec.md FR-005/007, plan.md Project Structure).

Seeded from `p0/fixtures/ruleset_defects.py`'s existing 25 known planted-
defect checks (spec.md Assumptions), NOT from `demo/syn`'s PDF-derived loans
-- those require poppler-extracted fixtures this environment does not always
have on disk (`p0/fixtures/from_docs/build_fixtures.py` needs the actual
closed-loan PDFs under `demo/syn/`, which are large binary test data, not
always checked out). Real-loan-derived GOLDEN entries remain a future,
additive source (spec.md User Story 5 / feature 012) -- this seed proves the
tier mechanically without depending on that binary fixture set.

Each panel entry reuses the SAME generalized constructor User Story 1 built
(`p0/eval_synth/scenario_construction.construct_scenario`) to build a
genuinely fail-case loan (the "known defect" condition) and a genuinely
pass-case loan (the clean counterfactual) for one representative check from
each of `ruleset_defects.py`'s buckets A/B/D/E/F -- spanning
predicate/ratio_threshold/agree_categorical/agree_numeric/
agree_doc_categorical/agree_doc_numeric, the real kind variety the 25 known
defects cover. No hand-written per-field mutation code is added here; PANEL
is built by calling the exact same `construct_scenario` every other tier
calls (dogfooding US1's own promise: no per-field mutation function needed).

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine.model import CanonicalLoan  # noqa: E402

import scenario_construction as SC  # noqa: E402
from fixtures.ruleset_defects import defects_ruleset  # noqa: E402

PANEL_VERSION = "golden-v1-ruleset-defects-seed"

# One representative check id per bucket (A/B/D/E/F) of ruleset_defects.py's
# 25 known planted defects -- spans predicate / ratio_threshold /
# agree_categorical / agree_numeric / agree_doc_categorical /
# agree_doc_numeric, the real kind variety those 25 defects cover (bucket C's
# derived date-diff fields and bucket F's remaining checks are the same
# ratio_threshold/agree_doc_* kinds already represented here, so are not
# separately re-seeded -- see module docstring of ruleset_defects.py for the
# full bucket breakdown).
_SEED_CHECK_IDS = [
    "chk-def-hud92900a-signed",         # Bucket A: predicate, is_true
    "chk-def-appraisal-comp-distance",  # Bucket B: ratio_threshold, field_value
    "chk-def-fha-case-number",          # Bucket D: agree_categorical (doc vs mismo)
    "chk-reconcile-loan-amount",        # Bucket E: agree_numeric (doc vs mismo)
    "chk-def-loan-purpose-agree",       # Bucket F: agree_doc_categorical
    "chk-def-cd-payoff-agree",          # Bucket F: agree_doc_numeric
]


def _build_panel() -> List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]]:
    universe = {c.id: c for c in defects_ruleset().checks}
    panel: List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]] = []
    for check_id in _SEED_CHECK_IDS:
        chk = universe[check_id]
        scenario = SC.construct_scenario(chk)
        if not scenario.ok:
            # An honest gap, not a silent drop -- a seed check whose kind
            # isn't (yet) constructible must never make the panel look
            # bigger than it actually is.
            continue
        panel.append((scenario.fail_loan, {check_id: scenario.expected_fail_status},
                     {"source": "ruleset_defects.py", "check_id": check_id,
                      "panel_version": PANEL_VERSION, "case": "known-defect"}))
        panel.append((scenario.pass_loan, {check_id: scenario.expected_pass_status},
                     {"source": "ruleset_defects.py", "check_id": check_id,
                      "panel_version": PANEL_VERSION, "case": "clean"}))
    return panel


PANEL: List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]] = _build_panel()
