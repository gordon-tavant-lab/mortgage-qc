# Criteria: 014 Decision Narrative

Executable, not prose — each maps directly to spec.md's Success Criteria.

## SC-001 — 5/5 loans produce a validated narrative

```bash
python3 p0/compile_runs/run_014_decision_narratives/generate_and_check.py
# expect: "5/5 narratives generated and validated" in stdout; exit 0
```

## SC-002 — Narrative claims match the real result (no invented, no dropped)

For each loan, assert programmatically (not just by eye):
```python
narrative = result["decision_narrative"]
assert set(narrative["referenced_check_ids"]) <= {r["check_id"] for r in real_exceptions}
assert set(result["review_reasons"]) <= narrative_mentions_all_reason_tags(narrative["narrative_text"])
```

## SC-003 — Fabrication is actually rejected

```python
fake_run_result = ...  # real loan's RunResult
fake_narrative_text = "... references check-id-that-does-not-exist-12345 ..."
with pytest.raises(ValidationError):
    decision_narrative._validate(fake_run_result, fake_narrative_text)
```

## SC-004 — Zero regressions

```bash
pytest p0/tests -v
# expect: 0 failed
```

## SC-005 — Cost is visible, not folded into "$0"

```python
log_events = read_events(eval_log_path)
cost_events = [e for e in log_events if e["stage"] == "cost"]
assert any(e["details"]["llm_calls"] > 0 for e in cost_events)  # narrative generation shows up
```

## SC-006 — Narrative is grounded in the real Guide, not just the run result

```python
vocab = FactVocabulary.load_latest()  # signed
for loan_result in real_results:
    narrative = loan_result["decision_narrative"]
    facts_touched = facts_for_run_result(loan_result, vocab)
    real_citations = {c for f in facts_touched.values() for c in f.guide_citations}
    # every guide citation the narrative claims must be real
    assert set(narrative["referenced_guide_citations"]) <= real_citations
    # every fact that HAS a real citation must actually be cited somewhere in the text
    for fact in facts_touched.values():
        if fact.guide_citations:
            assert any(c in narrative["narrative_text"] for c in fact.guide_citations)

# constructed-fabrication check, mirroring SC-003's shape
fake_narrative_text = "... per Fannie Mae Selling Guide B9-9.9-99, a section that does not exist ..."
with pytest.raises(ValidationError):
    decision_narrative._validate(real_run_result, vocab, fake_narrative_text)
```
