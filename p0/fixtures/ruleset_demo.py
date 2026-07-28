"""
Builds the demo signed ruleset, modeling the compile -> correct -> sign loop.

Each rule carries provenance: what the LLM drafted vs what the SME signed, with
the edit-distance computed automatically. Some rules are signed UNCHANGED (the
LLM got it right); others are CORRECTED by the SME (e.g. tightening a tolerance,
fixing a misread threshold) — exactly the human-in-the-loop the judge demanded
(ruling #2). The demo surfaces unedited-rule count as the sign-off-theater smell.

Python 3.9 compatible.
"""
from __future__ import annotations

from qc_engine.ruleset import Ruleset, Check, RuleProvenance

SIGNER = "kayla.sme@lender.example"
SIGNED_AT = "2026-06-26T15:00:00Z"  # injected, not wall-clock


def demo_ruleset() -> Ruleset:
    checks = [
        Check(id="chk-borrower-name", name="Borrower name agreement",
              field_name="borrower_name", kind="agree_categorical",
              severity="CRITICAL", sources=["doc", "los", "mismo"],
              normalizer="name",
              message_fail="Borrower name disparity across sources."),
        Check(id="chk-borrower-ssn", name="Borrower SSN (last 4) agreement",
              field_name="borrower_ssn", kind="agree_categorical",
              severity="CRITICAL", sources=["doc", "los", "mismo"],
              normalizer="ssn_last4",
              message_fail="SSN last-4 mismatch across sources."),
        Check(id="chk-note-rate", name="Note rate agreement",
              field_name="note_rate", kind="agree_numeric",
              severity="CRITICAL", sources=["doc", "los", "mismo"],
              tolerance="0.001",
              message_fail="Note rate differs beyond tolerance."),
        Check(id="chk-principal", name="Principal amount agreement",
              field_name="loan_amount", kind="agree_numeric",
              severity="CRITICAL", sources=["doc", "los", "mismo"],
              tolerance="0.00",
              message_fail="Principal amount mismatch."),
        Check(id="chk-property-address", name="Subject address agreement",
              field_name="property_address", kind="agree_categorical",
              severity="WARNING", sources=["doc", "los", "mismo"],
              normalizer="address",
              message_fail="Subject address disparity across sources."),
        Check(id="chk-flood-zone", name="Flood zone agreement",
              field_name="flood_zone", kind="agree_categorical",
              severity="CRITICAL", sources=["doc", "los"],
              normalizer="flood_zone",
              message_fail="FEMA flood zone conflict (doc vs system)."),
        Check(id="chk-note-signed", name="Promissory note signed",
              field_name="note_signed", kind="predicate", predicate="is_true",
              severity="CRITICAL", sources=["doc"],
              message_fail="Promissory note is unsigned."),
        Check(id="chk-ltv-max", name="LTV within program max (95%)",
              field_name="", kind="ratio_threshold", ratio="ltv",
              severity="CRITICAL", threshold="95.000", operator="<=",
              message_fail="LTV exceeds program maximum of 95%."),
    ]

    # Provenance: model real human corrections. Most match the LLM draft;
    # two were CORRECTED by the SME (rate tolerance tightened; LTV threshold
    # fixed from a misread 97 to 95). Edit-distance is computed in __post_init__.
    prov = [
        RuleProvenance("chk-borrower-name",
            "all sources agree on borrower name after normalization",
            "all sources agree on borrower name after normalization",
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-borrower-ssn",
            "compare full SSN across sources",
            "compare SSN last-4 across sources (doc is masked)",  # SME correction
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-note-rate",
            "note rate must match within 0.01",
            "note rate must match within 0.001",  # SME tightened tolerance
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-principal",
            "principal amount must match exactly",
            "principal amount must match exactly",
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-property-address",
            "subject address must agree across sources",
            "subject address must agree across sources",
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-flood-zone",
            "flood zone doc vs system must agree",
            "flood zone doc vs system must agree",
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-note-signed",
            "promissory note must be signed by primary borrower",
            "promissory note must be signed by primary borrower",
            SIGNER, SIGNED_AT),
        RuleProvenance("chk-ltv-max",
            "LTV must be at or below 97%",
            "LTV must be at or below 95%",  # SME corrected misread threshold
            SIGNER, SIGNED_AT),
    ]
    return Ruleset(ruleset_id="rs-conv-purchase", version=1,
                   checks=checks, provenance=prov)
