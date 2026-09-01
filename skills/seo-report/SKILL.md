---
name: seo-report
description: Generates a technical SEO report (Markdown first, then HTML) for any website from already-captured seo.json and seo_summary.txt data. Use this skill when the user wants to regenerate or update only the SEO report without re-capturing the site. Requires seo.json, seo_summary.txt, and screenshots to already exist in <cwd>/assets/.
---

# Technical SEO Report

Writes a concise technical SEO audit to `<cwd>/assets/seo-report.md`, then renders a matching `<cwd>/assets/seo-report.html`.

This skill is site-agnostic. Use the **site context** supplied by the caller for prioritization and framing — which pages matter most, which audiences the findings affect — but keep the output technical. Context is normally a directory; read every `.md` in it.

If it includes `audit-corrections.md`, it holds standing rules from previous audits of this site: checks judged false positives, severities the user has re-calibrated, recommendations they have rejected. **Apply every rule in it before writing findings.** A rule may suppress a finding or move it down the severity ladder. Rules never override `seo.json` on matters of fact — they govern what is worth reporting and how severely, not what the data says.

## Standalone invocation — setup

When invoked directly rather than by the `audit-website` orchestrator:

1. Check that `<cwd>/assets/seo.json` and `<cwd>/assets/seo_summary.txt` exist. If not, tell the user to run `/audit-website:audit-website` first.
2. Read `<cwd>/assets/seo.json` — the authoritative data source.
3. Read `<cwd>/assets/seo_summary.txt` — human-readable summary to cross-reference.
4. Read `<cwd>/assets/manifest.txt` — to know which screenshots are available.
5. Read the site context — every `.md` in `<cwd>/context/` if that directory exists, otherwise the legacy `<cwd>/site-context.md` or single `.md` in cwd — if any exists.
6. Audit only the pages present in the data files. Do not infer, crawl, or comment on other pages unless explicitly told to.

No user questions are needed; all data comes from the captured files.

## Verify before you assert

`seo.json` is the authority. If the caller's prompt summarizes findings for you, confirm each one against the data before repeating it, and say so plainly when a briefed claim turns out to be wrong.

## Analysis — what to evaluate

Work through every page in `seo.json`. Each page gets its own top-level section. Never collapse findings across pages into a single combined bullet.

For each page, check:

**Title tag** — present? unique across pages? under 60 characters? relevant to the page's purpose? not a generic placeholder?

**Meta description** — present? unique, or copied from another page? under 155 characters? does it match the page's actual content? truncated mid-word?

**H1** — exactly one? Zero H1s is High. Multiple H1s is Medium. Does the text match the page's purpose and primary keyword? An H1 that is a multi-sentence paragraph is a finding.

**H2/H3 hierarchy** — logical? keyword-relevant headings, or vague labels?

**Canonical URL** — present and self-referencing? A canonical pointing at a different page is a finding.

**OG and Twitter tags** — `og:title`, `og:description`, `og:image`, `og:url`, `twitter:card`, `twitter:image` present? Is `og:description` stale relative to the meta description?

**JSON-LD structured data** — any schema markup? Valuable types include `Organization`, `WebSite`, `SoftwareApplication`, `BreadcrumbList`, and `FAQPage` on pages with a Q&A block. Absent JSON-LD site-wide is Medium.

**Meta robots** — anything set to `noindex` is High-severity and blocking.

**Images missing alt text** — count, ratio, and a few examples. Medium: accessibility and SEO both.

**Word count** — under 150 words High (thin content); 150–300 Medium (borderline for competitive queries); over 300 OK.

**Links** — external links with empty anchor text, and links pointing at bare domain roots rather than real destinations.

**Cross-page patterns** — meta descriptions or full page content duplicated across URLs (High); inconsistent title templates; issues repeating on every page.

## Not defects — do not report these as findings

- **Absent `meta robots`.** A page with no robots meta defaults to `index, follow`. That is correct and expected. Report it as informational at most, never as a defect. Only an actual `noindex`, `nofollow`, or `none` value is a finding.
- **Absent `meta keywords`.** Ignored by every major search engine.

If a caller's briefing presents one of these as a defect, say plainly that it is not, and record it as informational.

## Severity definitions

- **High** — directly hurts ranking or crawlability, or is a publishing error: missing H1, `noindex`, duplicate pages, wrong or truncated meta description.
- **Medium** — a missed optimization that compounds: missing JSON-LD, thin content, OG gaps, absent alt text.
- **Low** — polish: a generic title, a mildly over-length description.

For every issue, include **why it matters** and a **suggested fix**.

## Writing rules

- Markdown first: write `seo-report.md` before generating `seo-report.html`.
- The HTML must be a faithful rendering of the Markdown, not a second draft.
- Data-first. Keep prose minimal and let tables and badges do the work.
- Each page section includes the page URL, its raw metric values, severity-tagged findings, and explicit fixes.
- Put a visible link near the top of the HTML to `seo-report.md`.

## HTML rendering

Self-contained: one file, no external CSS or JS. `system-ui` font stack, max width 900px, centered, 24px side padding. Match the messaging report's palette so the two read as one set.

Structure:
1. **Masthead** — site name, "Technical SEO Report", date.
2. **At a glance** — three stat boxes (High / Medium / Low counts) plus one sentence naming the most critical finding.
3. **Per-page sections** — page name as H2 with the URL as a muted subtitle; a two-column grid with a metrics table on the left and the viewport screenshot on the right; then an issues table.
4. **Site-wide patterns** — issues spanning multiple pages.
5. **All issues** — one table sorted High → Medium → Low across every page, for triage.

Severity badges: High `#fee2e2`/`#991b1b`/border `#fca5a5`; Medium `#ffedd5`/`#9a3412`/border `#fdba74`; Low `#f3f4f6`/`#374151`/border `#d1d5db`. Sticky top nav with an anchor per page section plus Summary, Patterns, and All Issues.
