#!/usr/bin/env python3
"""
Run the FULL compiled AMQ ruleset (4,166 rules) against a Touchless loan.

Honest by construction. Every rule lands in exactly one bucket:
  FAIL            - executable, fired, defect found
  PASS            - executable, all inputs present, did not fire
  NOT_APPLICABLE  - agency/program/feature gate excludes it for this loan
  NO_DATA         - executable but a required input is missing
  NOT_COMPILED    - no executable logic exists yet (eval_class=unmapped)

NOT_COMPILED is reported, never hidden: 97% of the workbook is in this state and
calling those "pass" would be the same false-clean bug as SHACL conforms=True.
"""
import glob, json, re, sys, collections
from rdflib import Graph, Namespace
from pyshacl import validate

LI  = Namespace("http://mortgage.audit.ontology/loan-instance#")
SH  = Namespace("http://www.w3.org/ns/shacl#")
CARO= Namespace("http://mortgage.audit.ontology/caro#")
REPO="/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/"

# doc_presence eval_target -> the doc_present_* fact built by touchless_to_amq.py
TARGET_TO_FACT = {
    "final_1003":       "doc_present_1003",
    "credit_report":    "doc_present_credit_report",
    "paystub":          "doc_present_paystub",
    "voe":              "doc_present_voe",
    "bank_statement":   "doc_present_bank_statement",
    "gift_letter":      "doc_present_gift_letter",
    "appraisal":        "doc_present_appraisal",
    "title_commitment": "doc_present_title_commitment",
    "closing_disclosure":"doc_present_closing_disclosure",
    "va_nov":           "doc_present_va_nov",
    "va_coe":           "doc_present_va_coe",
}
# --- AMQ program taxonomy (authoritative; Gordon, 2026-07-30) ---------------
# There are exactly FIVE loan programs, and ONLY a Question Code of the form
# "O-<TOKEN>-<n>" carries one. See docs/AMQ-PROGRAM-TAXONOMY.md.
#
# The five programs (4,932 of 5,520 Post-Closing rows, 89.3%):
#   O-FNM Fannie Mae | O-FRD Freddie Mac  -> CONVENTIONAL
#   O-FHA FHA | O-VA VA | O-RHS USDA/Rural Housing -> GOVERNMENT
#
# Eight other tokens also appear in the O-<TOKEN>- position but are NOT programs.
# They are regulatory / best-practice bodies and apply to EVERY loan regardless of
# program: FED, CNTL, EPD, BP, CFPB, HMDA, IRS, UDAAP (305 rows). Gating on these
# would silently drop TILA/HMDA/UDAAP checks from every audit.
#
# Anything whose Question Code does not start with "O-" (283 rows: SONYMA,
# Portfolio, Overlay, DUValid, AUS Findings, COVID19-*, ...) is an investor overlay
# or lender-specific check, NOT a program gate — it applies to all loans.
PROGRAMS = {
    "FNM": "CONVENTIONAL",
    "FRD": "CONVENTIONAL",
    "FHA": "FHA",
    "VA":  "VA",
    "RHS": "USDA",
}
# Present in the O-<TOKEN>- slot but explicitly NOT programs — never gate on these.
NON_PROGRAM_O_TOKENS = {"FED", "CNTL", "EPD", "BP", "CFPB", "HMDA", "IRS", "UDAAP"}


def program_token_of(rule):
    """Program token from an O-<TOKEN>-<n> Question Code, else None.

    Returns None for regulatory tokens and for any non-"O-" code, so callers
    treat those as universally applicable rather than program-gated.
    """
    m = re.match(r"^O-([A-Za-z0-9]+)-", str(rule.get("question_code") or ""))
    if not m:
        return None
    tok = m.group(1).upper()
    return tok if tok in PROGRAMS else None


def is_excluded_by_program(rule, loan_program):
    """True only when the rule belongs to a program the loan is not.

    CONVENTIONAL rules (FNM/FRD) apply to a conventional loan; FHA/VA/USDA rules
    are mutually exclusive with it.
    """
    tok = program_token_of(rule)
    if tok is None:
        return None            # not program-gated -> always applies
    required = PROGRAMS[tok]
    return None if required == loan_program else required

def load_loan(ttl):
    g=Graph().parse(ttl,format="turtle")
    facts={}
    for s,p,o in g:
        n=str(p).split("#")[-1]
        if n.startswith("cite_"): continue
        v=str(o)
        if v in ("true","false"): v = (v=="true")
        facts.setdefault(n,v)
    return g,facts

