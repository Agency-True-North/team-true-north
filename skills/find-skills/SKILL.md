---
name: find-skills
description: Discover and install agent skills from the open skills ecosystem when you ask "is there a skill for X", "find a skill that…", "can you do X", or want to extend what Claude can do. Use it before building a workflow from scratch — an installable skill may already exist.
---

# Find Skills

Package manager for the open agent-skills ecosystem (`npx skills`). Use it to check whether a battle-tested skill already exists before hand-building a process.

## When to reach for this

- The user asks "is there a skill for X" / "find a skill that…" / "can you do X"
- A task looks common enough that someone has likely packaged it
- The user wants a new capability added to their workspace
- Before building a multi-step workflow from scratch — check for an existing skill first

## Commands

- `npx skills find [query] [--owner <owner>]` — search (interactive or by keyword)
- `npx skills add <owner/repo@skill> -g -y` — install globally, skip prompts
- `npx skills check` — check for updates
- `npx skills update` — update all installed skills

Browse + leaderboard: https://skills.sh/

## How to run it

1. **Name the need** — domain + specific task (e.g. "video → captions", "PDF export").
2. **Check the leaderboard first** at https://skills.sh/ — the most-installed skills for a domain surface there.
3. **Search** if the leaderboard doesn't cover it: `npx skills find <specific keywords>`. Specific beats broad ("react testing" > "testing"); try synonyms if the first term is dry.
4. **Vet before recommending** — never recommend on search-rank alone:
   - Install count: prefer 1K+, be wary under 100
   - Source: official owners (`anthropics`, `vercel-labs`, `microsoft`) > unknown authors
   - Repo stars: <100 stars = treat with skepticism
5. **Present the shortlist** — skill name + what it does, install count + source, the exact `npx skills add …` command, and the skills.sh link. Recommend one, don't dump the whole list.
6. **Offer to install** only on the user's go: `npx skills add <owner/repo@skill> -g -y`.

## Check what's already installed first

Look in `.claude/skills/` (this project) and `~/.claude/skills/` (global) before searching the ecosystem. Most recurring work is already covered by a skill the team built. Only go outside for a genuinely new capability.

## If nothing good exists

Say so plainly, then either do the task directly or offer to scaffold a new skill:
`npx skills init <name>` — then write the `SKILL.md` in the same locked format as the others in `.claude/skills/`.
