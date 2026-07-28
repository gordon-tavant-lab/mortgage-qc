### Action Items

- [ ]  Gordon to connect with Kayla to validate rule interpretation and get labeled test data for QA/QC checks
- [ ]  Gordon to create a PRD covering inputs, tool processing, design decisions, and output/integrations
- [ ]  Gordon to resubmit expense report with receipts attached, including items over 60 days
- [ ]  Request exception from Sesha and Anusha for Gordon's overdue expense submissions
- [ ]  Gordon to enroll in Sujata's Mortgage 101 / Tavant Mortgage University courses
- [ ]  Gordon to connect with offshore team (Amit, Vardaraj) and product team (Monish) to expand internal network
- [ ]  Team to brainstorm autonomous AI demo concept for Mortgage AI Conference in October (July–September window)
- [ ]  Kayla to provide more detail on which product/program applies to which rule sets in the spreadsheet

### QA/QC Tool — Prototyping Challenges

- **Challenge 1 — Data extraction:** An existing product was assumed to cover this, but inaccurate extraction was causing issues; would prefer to connect with the existing tool rather than rebuild
- **Challenge 2 — Labeled test data:** Test files lack known outcomes, making it impossible to validate rule results; need synthetic or pre-validated data where issues (e.g., credit score, appraisal problems) are known
- **Challenge 3 — Rule spreadsheet scope:** The Excel spreadsheet from the client is the base rule set, but additional context is needed on which rules apply to which product/program (e.g., owner-occupied vs. investment loans); for now, treat rules as applying to all loans
- Kayla may be able to provide loan files processed through Cloud, which could reduce the need for separate document extraction

### Tool Architecture & Data Sources

- Three data sources to support:
    - **Closed loan documents (PDFs):** Returned from title company after closing; these are the source of truth — document analysis (touchless team) handles classification and field extraction
    - **MISMO 3.4 XML file:** May come from title company or exported from LOS
    - **LOS (Loan Origination System):** Existing connector can be reused
- Document extraction and LOS integration are **not** to be rebuilt; assume those are solved problems and focus on the core: applying 800 checks correctly across the three data sources
- Two-step validation is needed: extract data from documents, then cross-compare with LOS/MISMO data

### Rule Engine Design Discussion

- Key question: **deterministic rule engine vs. direct LLM interpretation**
- Strong preference for determinism — the tool must produce the same pass/fail result every time for the same loan, with no variation
- Proposed approach: LLM generates an intermediate rule set at configuration time (not at run time); rules are validated, agreed upon, then executed deterministically
- LLM-per-run approach raises **cost concerns** — at scale (thousands of loans), per-file token costs could be significant
- Olav's POC is LLM-centric; acknowledged as a design difference to address
- The POC's routes → blocks → checks configuration UI was well-received by the client; this philosophy should be preserved — non-technical users (BAs, SMEs) should be able to configure and run checks without IT
- PRD should document: input sources, tool processing design, LLM vs. non-LLM tradeoffs, intermediate rule generation, output format, and downstream integrations
- Target: complete this with Kayla and the team within the next month

### Conferences & Presentations

- **HousingWire AI Summit:** Olav to handle; format of theory + live demo (workbench walkthrough) resonated well with prior audience
- **Mortgage AI Conference (California, October):** Gordon to prepare something — potentially a keynote
    - Goal: demonstrate **truly autonomous agentic decisioning** — something the industry has not seen yet
    - Target: build a compelling prototype over July–September; involve Sandeep, Olav, and others in brainstorming
    - The QA/QC tool (800 checks, configurable rules) is also a strong candidate example for a presentation

### Career Development Advice

- **Deepen mortgage domain knowledge:** Understand underwriting, income analysis, lingo, and regulatory requirements to speak intelligently about where agentic AI is appropriate vs. where pure determinism is required
- **Expand internal network:** Connect with offshore team (Amit, Vardaraj) and product/engineering leads (Monish); introductions to be facilitated
- **Role focus:** Rapid prototyping — build prototypes with Kayla, validate with clients, then hand off to Monish's team for production build-out

### Admin Items

- **Expense report:** Gordon's submission was rejected due to missing receipts and some items exceeding the 60-day submission window  ; receipts required for items above $10; exception to be requested from Sesha and Anusha
- **PTO:** Gordon's PTO request for Thursday and Friday (25th and 26th) was approved