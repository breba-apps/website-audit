---
name: audit-website
description: Full website audit for any site. Captures screenshots and SEO data for a given list of URLs, then runs a messaging audit and a technical SEO report in parallel as subagents, and produces a linked index.html. Use this skill whenever the user wants to review, audit, critique, or analyze a website — including phrases like "audit example.com", "review our site", "what do you think of our homepage", or "update the website audit".
---

# Website Audit — Orchestrator

Captures fresh screenshots of the requested URLs, then spawns a messaging report agent and a technical SEO report agent **in parallel**, waits for both, and writes an `index.html` linking to both the HTML and Markdown outputs.

This skill is site-agnostic. Everything specific to a particular company, product, audience, or business goal lives in the **context directory** (see Step 2), never in this file.

---

## Step 1: Determine the URLs to audit

The user must supply the URLs, either directly in their request or in a `urls.json` file.

- If the user named specific URLs, use exactly those.
- If the user named only a domain, ask which pages to audit and offer to start from the homepage plus the pages in the main navigation. Do not crawl or discover pages on your own.
- If `<cwd>/assets/urls.json` already exists and the user asked to re-run or update an audit, reuse it.

Audit only these URLs. Do not report on any other pages unless the user explicitly asks.

---

## Step 2: Resolve the context directory

Context supplies the domain knowledge the reports need — what the company does, who its audiences are, what the site is meant to accomplish — plus any standing corrections from previous audits. Resolve it in this order:

1. A path the user named explicitly. A directory resolves as a bundle; a single file resolves as itself.
2. `<cwd>/context/` — **read every `.md` file in it**, not one of them. This is the normal case.
3. `<cwd>/site-context.md` (legacy single-file layout).
4. A single `.md` file in cwd (legacy).

Read everything that resolves, in full, and pass the **directory path** to both subagents — or the single file path if a legacy layout resolved. Never paste the contents into the agent prompts.

A populated `context/` directory normally holds:
- `company.md` — the company, its audiences, its business goals
- `audit-corrections.md` — standing rules about how this site should be audited, learned from feedback on previous runs
- any other `.md` the user has added

If nothing resolves, **invoke the `audit-context-updater` skill** to bootstrap it. That skill owns the interview and writes `company.md` and `audit-corrections.md`. Do not improvise the interview here, and do not proceed without context — both reports are graded against audiences and goals, and without them the output is generic.

If the user corrects a fact about the company, its audiences, or its goals mid-audit, hand it to `audit-context-updater` rather than editing context yourself. It owns the rules that decide which file a correction belongs in and whether it is written in place or appended.

---

## Step 3: Set up the assets directory and capture the site

The assets directory is `<cwd>/assets`.

`<skill-dir>` below is the base directory announced when this skill was invoked. Do not use `${CLAUDE_PLUGIN_ROOT}` — it is not exported to the Bash tool.

```bash
mkdir -p <cwd>/assets
python3 "<skill-dir>/scripts/capture_site.py" <cwd>/assets <url> [<url> ...]
```

Requires Playwright with Chromium. If the script fails on a missing browser, run `python3 -m playwright install chromium` and retry.

The script produces, in the assets directory:
- `*.png` — full-page and viewport screenshots for each requested URL
- `seo.json` — raw SEO data (machine-readable)
- `seo_summary.txt` — human-readable SEO summary per page
- `manifest.txt` — list of all captured screenshots

While it runs, read a few of the resulting screenshots with the Read tool to form your own picture of the pages — at minimum the viewport and full-page shots of the most important URLs.

---

## Step 4: Read runtime inputs

Read `<cwd>/assets/seo_summary.txt` (pass to the SEO subagent) and `<cwd>/assets/manifest.txt` (pass to both).

---

## Step 5: Spawn both report agents IN PARALLEL

**Send a single message containing two Agent tool calls** so they run concurrently.

Use the agents bundled with this plugin: `subagent_type: "audit-website:messaging-agent"` and `subagent_type: "audit-website:seo-agent"`. If those names are not available, they may appear unprefixed as `messaging-agent` and `seo-agent`. Each already has its report skill preloaded, so do **not** paste skill contents into the prompts.

Do not paste the context either — pass the absolute directory path and let each agent read every `.md` in it. Do paste `manifest.txt`, and paste `seo_summary.txt` for the SEO agent.

### Agent 1 — Messaging Report (`messaging-agent`)

```
You are generating a messaging audit for the URLs listed below.
Your messaging-report skill is preloaded — follow it exactly. Skip its
"Standalone invocation" section; all setup is done and all context is below.

== SITE CONTEXT ==
Read EVERY .md file in this directory, in full:
[absolute path to the resolved context directory]

`company.md` is the source of truth for the company, its audiences, and its
business goals. `audit-corrections.md`, if present, holds standing rules from
previous audits of this site — apply every rule in it before writing findings.
Never assume a fact about the company that these files do not state.

== CONTEXT ==
Assets directory (absolute path): <cwd>/assets
All screenshots are already captured there.
Markdown output to write first: <cwd>/assets/messaging-report.md
HTML output to write second: <cwd>/assets/messaging-report.html
Screenshot img src paths: use the filename only (e.g. src="home_full.png") — the HTML lives in the same directory.
Today's date: [today's date]
Audit only the pages represented in the manifest below. Do not discuss or infer other pages.

== AVAILABLE SCREENSHOTS ==
[paste the contents of manifest.txt]

== INSTRUCTIONS ==
Read only the screenshots you need using the Read tool. Write messaging-report.md first,
then render messaging-report.html from that Markdown.
Do not ask any questions — all context is provided above. Proceed directly to generating both files.
Return a short summary of the core gap and the top 3 priorities.
```

