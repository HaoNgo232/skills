---
name: fact-check
description: Rigorously verify claims, news, social posts, or statements against high-trust primary sources with a structured evidence hierarchy, verbatim citations, and clear verdict taxonomy. Use when the user asks to "fact-check this", "verify this claim", "is this true", or invokes /fact-check.
---

# Fact-Check Skill (`fact-check`)

Rigorously analyze, cross-examine, and verify claims against primary sources and authoritative evidence to produce structured, neutral, and auditable fact-check reports.

---

## 1. End-to-End Fact-Checking Workflow (9 Stages)

```
[Raw User Claim / Article / Social Post]
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 1: Intake & Scoping               │ ── Identify claim type, language, constraints & source restrictions
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 2: Claim Extraction (Atomization) │ ── Break complex text into atomic verifiable statements
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 3: Prior-Plausibility Triage      │ ── Sagan's rule: extraordinary claims require extraordinary evidence
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 4: Targeted Evidence Collection   │ ── Draft 2-6 queries per statement, parallelize, prioritize Tier 1
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 5: Cross-Checking (Two-Source)    │ ── Independence test: 2 outlets citing the same wire != 2 sources
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 6: Logic & Context Analysis       │ ── Fallacies, missing-context audit, cherry-picking & manipulation
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 7: Verdict Assignment             │ ── 8-label taxonomy + modifiers + composite aggregation rule
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 8: Standardized Reporting         │ ── Markdown report with front-loaded title & hyperlinked verbatim quotes
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Stage 9: Post-Publication Quality Gate  │ ── Final pre-flight verification checklist
└─────────────────────────────────────────┘
```

### Stage 1 — Intake & Scoping
* **Capture raw input**: Preserve original wording, timestamps, and context.
* **Detect language**: Always respond in the user's inquiry language while keeping critical original quotes intact.
* **Identify request type**: Single-claim check, multi-claim article check, follow-up inquiry, or meta-analysis.
* **Enforce user constraints**: If the user pins an exclusive source list and all fail, halt and notify the user — never silently substitute unpermitted sources.

### Stage 2 — Claim Extraction (Atomization)
* **Atomize compound assertions**: E.g., *"Company X laid off 500 workers on Tuesday and was sued for fraud"* becomes two separate atomic statements.
* **Extract & Flag**: Exact dates, numbers, statistics, event occurrences, legal actions, quotes and attributions, scientific/medical claims, claims about identifiable people/organizations.
* **Ignore / Do Not Flag**: Subjective opinions ("I think", "feels unfair"), unprovable hypotheticals, rhetorical questions, well-established universal facts (e.g., "water is H₂O").

### Stage 3 — Prior-Plausibility Triage
Assign a prior plausibility score (**Low / Medium / High**) to prioritize search depth:
* *Sagan's Rule*: Extraordinary claims require extraordinary evidence. Low-plausibility claims demand the deepest multi-tier verification.

### Stage 4 — Evidence Collection
* Draft 2–6 targeted queries per statement targeting primary sources.
* Run parallel searches. Crawl full pages — **never** rely solely on search engine snippets for final verdicts.
* Record verbatim quotations, original dates, and permanent URLs.

### Stage 5 — Cross-Checking Protocols
* **Two-Source Rule**: No material fact is confirmed without at least two independent sources, unless the sole source is an unassailable Tier-1 primary record (e.g., official government gazette, SEC filing).
* **Independence Test**: Two news outlets syndicating the exact same wire story (e.g., AP/Reuters feed) count as **one** source, not two. Look for independent reporting or primary source records.
* **Temporal Alignment**: Ensure the source publication date precedes or coincides with the claimed event timeframe.
* **Translation Integrity**: For non-English statements, quote the original verbatim and provide an accurate translation.

### Stage 6 — Logic & Context Analysis
Apply the critical thinking and manipulation filters detailed in Section 3.

### Stage 7 — Verdict Assignment
Map evidence to the 8-label taxonomy (Section 4) with appropriate modifiers and composite aggregation rules.

### Stage 8 — Reporting
Render using the Standard Output Template (Section 5).

### Stage 9 — Post-Publication Quality Gate
Checklist before returning response to user:
- [ ] Every atomic statement has an explicit verdict.
- [ ] At least 2 independent sources for each material fact.
- [ ] Title front-loads the verdict.
- [ ] Every factual assertion has an inline hyperlinked citation.
- [ ] No evidence carried over from an unrelated prior request.
- [ ] Response language strictly matches user language.

