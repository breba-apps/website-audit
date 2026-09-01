---
name: audit-context-updater
description: Creates and maintains the site context directory that website audits are graded against. Use when bootstrapping context for a site that has none, and whenever the user pushes back on audit findings — "that's wrong", "that doesn't matter for us", "we're not actually targeting X", "stop flagging Y" — so the correction persists into future runs instead of evaporating.
---

# Audit Context Updater

Maintains `<cwd>/context/` — the directory the audit reports are graded against.

Run this **in the main conversation loop, never as a subagent.** It interviews the user
and edits their source of truth; a background agent can do neither.

---

## The context directory

```
<cwd>/context/
  company.md            what the company is, who it sells to, what the site is for
  audit-corrections.md  standing rules about how this site should be audited
  <anything>.md         optional extras — brand voice, competitors, prior decisions
```

Every `.md` in the directory is read by the report agents. Both core files live per
site, alongside each other.

The two core files have **different write semantics**, and this is the distinction the
whole skill turns on:

| File | Corrections | Write |
|---|---|---|
| `company.md` | supersede — a new fact replaces the old one | **edit in place** |
| `audit-corrections.md` | accumulate — rules build up over runs | **append** |

Getting this backwards is the main failure mode. Appending facts produces a
self-contradicting fact sheet; overwriting corrections loses everything learned.

Templates for both live in `<skill-dir>/references/` as `company-template.md` and
`corrections-template.md`, where `<skill-dir>` is the base directory announced when
this skill was invoked.

A directory named `context/` always means live, per-site context that the report
agents read in full. Never write a template or an example into one.

---

## Mode A — Bootstrap

Use when `<cwd>/context/` is missing or has no `company.md`.

1. Read `references/company-template.md`. It defines the required sections.
2. Ask the user for the two things the reports cannot be written without:
   - **Audiences** — who they are, by role and organization type; what brings them to
     the site; what emotional state they arrive in; what they need to believe before
     they will act. Primary and secondary.
   - **Business goals** — the single action they most want a visitor to take, and the
     next-best one.
3. Ask for proof points (funding, investors, founders, customers, partners, press) and
   any vocabulary notes — preferred product names, naming collisions with better-known
   unrelated brands, known inconsistencies to flag rather than adopt. These are
   optional; do not block on them.
4. Fill in what the user told you. Anything they did not answer stays as the template's
   bracketed placeholder — never invent a fact to fill a gap, and never infer audiences
   or goals from the site itself. Inventing them defeats the purpose: the reports would
   then be graded against the site's own assumptions.
5. Write `<cwd>/context/company.md`.
6. Copy `references/corrections-template.md` to `<cwd>/context/audit-corrections.md`, header filled
   in, corrections section empty.

Migration: if a legacy single context file exists — `<cwd>/site-context.md`, or one
loose `.md` in cwd — move it to `context/company.md` rather than starting fresh, and
tell the user you did.

---

## Mode B — Capture feedback

Use when the user reacts to findings from a completed audit.

Work through their feedback one item at a time. For each, classify it, then act:

### 1. A fact about the company is wrong
*"We're not a custody provider." "Guardian isn't a product, it's a backend."*

→ **Edit `company.md` in place.** Replace the wrong statement. Do not append a
correction next to it.

### 2. An audience or goal is wrong or has changed
*"Developers are primary now." "We don't care about retail."*

→ **Edit `company.md` in place**, same as above. These rewrite how every future report
is prioritized, so confirm the new framing back to the user before writing.

### 3. A finding was a false positive, miscalibrated, or irrelevant to this business
*"Word count doesn't matter for us." "That severity is way too high." "Stop telling us
to add a blog."*

→ **Append a rule to `audit-corrections.md`**, in the format that file specifies:
imperative rule, scope in parentheses, why, date.

Scope narrowly. The user's complaint is about a specific finding; the rule should be
about that finding's class, not its whole topic. If you cannot state a scope narrower
than "this entire kind of analysis", the feedback is probably category 4 or 5.

### 4. A one-off reaction with nothing durable in it
*"This section reads a bit long."*

→ **Write nothing.** Acknowledge and move on. Persisting taste reactions as rules
accumulates noise that degrades every future run.

### 5. A genuine defect in the audit skills themselves
*The orchestrator briefed the agent with a claim that was wrong for any site. A report
skill's severity ladder is miscategorizing something universally.*

→ **Write nothing to the context directory.** Tell the user this looks like a skill
bug, name the file that needs changing (`skills/audit-website/SKILL.md`,
`skills/seo-report/SKILL.md`, `skills/messaging-report/SKILL.md`), and offer to fix it
there.

This is the category most easily mistaken for category 3. The test: **would this
correction be true when auditing a completely different company's site?** If yes, it is
a skill bug, and writing it into one site's corrections file papers over a defect every
future audit of every other site will keep hitting.

---

## Confirm before writing

Never edit the context directory silently. Show the user what you intend to write —
the exact new or replaced text, and which file it lands in — and get their agreement.
This is their source of truth, and a wrong entry here quietly distorts every future
audit.

Batch the confirmation: classify all their feedback first, then present the whole set
of intended edits at once. Do not interrupt after each item.

---

## Keeping the corrections file healthy

`audit-corrections.md` is injected into every future run, so it cannot grow without
bound.

- **Cap it at roughly 25 active rules.** Past that, consolidate before appending:
  merge rules that say the same thing in different words, and move rules the user has
  contradicted to the `## Retired` section with a note.
- **Supersede rather than duplicate.** If a new correction contradicts an existing
  rule, retire the old one in the same edit. Two live rules that disagree make the
  report agent's behavior arbitrary.
- **Watch for over-fitting.** Rules suppress findings. A corrections file that has
  grown broad enough to silence whole categories of analysis produces a flattering,
  useless audit. If you notice the accumulated rules trending that way, say so.

---

## Reporting back

Tell the user, briefly: which files you changed, how many rules the corrections file
now holds, and anything you deliberately did not persist — especially category 5 items,
since those need a real fix elsewhere.
