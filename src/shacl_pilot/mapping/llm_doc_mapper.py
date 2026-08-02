#!/usr/bin/env python3
"""
LLM document-name mapper: AMQ document name -> Touchless documentType.

WHY an LLM and not a hard-coded table: the AMQ workbook names ~112 documents in
auditor language ("Uniform Underwriting and Transmittal Summary"); a vendor labels
them in its own vocabulary ("URLA - Lender Loan Information"). Enumerating that
crosswalk by hand does not generalize to the next vendor.

WHY this is still compatible with Non-Negotiable #1 (determinism): the LLM runs at
CONFIGURATION time only. It emits a signed crosswalk artifact that an SME reviews;
the engine then reads the frozen artifact. The LLM is never in the evaluation path.
Same "compile, then run" pattern as the rule compiler.

CRITICAL DESIGN CONSTRAINT — the model must be able to say NO.
An absent document is the common case, not the exception: of 7 documents sampled from
the AMQ rules, ZERO had anything resembling them in Touchless's 54 types. A mapper
biased toward finding a match manufactures false "document present" answers, which
silently converts a real defect into a pass. NOT_CLASSIFIED is a first-class answer.
"""
import json, os, sys
import boto3

MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

SYSTEM = """You map a mortgage document name from a lender's audit questionnaire (AMQ) \
onto a document-classification label used by a document-processing vendor.

You are given:
- amq_document: the document name as the AMQ rule refers to it
- amq_context: the full AMQ exception text, so you can see how the document is used
- vendor_labels: the COMPLETE list of labels the vendor can emit

Return ONE JSON object:
{
  "verdict": "MATCH" | "NOT_CLASSIFIED" | "AMBIGUOUS",
  "vendor_label": "<exact string from vendor_labels, or null>",
  "alternates": ["<other plausible vendor_labels>"],
  "confidence": 0.0-1.0,
  "reasoning": "<one or two sentences>",
  "same_document_test": "<state plainly whether these are the SAME physical document, \
not merely related to the same topic>"
}

RULES — read carefully, these are the whole point:

1. NOT_CLASSIFIED is a CORRECT and COMMON answer. The vendor list is finite and does
   not cover every document a rule can name. If no label denotes the same physical
   document, return NOT_CLASSIFIED with vendor_label null. Do NOT stretch for a match.

2. MATCH means the SAME PHYSICAL DOCUMENT, not the same subject area.
   - "Uniform Underwriting and Transmittal Summary" (Form 1008) is NOT
     "Form 1004 Uniform Residential Appraisal" — both contain the word "Uniform",
     they are different documents.
   - "Single-Family Comparable Rent Schedule" (Form 1007) is NOT
     "Form 1040 - Schedule C" — both say "Schedule", different documents.
   - A word overlap is not evidence. Ask: would a post-closing auditor accept the
     vendor's document as satisfying the AMQ requirement? If not, NOT_CLASSIFIED.

3. AMBIGUOUS when the amq_document is under-specified ("VA Form", "IRS Form",
   "Certification") and you cannot tell which document is meant. Do not guess.

4. Government-program forms (HUD-*, VA forms, FHA-specific like the Amendatory Clause,
   NPMA-33) are frequently absent from a vendor's conventional-loan label set. Return
   NOT_CLASSIFIED rather than reaching for a superficially similar conventional doc.

5. confidence must reflect real uncertainty. Reserve >0.9 for cases where the names
   denote the same document beyond reasonable dispute.

6. Never invent a vendor_label. It must be copied exactly from vendor_labels or be null.
"""

def _client():
    return boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION","us-east-1"))

# ---- post-execution guardrails (docs/LLM-GUARDRAIL-POLICY.md §4) -------------
# Both were derived from MEASURED failures, not theory. On an adversarial near-miss
# suite the model scored 4/6; both failures were the same shape — it accepted a
# BROADER vendor category as satisfying a MORE SPECIFIC AMQ document:
#   "Verification Of Deposit"            -> "Verification Of Assets"   (wrong)
#   "Hazard Insurance Declaration Page"  -> "Hazard Insurance"         (questionable)
# Both scored 0.85 — the same confidence as two CORRECT judgment calls, so
# confidence alone cannot separate them.

# H1: the model's own hedging is a detectable signal of an unsafe match.
HEDGES = ("likely", "probably", "would typically", "typically", "generally",
          "may be", "might be", "presumably", "in most cases", "usually",
          "could be", "appears to be", "should be")

# H2: an extra qualifier makes the AMQ name narrower than the vendor label.
SPECIFICITY_MARKERS = ("final", "initial", "declaration page", "endorsement",
                       "supplement", "allonge", "deposit", "addendum", "rider",
                       "update", "amended", "corrected", "certified", "page")


def apply_guardrails(out, amq_document, vendor_labels):
    """Downgrade unsafe MATCHes to AMBIGUOUS. Never upgrades a verdict."""
    flags = []
    # Q2 — closed-set enforced in CODE, never trusting the prompt
    if out.get("vendor_label") and out["vendor_label"] not in vendor_labels:
        out["_rejected_label"] = out.pop("vendor_label")
        out.update(vendor_label=None, verdict="INVALID_LABEL")
        flags.append("Q2:invented_label")
        out["guardrail_flags"] = flags
        return out

    if out.get("verdict") == "MATCH":
        blob = " ".join(str(out.get(k, "")) for k in
                        ("reasoning", "same_document_test")).lower()
        # H1 hedge detection
        hits = [h for h in HEDGES if h in blob]
        if hits:
            out["verdict"] = "AMBIGUOUS"
            flags.append("H1:hedged(%s)" % ",".join(hits[:3]))
        # H2 specificity guard — AMQ name carries a qualifier the label lacks
        a, v = amq_document.lower(), str(out.get("vendor_label") or "").lower()
        narrower = [m for m in SPECIFICITY_MARKERS if m in a and m not in v]
        if narrower:
            out["verdict"] = "AMBIGUOUS"
            flags.append("H2:more_specific(%s)" % ",".join(narrower[:3]))

    # H3 — no auto-accept for document mapping; every MATCH needs SME sign-off
    if out.get("verdict") == "MATCH":
        out["requires_sme_signoff"] = True
        flags.append("H3:sme_signoff_required")

    out["guardrail_flags"] = flags
    return out


def map_document(amq_document, amq_context, vendor_labels, client=None, model=MODEL,
                 apply_guards=True):
    client = client or _client()
    vendor_labels = sorted(vendor_labels)
    user = json.dumps({
        "amq_document": amq_document,
        "amq_context": amq_context,
        "vendor_labels": vendor_labels,
    }, indent=2)
    resp = client.converse(
        modelId=model,
        system=[{"text": SYSTEM}],
        messages=[{"role":"user","content":[{"text":user}]}],
        inferenceConfig={"maxTokens":900,"temperature":0.0},  # P2
    )
    txt = resp["output"]["message"]["content"][0]["text"]
    s,e = txt.find("{"), txt.rfind("}")
    out = json.loads(txt[s:e+1])                              # Q1
    out["_model_id"] = model                                  # Q9 provenance
    out["_llm_verdict"] = out.get("verdict")                  # keep pre-guardrail value
    if apply_guards:
        out = apply_guardrails(out, amq_document, vendor_labels)
    return out

if __name__ == "__main__":
    labels = json.load(open(sys.argv[1]))
    for name, ctx in json.load(open(sys.argv[2])):
        r = map_document(name, ctx, labels)
        print(json.dumps({"amq_document":name, **r}))