---

## 2. Verification Hierarchy & Evidence Weighting

* **Tier 1 — Primary / Direct Sources (Weight: ⭐⭐⭐⭐⭐)**:
  * Official government records: Court dockets, legislative text, agency filings (SEC/EDGAR, FDA, USPTO, EUR-Lex).
  * Statistical agencies: World Bank, IMF, WHO, national census & labor bureau datasets.
  * Peer-reviewed academic journals (verifying non-retraction status).
  * Direct verified first-party statements: Sworn testimony, official corporate press releases, verified origin social posts.
  * Raw photographic, video, or audio evidence with verified provenance.
* **Tier 2 — Authoritative Secondary Sources (Weight: ⭐⭐⭐⭐)**:
  * International wire services: Reuters, Associated Press (AP), AFP, Bloomberg.
  * Major newspapers of record: NYT, WaPo, WSJ, Financial Times, The Guardian, BBC, NPR.
  * Signatories of the International Fact-Checking Network (IFCN): PolitiFact, Snopes, FactCheck.org, Full Fact.
* **Tier 3 — Reputable Analytical Sources (Weight: ⭐⭐⭐)**:
  * Non-partisan think tanks and NGOs with disclosed methodology and funding (Pew, Brookings, RAND).
  * Specialist trade press: Nature News, Science, IEEE Spectrum.
  * Domain commentary from credentialed academic subject-matter experts.
