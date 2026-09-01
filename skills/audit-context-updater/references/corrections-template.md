# Audit Corrections — [COMPANY] ([domain])

Durable feedback on **how this site should be audited**. Written by the
`audit-context-updater` skill when the user pushes back on a finding, and read by
`messaging-report` and `seo-report` before they write anything.

This file is about audit judgment, not company facts. Facts about the company, its
audiences, and its goals belong in `company.md`, which is edited in place. This file
accumulates instead — each entry is a standing rule that survives into future runs.

Do not delete entries casually. Retire one only when it is superseded by a newer rule
or the user says it no longer applies.

---

## How to write an entry

Each entry is a **rule**, not a story. Three parts, all required:

- **The rule** — an imperative the report agent can act on.
- **Scope** — which report and which pages it applies to, in parentheses.
- **Why** — the reason it holds, so a future run can judge whether it still does.

Scope every rule as narrowly as the feedback justifies. A rule that says
"don't discuss CTAs" is too broad and will suppress valid findings; one that says
"don't flag the missing CTA on /careers" is actionable.

Never write a rule that blanket-forbids a whole topic or page.

---

## Corrections

<!-- Newest last. Format:

- **[Imperative rule.]** (report-name, page scope)
  [Why this holds — one or two sentences.]
  *Recorded [YYYY-MM-DD].*

Example:

- **Don't flag absent `meta robots` as a defect.** (seo-report, all pages)
  Absent robots meta defaults to `index, follow`. Report as informational only.
  *Recorded 2026-08-30.*

-->

*(No corrections recorded yet.)*

---

## Retired

<!-- Move superseded rules here rather than deleting them, with a one-line note
     saying what replaced them and when. Keeps the reasoning auditable. -->

*(None.)*