def run_shapes(data):
    shapes=Graph()
    for f in sorted(glob.glob(REPO+"src/shacl_pilot/blocks/*.ttl")):
        if "touchless" in f: continue
        shapes.parse(f,format="turtle")
    _,rep,_=validate(data_graph=data,shacl_graph=shapes,inference="none",advanced=True)
    fired={}
    for r in rep.subjects(SH.resultSeverity,None):
        nm=str(rep.value(r,SH.sourceShape)).split("#")[-1]
        fired.setdefault(nm,[]).append(str(rep.value(r,SH.resultMessage)))
    # per-shape required predicates, from the SPARQL body (citesFields is unreliable)
    need={}
    for f in sorted(glob.glob(REPO+"src/shacl_pilot/blocks/*.ttl")):
        if "touchless" in f: continue
        g=Graph().parse(f,format="turtle")
        for s in g.subjects(SH.targetClass,None):
            body="".join(str(g.value(c,SH.select) or "") for c in g.objects(s,SH.sparql))
            preds=set(re.findall(r"li:([A-Za-z_][A-Za-z_0-9]*)",body))
            preds-={"cite_row","doc_name","page","document_id","snippet"}
            need[str(s).split("#")[-1]]=(preds,body)
    return fired,need

def main(loan_ttl, ruleset_path):
    data,facts=load_loan(loan_ttl)
    rules=json.load(open(ruleset_path))["rules"]
    fired,need=run_shapes(data)

    program=str(facts.get("mismo_mortgage_type","")).upper()
    amort=str(facts.get("mismo_amortization_type",""))
    has_co="co_borrower_name" in facts

    R=collections.defaultdict(list)
    for r in rules:
        ec, tgt = r["eval_class"], r.get("eval_target")
        # program gate from the O-<TOKEN>- Question Code; applies compiled or not
        req=is_excluded_by_program(r, program)
        if req:
            R["NOT_APPLICABLE"].append((r,"%s-only (loan is %s)"%(req,program or "?"))); continue
        if ec=="doc_presence" and tgt in TARGET_TO_FACT:
            fact=TARGET_TO_FACT[tgt]
            if fact not in facts: R["NO_DATA"].append((r,"no fact %s"%fact))
            elif facts[fact] is True: R["PASS"].append((r,"%s present"%tgt))
            else: R["FAIL"].append((r,"required document not in file: %s"%tgt))
        elif ec=="mapped" and tgt in need:
            preds,body=need[tgt]
            if tgt in fired: R["FAIL"].append((r,fired[tgt][0]))
            elif preds-set(facts): R["NO_DATA"].append((r,"missing: %s"%", ".join(sorted(preds-set(facts))[:4])))
            else: R["PASS"].append((r,"%s did not fire"%tgt))
        else:
            R["NOT_COMPILED"].append((r,r.get("yellow_blocker_type") or ec))

    W=78; tot=len(rules)
    print("="*W); print("FULL AMQ RULESET AUDIT — loan %s"%facts.get("loan_id"))
    print("ruleset: %d rules from %s"%(tot,ruleset_path.split("/")[-1]))
    print("loan: %s / %s / %s / co-borrower=%s"%(program,amort,facts.get("loan_purpose_1003"),has_co))
    print("="*W)
    for k in ["FAIL","PASS","NOT_APPLICABLE","NO_DATA","NOT_COMPILED"]:
        print("\n%-16s %5d  (%.1f%%)"%(k,len(R[k]),100*len(R[k])/tot))
    print("\n"+"="*W); print("FAIL detail — %d rules"%len(R["FAIL"])); print("="*W)
    grp=collections.defaultdict(list)
    for r,why in R["FAIL"]: grp[why].append(r)
    for why,rs in sorted(grp.items(),key=lambda x:-len(x[1])):
        sev=collections.Counter(str(x.get("severity")) for x in rs)
        print("\n[%d rules] %s"%(len(rs),why[:110]))
        print("   severity: %s"%dict(sev))
        print("   categories: %s"%dict(collections.Counter(x["category"] for x in rs)))
        for x in rs[:3]: print("   e.g. %-14s %s"%(x.get("exception_code"),str(x.get("question_text"))[:88]))
    print("\n"+"="*W); print("PASS by document"); print("="*W)
    for why,n in collections.Counter(w for _,w in R["PASS"]).most_common():
        print("  %-42s %3d rules"%(why,n))
    print("\n"+"="*W); print("NOT_COMPILED — why (the real backlog)"); print("="*W)
    for why,n in collections.Counter(w for _,w in R["NOT_COMPILED"]).most_common():
        print("  %-34s %5d  (%.1f%%)"%(why,n,100*n/tot))
    print("\n"+"="*W)
    ev=len(R["FAIL"])+len(R["PASS"])
    print("VERDICT REACHED: %d / %d rules (%.1f%%)"%(ev,tot,100*ev/tot))
    print("of rules that are compiled AND applicable: %d / %d"%(ev,ev+len(R["NO_DATA"])))
    print("="*W)
    return R

if __name__=="__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else REPO+"src/shacl_pilot/compiled/ruleset.json")