### Agent 2 — Technical SEO Report (`seo-agent`)

```
You are generating a technical SEO audit for the URLs listed below.
Your seo-report skill is preloaded — follow it exactly. Skip its
"Standalone invocation" section beyond reading the data files named below.

== SITE CONTEXT ==
Read EVERY .md file in this directory, in full:
[absolute path to the resolved context directory]

Use `company.md` to prioritize and frame findings. If `audit-corrections.md` is
present, apply every rule in it before writing findings — a rule there may
suppress or re-rank a finding you would otherwise report.

== CONTEXT ==
Assets directory (absolute path): <cwd>/assets
Markdown output to write first: <cwd>/assets/seo-report.md
HTML output to write second: <cwd>/assets/seo-report.html
Screenshot img src paths: use the filename only (e.g. src="home_viewport.png").
Today's date: [today's date]
Audit only the pages present in seo.json. Do not discuss or infer other pages.

== SEO DATA ==
The authoritative source is <cwd>/assets/seo.json — read it. Cross-reference the summary below.
[paste the contents of seo_summary.txt]

== AVAILABLE SCREENSHOTS ==
[paste the contents of manifest.txt]

== INSTRUCTIONS ==
Read any screenshots you need for visual context. Write seo-report.md first,
then render seo-report.html from that Markdown.
Do not ask any questions — all data is in the files. Proceed directly to generating both files.
Return a short summary: High/Medium/Low counts and the single most critical finding.
```

---

## Step 6: Wait for both agents

Both run concurrently. Wait for both to return before writing `index.html`.

If either agent reports a correction to something you told it, verify it yourself against `seo.json` before repeating it to the user.

---

## Step 7: Write index.html

Write `<cwd>/assets/index.html` — a minimal table of contents linking to both the HTML and Markdown versions of each report. Substitute the real site name and today's date for the bracketed placeholders.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[SITE NAME] Website Audit — [MONTH YEAR]</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #fff;
      color: #1a1a1a;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container { max-width: 560px; width: 100%; padding: 0 24px; }
    .eyebrow {
      font-size: 11px; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.1em; color: #999; margin-bottom: 12px;
    }
    h1 {
      font-size: 36px; font-weight: 700; letter-spacing: -0.02em;
      line-height: 1.1; margin-bottom: 6px;
    }
    .date { font-size: 14px; color: #999; margin-bottom: 48px; }
    .reports { list-style: none; }
    .reports li { border-top: 1px solid #ebebeb; padding: 20px 0; }
    .reports li:last-child { border-bottom: 1px solid #ebebeb; }
    .reports a {
      display: block; font-size: 17px; font-weight: 600;
      color: #1a1a1a; text-decoration: none; margin-bottom: 3px;
    }
    .reports a:hover { color: #2563eb; }
    .reports p { font-size: 13px; color: #777; line-height: 1.5; }
    .reports .src a { display: inline; font-size: 13px; font-weight: 400; color: #2563eb; }
  </style>
</head>
<body>
  <div class="container">
    <div class="eyebrow">[DOMAIN]</div>
    <h1>Website Audit</h1>
    <div class="date">[FULL DATE — e.g. May 13, 2026]</div>
    <ul class="reports">
      <li>
        <a href="messaging-report.html">Messaging Audit →</a>
        <p>Page-by-page messaging audit with prioritized recommendations.</p>
        <p class="src"><a href="messaging-report.md">Markdown source</a></p>
      </li>
      <li>
        <a href="seo-report.html">Technical SEO Report →</a>
        <p>Page-by-page SEO findings with severities and suggested fixes.</p>
        <p class="src"><a href="seo-report.md">Markdown source</a></p>
      </li>
    </ul>
  </div>
</body>
</html>
```

---

## Step 8: Done

Tell the user the audit is complete, give them the path to `<cwd>/assets/index.html`, and surface the headline findings each agent returned. Note that they can open the index in a browser to reach both reports.

---

## Step 9: Capture feedback

If the user pushes back on any finding — it is wrong, it does not matter for their business, the severity is off, the audit keeps recommending something they have already rejected — **invoke the `audit-context-updater` skill** and let it classify and persist the feedback.

This applies whenever the pushback arrives: immediately, or several turns later. Do not write to the context directory yourself, and do not let a correction pass with only a conversational acknowledgement — unpersisted feedback means the next run repeats the same mistake.

Do not prompt for feedback if the user has not offered any. Wait for a genuine reaction rather than soliciting one.
