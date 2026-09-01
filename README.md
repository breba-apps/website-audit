# audit-website

A Claude Code **plugin** that audits a website on your own machine — no sandbox, no cloud, no containers. It captures screenshots and SEO data for a list of URLs, then runs a **messaging audit** and a **technical SEO report** in parallel and links them from a single `index.html`.

The skills are generic. Everything specific to a company — what it does, who it's for, what the site is meant to accomplish — lives in an editable **context directory** at `./context/`. The plugin also learns: when you push back on a finding, the correction is written back to that directory so the next audit does not repeat it.

## Requirements

- Claude Code
- Python 3 with Playwright and Chromium:

```bash
pip install playwright
python3 -m playwright install chromium
```

## Install

In Claude Code, add this repo as a plugin marketplace, then install the plugin from it:

```
/plugin marketplace add breba-apps/website-audit
/plugin install audit-website@breba-tools
```

The first line points at the repository; the second installs the plugin by name from the `breba-tools` marketplace it contains. Pin to a tag if you want a fixed version:

```
/plugin marketplace add breba-apps/website-audit@v1.1.0
```

Update later with `/plugin update audit-website@breba-tools`.

### Local development

To run a working copy without installing:

```bash
claude --plugin-dir /path/to/website-audit
```

Either way the plugin loads as a unit — the four skills and two agents travel together, and nothing depends on where they sit relative to each other.

## Use

```
/audit-website:audit-website https://example.com https://example.com/pricing https://example.com/about
```

Plugin skills are always namespaced `plugin-name:skill-name`, which is why the name appears twice. Rename the plugin in `.claude-plugin/plugin.json` to change the prefix.

On the first run for a new site there is no context yet. The orchestrator hands off to `audit-context-updater`, which interviews you and writes `./context/company.md`. To skip the interview, fill it in yourself:

```bash
mkdir -p context
cp /path/to/plugin/skills/audit-context-updater/references/company-template.md context/company.md
cp /path/to/plugin/skills/audit-context-updater/references/corrections-template.md context/audit-corrections.md
```

The orchestrator looks for a path you name explicitly, then `./context/` — reading **every** `.md` in it — then the legacy `./site-context.md` or a single loose `.md`. It won't run without context: both reports are graded against audiences and business goals, and without them the output is generic.

### Feedback

When you tell the audit it got something wrong, run `audit-context-updater` (the orchestrator offers it). It classifies each correction and routes it:

| Feedback | Lands in | How |
| --- | --- | --- |
| A company fact, audience, or goal is wrong | `context/company.md` | edited in place — new facts supersede old ones |
| A finding was a false positive, wrong severity, or irrelevant to your business | `context/audit-corrections.md` | appended as a scoped rule that future runs apply |
| A one-off taste reaction | nowhere | persisting these just accumulates noise |
| A defect that would hit *any* site | nowhere | it's a skill bug — fix the skill instead |

That last row is the one worth understanding. If a correction would also be true when auditing a different company, writing it into your site's corrections file papers over a defect every other audit keeps hitting.

Both reports read `audit-corrections.md` before writing findings. Rules govern what is worth reporting and how severely — they never override `seo.json` on matters of fact.

Output lands in `./assets/`:

| File | What it is |
| --- | --- |
| `index.html` | Table of contents linking both reports |
| `messaging-report.md` / `.html` | Page-by-page messaging audit with a priority table |
| `seo-report.md` / `.html` | Page-by-page SEO findings with severities and fixes |
| `*.png` | Full-page and viewport screenshots |
| `seo.json`, `seo_summary.txt`, `manifest.txt` | Raw captured data |

Open `assets/index.html` in a browser.

## Layout

```
.claude-plugin/plugin.json    manifest
skills/
  audit-website/              orchestrator — captures the site, spawns both agents, writes index.html
    scripts/capture_site.py
  messaging-report/           generic messaging audit skill
  seo-report/                 generic technical SEO skill
  audit-context-updater/      bootstraps context; captures feedback into it after a run
    references/
      company-template.md     blank company.md to copy per site
      corrections-template.md blank audit-corrections.md to copy per site
agents/
  messaging-agent.md          preloads messaging-report
  seo-agent.md                preloads seo-report
```

The plugin ships no directory named `context/`. That name means exactly one thing — live, per-site context, read in full by the report agents — so the templates deliberately live under the skill that owns them.

Per audited site, in that site's working directory:

```
context/
  company.md                  the company, its audiences, its business goals
  audit-corrections.md        standing rules learned from your feedback
  <anything>.md               optional extras — all of them get read
assets/                       screenshots, captured data, generated reports
```

The orchestrator spawns the two bundled agents, each of which has its report skill preloaded via `skills:` frontmatter — so no prompt pasting and no path resolution between skills.

Either report skill can also be run on its own to regenerate one report from already-captured assets without re-crawling:

```
/audit-website:messaging-report
/audit-website:seo-report
```

`audit-context-updater` runs standalone too, whenever you want to record feedback or edit context:

```
/audit-website:audit-context-updater
```

It always runs in the main conversation — it needs to interview you and confirm before editing your source of truth, and it never writes silently.

## Capturing without Claude

The capture script is standalone:

```bash
python3 skills/audit-website/scripts/capture_site.py ./assets https://example.com
# or, reading ./assets/urls.json
python3 skills/audit-website/scripts/capture_site.py ./assets
```

It visits only the URLs it is given — there is no crawling or page discovery.