* **Tier 4 — Contextual Sources (Weight: ⭐⭐)**:
  * Wikipedia (used only as a directory/map to underlying primary sources, never as terminal evidence).
  * General magazines, corporate blogs (valid only for that company's stated stance).
* **Tier 5 — Low-Trust / Contextual-Only (Weight: ⭐)**:
  * Anonymous forum threads, unverified social media screenshots, content farms, AI-generated aggregators.
  * *Rule*: Never used as terminal evidence; cited only if the claim itself is about the viral post.

### Red Flags That Downgrade a Source
* Lack of named author, dateline, or editorial correction policy.
* Absence of direct links to underlying data/documents.
* Clickbait/sensationalist headline unsupported by the article text.
* Undisclosed funding or clear conflicts of interest.
* Circular reporting: Outlets simply quoting each other without independent inquiry.

---

## 3. Logic & Context Analysis Framework

### A. Fallacy Detection Checklist
* **Straw Man**: Target's position distorted -> Compare directly to the target's original words.
* **Ad Hominem**: Attack on personal character -> Disregard insults; verify underlying factual assertion only.
* **False Dilemma**: Only two extreme options presented -> Document nuanced intermediate possibilities.
* **Post Hoc (Correlation vs. Causation)**: *"A happened, then B, therefore A caused B"* -> Demand controlled evidence or demonstrable mechanism.
* **Cherry-Picking**: Selective extraction of favorable numbers or quotes -> Retrieve the complete dataset or transcript.
* **Hasty Generalization**: Single anecdote treated as universal rule -> Require statistical population-level data.
* **Appeal to Authority**: Quoting an irrelevant or uncredentialed authority -> Verify subject-matter qualifications.
* **Loaded Question / Presupposition**: Question assumes a contested fact -> Split into presupposition and question.

### B. Missing-Context Audit (7 Questions)
1. **When** did this happen? (Was an old event recycled as recent news?)
2. **Where** did it occur? (Is the geographic scope misrepresented?)
3. **Who** is involved? (Is the title or standing overstated?)
4. **Compared to what?** (Is the baseline stated?)
5. **Out of how many?** (Is the denominator provided for percentage claims?)
6. **What was cut?** (Are quotes or video clips trimmed deceptively?)
7. **What came before and after?** (Is the chronological sequence preserved?)

### C. Manipulation Tactic Detection
* **Cropped Media**: Images or video trimmed to alter meaning -> Locate original uncropped source.
* **Deepfake / Synthetic AI Media**: AI-generated audio/visuals -> Check forensic artifacts and verify against official broadcast streams.
* **Miscaptioned Media**: Genuine footage paired with a false narrative/date/location -> Reverse-image search to identify original provenance.
* **Rage-Bait Framing**: Emotive adjectives obscuring thin facts -> Strip loaded language, extract factual core.

---

## 4. Verdict Classification Taxonomy (8 Labels + Modifiers)

| Verdict | Definition | Required Evidence Threshold |
| :--- | :--- | :--- |
| **True** | The claim is accurate and no significant details are omitted. | $\ge$ 2 independent Tier-1/2 sources fully corroborate. No credible contradicting evidence. |
| **Mostly True** | Core claim is accurate, with only minor inaccuracies that do not alter the overall takeaway. | Corroboration of the main assertion; minor factual slips explicitly noted. |
| **Half True / Mixed** | Contains accurate elements alongside inaccurate or misleading elements of equal weight. | Mixed confirmation: key parts verified, other key parts contradicted. |
| **Misleading** | Technically true elements framed or cropped to produce a substantially false impression. | Verified facts combined with documented omission of critical context. |
| **Mostly False** | Contains a minor kernel of truth but is largely wrong or distorts foundational facts. | Central assertion refuted; only peripheral details are correct. |
| **False** | The claim is demonstrably incorrect or fabricated. | $\ge$ 2 independent Tier-1/2 sources directly contradict. Zero credible evidence. |
| **Unverified / Insufficient Evidence** | Reliable information is insufficient to confirm or refute the claim. | Exhaustive search completed; primary records absent or irreconcilably divided. |
| **Satire / Miscategorized** | Originates as satire, fiction, parody, or opinion mistaken as genuine news. | Provenance linked to known satire publication or creator admission. |

### Optional Modifiers
* **(Outdated)**: Accurate at a prior point in time but no longer true (e.g., `True (Outdated)`).
* **(Disputed)**: High-tier reputable sources actively disagree on interpretation (e.g., `Half True (Disputed)`).

### Composite-Claim Aggregation Rule
When an inquiry contains multiple atomic statements:
1. Assign an individual verdict to each atomic statement.
2. The overall verdict is determined by the **weakest-link / most consequential statement**, unless minor peripheral errors do not affect the main conclusion.
3. Always present the atomic breakdown table so the audit trail is transparent.

---

## 5. Title Construction Rules

Always **front-load the verdict** in the headline:
* **False / Mostly False**: `Fact Check: [Subject] Did NOT [Action]`
* **True / Mostly True**: `Fact Check: [Subject] DID [Action]`
* **No Evidence Exists**: `Fact Check: NO Evidence [Subject] [Action]`
* **Misleading Framing**: `Fact Check: [Subject] Claim Is MISLEADING; [Brief explanation]`
* **Attribution Error**: `Fact Check: [Entity] Did NOT Say [Quote]`

---

## 6. Standardized Output Report Scaffold

```markdown
# Fact Check: {Front-Loaded Verdict Headline}

**Claim (verbatim):** "{Exact text of the original claim}"
**Source of Claim:** {Originating post URL, public speech, document, or publication date}
**Overall Verdict:** {One of the 8 labels + modifier if applicable}
**Executive Summary:** {2–4 sentences: what was claimed, core findings from primary sources, and why this verdict was reached.}

---

## Atomic Statements & Verdicts

| # | Atomic Statement (verbatim) | Verdict | Key Evidence Source |
|---|---|---|---|
| 1 | "{Statement 1}" | True / False / Misleading | [Primary Source](https://url) |
| 2 | "{Statement 2}" | ... | [Primary Source](https://url) |

---

## Detailed Statement Analysis

### Statement 1: "{Statement 1}"
* **Verdict:** {Verdict}
* **Supporting Evidence:**
  * "{Verbatim quote}" — [Publisher Name](https://url) *(accessed YYYY-MM-DD)*
* **Contradicting / Complicating Evidence:**
  * "{Verbatim quote}" — [Publisher Name](https://url)
* **Logic & Context Notes:** {Fallacies detected, missing denominator, temporal distortion, etc.}
* **Reasoning:** {Clear deductive explanation linking evidence to the assigned verdict.}

---

## Context & Background
{1–3 paragraphs supplying necessary background history, preceding events, or institutional context with hyperlinked citations.}

---

## Methodology & Audit Notes
* **Sources Consulted:** {Count by tier, e.g., 3 Tier-1 Primary, 4 Tier-2 Secondary}
* **Independence Verification:** {Confirmation that sources do not share circular origin}
* **Limitations:** {Any documents or data points currently inaccessible}

---

## Conclusion
{Final concise synthesis restating the core reality and addressing any remaining uncertainty.}

---

## References & Citations
1. [Document / Article Title](https://url) — *Publisher, Date (Tier classification)*
2. [Document / Article Title](https://url) — *Publisher, Date (Tier classification)*
```
