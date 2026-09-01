---
name: messaging-report
description: Generates a messaging audit report (Markdown first, then HTML) for any website from already-captured screenshots and a site context directory. Use this skill when the user wants to regenerate or update only the messaging report without re-capturing the site. Requires screenshots and seo_summary.txt to already exist in <cwd>/assets/.
---

# Messaging Report

Writes a concise messaging audit to `<cwd>/assets/messaging-report.md`, then renders a matching `<cwd>/assets/messaging-report.html`.

This skill is site-agnostic. All knowledge about the specific company, its audiences, and its business goals comes from the **site context** supplied by the caller — normally a directory, every `.md` in which must be read. Ground every recommendation in it; never assume facts about the company that it does not state.

If the context includes `audit-corrections.md`, it holds standing rules from previous audits of this site: findings judged false positives, severities the user has re-calibrated, recommendations they have rejected. **Apply every rule in it before writing findings.** A rule may suppress or re-frame something you would otherwise report. If a rule seems to contradict what the page plainly shows, follow the rule and note the tension in one line rather than silently overriding it.

## Standalone invocation — setup

When invoked directly rather than by the `audit-website` orchestrator:

1. Verify `<cwd>/assets/` contains screenshots. If not, tell the user to run `/audit-website:audit-website` first to capture them.
2. Read `<cwd>/assets/manifest.txt` for the list of available screenshots.
3. Read `<cwd>/assets/seo_summary.txt` for copy-level context — headings, word counts, meta descriptions.
4. Read the site context: every `.md` in `<cwd>/context/` if that directory exists, otherwise the legacy `<cwd>/site-context.md` or single `.md` in cwd. If none exists, invoke the `audit-context-updater` skill to bootstrap it before continuing.
5. Audit only the pages represented in the assets. Do not infer, crawl, or comment on other pages unless explicitly told to.

## Analysis — what to read

Read the screenshots from `manifest.txt` needed to understand each audited page. Read the full-page shot when judging structure and flow; the viewport shot when judging first impression.

## Analysis — what to evaluate

Before writing anything, identify the cross-sectionality of content, intent, and audience for each page: who is this page's content actually for, and is that audience addressed in a way that is intentional, instructive, and persuasive?

Give each audited page its own top-level section. Within it, evaluate the relevant parts of the page on three axes:

1. **What's there now** — what the section actually says and shows. Reference the screenshot filename.
2. **The opportunity** — tie the critique to a specific audience from `company.md` and their emotional starting point. No generic feedback.
3. **Possible directions** — 2–3 concrete alternatives, with example copy where useful.

**Page aspects to cover when relevant**
- Hero / above the fold
- Value proposition
- Use cases
- Credibility signals
- Conversion paths, or their absence
- Calls to action

**Core gap:** before the page-by-page sections, name the single most important gap in 1–2 short sentences, framed against the primary audience and business goal.

**What's working:** lead with 2–4 specific observations about what the site does well. Specific, not flattering.

**Priority table:** close with a prioritized table of 3–6 recommended actions.

Report factual defects you find in the live copy — placeholder text, duplicated copy across sections, dates that have passed, broken or dead-end links — as findings in their own right, with the screenshot that shows them.

## Writing rules

- Markdown first: write `messaging-report.md` before generating `messaging-report.html`.
- The HTML must be a faithful rendering of the Markdown, not a second draft.
- Concise, concrete, specific. No fluff, throat-clearing, or generic web-best-practice filler.
- Every claim maps to a page section and, where useful, a screenshot filename.
- Never collapse multiple pages into one vague combined summary. Each page gets its own section and its own anchor in the HTML.
- Put a visible link near the top of the HTML to `messaging-report.md` so the source can be copied or downloaded.

## HTML rendering

Self-contained: one file, no external CSS or JS, no CDN links. `system-ui` font stack.

- Palette: background `#ffffff`, text `#1a1a1a`, muted `#6b7280`, border `#e5e7eb`, accent `#2563eb`.
- Callout borders: working `#16a34a` on `#f0fdf4`, gap `#ea580c` on `#fff7ed`, direction `#2563eb` on `#eff6ff`.
- Max content width 800px, centered, 24px side padding.
- Sticky top nav with anchor links to each audited page and to the priority table.
- Screenshots inside `<figure>` at full column width with a muted `<figcaption>` naming the file. Use `loading="lazy"`.
- Priority table: dark header rule, numbered badge per row.
