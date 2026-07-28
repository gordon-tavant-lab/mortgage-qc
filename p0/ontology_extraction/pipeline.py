"""
FR-008: sequences Layer 0 -> Layer 1 -> Layer 2 -- a row resolved by an
earlier layer is never reprocessed by a later one. FR-012 / Onity's coverage
circuit breaker: when Layer 0's coverage falls below the configured floor,
halt before Layer 1/2 expansion and surface that as a structured signal on
the result, rather than silently proceeding at full (expensive) scale.

This is the package's single public entry point (`run_layers`) -- callers
(mortgage-qc-prod's `002e`, or another project entirely) depend on this
module and the `PreconditionProposal`/`CoverageReport` shapes it returns,
not on the individual layer modules directly.

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Pattern

from ontology_extraction import layer0_clustering as L0
from ontology_extraction import layer1_extraction as L1
from ontology_extraction import layer2_grounded as L2
from ontology_extraction.layer0_clustering import CoverageReport, UnparsedDependency

# Derived from source_layer (spec.md Key Entities) -- `002e` uses this to
# decide auto-sign vs. mandatory review. Layer 2 is pinned to mandatory
# review by FR-007 regardless of anything else about the proposal.
TRUST_TIER_BY_LAYER = {
    0: "HIGH_AUTO_ELIGIBLE",
    1: "MEDIUM_SME_REVIEW",
    2: "MANDATORY_HUMAN_REVIEW",
}


@dataclass
class PreconditionCondition:
    field_name: str
    operator: str
    value: Any


@dataclass
class PreconditionProposal:
    row_id: str
    source_layer: int  # 0, 1, or 2
    condition: Optional[PreconditionCondition]
    provenance: Optional[str]
    trust_tier: str
    parse_failed: bool = False


@dataclass
class PipelineResult:
    proposals: List[PreconditionProposal] = field(default_factory=list)
    coverage: Optional[CoverageReport] = None
    unparsed: List[UnparsedDependency] = field(default_factory=list)
    halted_after_layer0: bool = False


def _layer0_proposals(cluster_result: L0.ClusterResult) -> List[PreconditionProposal]:
    proposals = []
    for row_id, pairs in sorted(cluster_result.resolved_row_dependencies.items()):
        by_key: Dict[str, List[str]] = {}
        for key, answer in pairs:
            by_key.setdefault(key, []).append(answer)
        for key, answers in sorted(by_key.items()):
            unique_answers = sorted(set(answers))
            condition = PreconditionCondition(
                field_name=f"question_{key}",
                operator="in" if len(unique_answers) > 1 else "==",
                value=unique_answers if len(unique_answers) > 1 else unique_answers[0],
            )
            proposals.append(PreconditionProposal(
                row_id=row_id, source_layer=0, condition=condition,
                provenance=f"ontology key {key}", trust_tier=TRUST_TIER_BY_LAYER[0],
            ))
    return proposals


def run_layers(
    rows: List[dict],
    layer1_client: Any = None,
    layer2_client: Any = None,
    corpus_lookup: Optional[Callable[[dict], Any]] = None,
    judge_verdicts_fn: Optional[Callable[[Any, dict], list]] = None,
    dependency_field: str = "question_criteria_by_q",
    pattern: Pattern = L0.DEFAULT_DEPENDENCY_PATTERN,
    coverage_floor: float = 0.0,
    layer1_max_retries: int = 2,
    layer2_max_retries: int = 2,
) -> PipelineResult:
    """FR-008: strict sequence, no row reprocessed once resolved.

    `layer1_client`/`layer2_client`: pass `None` to skip that layer entirely
    (e.g. Layer 0-only structural coverage measurement, spec.md SC-002/T020 --
    the exact use case this project's Phase 1 needs before spending real
    Bedrock cost on Layer 1/2). `corpus_lookup(row) -> KnowledgeBaseCorpus |
    None` supplies Layer 2's per-row signed KB.
    """
    cluster_result = L0.cluster(
        rows, dependency_field=dependency_field, pattern=pattern,
        coverage_floor=coverage_floor,
    )
    proposals = _layer0_proposals(cluster_result)

    if cluster_result.coverage.below_floor:
        # Onity's circuit-breaker precedent (Edge Cases): a rule source with
        # no matching structure gets a structured low-structure signal, not
        # a silent full-scale Layer 1/2 run.
        return PipelineResult(
            proposals=proposals, coverage=cluster_result.coverage,
            unparsed=cluster_result.unparsed, halted_after_layer0=True,
        )

    resolved_ids = set(cluster_result.resolved_row_dependencies.keys())
    remaining_rows = [r for r in rows if r["row_id"] not in resolved_ids]

    if layer1_client is not None:
        still_remaining = []
        for row in remaining_rows:
            result = L1.extract_row(layer1_client, row, max_retries=layer1_max_retries)
            if result.parse_failed:
                proposals.append(PreconditionProposal(
                    row_id=row["row_id"], source_layer=1, condition=None,
                    provenance=None, trust_tier=TRUST_TIER_BY_LAYER[1], parse_failed=True,
                ))
                continue
            if result.condition is not None:
                proposals.append(PreconditionProposal(
                    row_id=row["row_id"], source_layer=1,
                    condition=PreconditionCondition(
                        field_name=result.condition.field_name,
                        operator=result.condition.operator,
                        value=result.condition.value,
                    ),
                    provenance=result.quoted_span, trust_tier=TRUST_TIER_BY_LAYER[1],
                ))
                continue
            # FR-004: no confident extraction -- falls through to Layer 2,
            # not silently dropped.
            still_remaining.append(row)
        remaining_rows = still_remaining

    if layer2_client is not None and corpus_lookup is not None:
        for row in remaining_rows:
            corpus = corpus_lookup(row)
            if corpus is None:
                continue
            result = L2.propose(
                layer2_client, row, corpus, judge_verdicts_fn=judge_verdicts_fn,
                max_retries=layer2_max_retries,
            )
            if result.parse_failed:
                proposals.append(PreconditionProposal(
                    row_id=row["row_id"], source_layer=2, condition=None,
                    provenance=None, trust_tier=TRUST_TIER_BY_LAYER[2], parse_failed=True,
                ))
                continue
            if result.condition is not None and result.grounding_verified:
                proposals.append(PreconditionProposal(
                    row_id=row["row_id"], source_layer=2,
                    condition=PreconditionCondition(
                        field_name=result.condition.field_name,
                        operator=result.condition.operator,
                        value=result.condition.value,
                    ),
                    provenance=f"{result.kb_program} v{result.kb_version} §{result.cited_section_id}",
                    trust_tier=TRUST_TIER_BY_LAYER[2],
                ))
            # else: rejected (failed grounding, no supported proposal) --
            # the row compiles unconditionally, the documented safe default
            # (spec.md Edge Cases).

    return PipelineResult(
        proposals=proposals, coverage=cluster_result.coverage,
        unparsed=cluster_result.unparsed, halted_after_layer0=False,
    )
