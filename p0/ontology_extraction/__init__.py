"""
002f: the precondition ontology layer -- a standalone, domain-agnostic
package for sourcing a rule row's loan-fact (or, more generally, record-fact)
applicability precondition, in three layers of increasing cost and decreasing
trust:

  Layer 0 (layer0_clustering.py)  -- deterministic cross-reference-column
    clustering, zero LLM, zero network.
  Layer 1 (layer1_extraction.py)  -- source-text extraction with explicit
    deontic-modality + cross-reference-target classification (LLM, compile
    time only).
  Layer 2 (layer2_grounded.py)    -- KB-retrieval + automated grounding
    verification + mandatory human sign-off (reuses `002c`'s
    knowledge_base.py/judge_panel.py).

`pipeline.run_layers()` sequences all three per FR-008: a row resolved by an
earlier layer is never reprocessed by a later one.

FR-009 (enforced by `p0/tests/test_ontology_reusability.py`): this package
has zero imports from `p0.qc_engine`. Its public interface is plain
dicts/dataclasses in, plain dicts/dataclasses out -- `002e` is the sole
mortgage-qc-prod-specific consumer, translating this package's output into
`Check.applies_if`.

Python 3.9 compatible.
"""
