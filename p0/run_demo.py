"""
End-to-end demo runner: run the golden loans through the signed ruleset, print
the result set the way the Output surface would (auto-clear vs exceptions vs
needs-review), and append each run to the cryptographically-chained audit log,
then verify the chain.

Run:  python run_demo.py
Python 3.9 compatible.
"""
from __future__ import annotations

from qc_engine import run, AuditLog
from fixtures.golden import golden_loans
from fixtures.ruleset_demo import demo_ruleset, SIGNED_AT


def main() -> None:
    rs = demo_ruleset()
    print(f"\nSigned ruleset {rs.ruleset_id} v{rs.version}  sha256={rs.sha256()[:16]}…")
    s = rs.signoff_summary()
    print(f"Sign-off: {s['rules_edited_by_sme']}/{s['rules_total']} rules "
          f"corrected by SME (unedited={s['rules_unedited']}, "
          f"mean edit-distance={s['mean_edit_distance']})")

    def _line(r):
        cite = ""
        if r.citation:
            cite = f"  [{r.citation['docName']} p.{r.citation['pageNum']}]"
        if r.inputs:
            detail = f"  inputs={r.inputs}"
        elif r.compared_value:
            detail = f"  value={r.compared_value}% (rounding={r.rounding})"
        else:
            detail = ""
        return f"      [{r.status:12}] {r.check_name} ({r.severity}){detail}{cite}"

    audit = AuditLog(":memory:")
    print("\n" + "=" * 72)
    for loan, _expected in golden_loans():
        res = run(loan, rs)
        rec = audit.append(res, signed_at=SIGNED_AT)
        verdict = "AUTO-CLEARED" if res.auto_cleared else "EXCEPTION"
        nr = len(res.needs_review)
        nflags = len(res.flags)
        tail = ""
        if res.auto_cleared and nflags:
            tail = f" (with {nflags} data-sync flag(s))"
        elif nr:
            tail = f", {nr} need review"
        print(f"\nLoan {loan.loan_id} ({loan.loan_type}) -> {verdict}{tail}")

        # Step 1 — reconcile (doc truth vs system). Flags are INFORMATIONAL:
        # the docs are truth, so a mismatch means "fix your system data", it
        # does NOT fail QC.
        flags = res.flags
        print(f"   STEP 1 · Reconcile (doc vs system): "
              + ("all match ✓" if not flags
                 else f"{len(flags)} flag(s) — system out of sync (informational)"))
        for r in flags:
            print(_line(r))

        # Step 2 — QC policy rules. THIS is the pass/fail test.
        qcf = res.qc_failures
        print(f"   STEP 2 · QC rules (pass/fail): "
              + ("all pass ✓" if not qcf else f"{len(qcf)} failure(s)"))
        for r in qcf:
            print(_line(r))

        # anything needing human review (e.g. low-confidence extraction)
        for r in res.needs_review:
            print(_line(r))
        print(f"   audit record: {rec[:16]}…")

    print("\n" + "=" * 72)
    print(f"Audit chain verified: {'YES ✓' if audit.verify_chain() else 'NO ✗'} "
          f"({len(audit.records())} immutable records)")
    audit.close()
    print()


if __name__ == "__main__":
    main()
