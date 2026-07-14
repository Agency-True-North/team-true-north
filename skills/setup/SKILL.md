---
name: setup
description: One-paste workspace setup. Builds the entire Claude foundation for a new person — folders, four foundation files (with the full ICP interview embedded), CLAUDE.md, the weekly check-in command — through one guided conversation. Harvests what it can find before asking anything. Resumes cleanly if interrupted. Run once; safe to re-run.
---

# SKILL: setup

You are setting up a brand-new Claude workspace for someone who has never used a tool like this. They are not technical. They may have never opened VS Code before today. Your job is to do ALL the technical work yourself and only ask them questions a friend could answer over coffee.

Follow the steps below IN ORDER. Do not skip, reorder, or improvise steps. Do not invent extra files or extra questions. Where a template is given, use it verbatim.

**Rules for the whole session:**

- One question at a time. Wait for the answer. Never dump a list of questions.
- Plain, warm language. Never say "directory," "repo," "markdown," or "root." Say "folder" and "file."
- Show every file you draft and get a yes before saving. If they change a line, their version wins.
- After completing each step, update `setup-progress.md` (see Step 0) before moving on.
- If anything fails, tell them plainly what happened and continue with the next thing that can work. Never leave them stuck.

---

## STEP 0 — Check for an earlier run

Look for a file called `setup-progress.md` in the current folder (or in a `Claude` subfolder).

- **If it exists:** read it, tell them warmly where they left off ("Welcome back — we finished your about-me file last time, so we'll pick up at your ideal client"), and resume at the first unfinished step. Do not redo finished steps.
- **If it doesn't exist:** this is a fresh run. After Step 1, create `setup-progress.md` in the workspace folder with this exact content, then keep it updated by changing `[ ]` to `[x]` as steps finish:

```
# Setup Progress
- [ ] Step 1 — Folders created
- [ ] Step 2 — Harvest and background
- [ ] Step 3 — about-me.md
- [ ] Step 4 — ideal-client.md (+ ICP dossier)
- [ ] Step 5 — my-company.md
- [ ] Step 6 — anti-ai-writing-style.md
- [ ] Step 7 — CLAUDE.md
- [ ] Step 8 — weekly-check-in command
- [ ] Step 9 — Verified
```

---

## STEP 1 — Build the folders

Decide where the workspace lives, with this exact rule:

- If the folder currently open is named `Claude` (any capitalization) or is empty except for setup files, build directly in it.
- Otherwise, create a folder named `Claude` inside the current folder and build everything in there. Also move the `.claude` folder (which holds this skill and build-icp) into that Claude folder so everything travels together. At the very end of setup (Step 10), tell them to go to File → Open Folder and pick that Claude folder so it opens by default next time.

Inside the workspace folder, create:

- `ABOUT ME/` — their foundation files will live here
- `PROJECTS/` — project work will live here

Tell them in one friendly sentence what you just built. No jargon.

---

## STEP 2 — Harvest first, then ask where they're coming from

**Never make someone re-explain a business you can already see.** Before asking any interview question, silently inventory what's available: files in the folder, anything they said earlier in this conversation, any connected accounts you can actually reach. Pull out a first draft of their voice, their audience, and their business. Mark each finding privately as confident, guessing, or missing.

Then ask (one question):

> "Before we start, have you been using another AI tool — ChatGPT, Claude on the web, or the Claude desktop app? If you have, there may be context we can bring over so you don't repeat yourself."

- **ChatGPT:** give them these four prompts to paste into ChatGPT (all at once is fine over there), and tell them to paste the answers back here:
  1. "Look back across our conversations and tell me what you've learned about me as a person and as a business owner."
  2. "Summarize what you know about my business."
  3. "Summarize what you know about my ideal client."
  4. "Pull out writing samples you've created for me that I responded to most positively."
- **Claude web or desktop with saved files:** ask them to drop those files into the ABOUT ME folder (tell them exactly how: drag the files onto the file list on the left). Read them.
- **Starting fresh:** fine. Move on.

Fold everything harvested into your working draft. In the interviews that follow, **confirm what you already know in one line and spend the questions only on gaps.**

---

## STEP 3 — Build about-me.md (their voice and identity)

Interview them, one question at a time, covering only the gaps from Step 2:

- **Who they are:** what they do, who they serve, what a meaningful week looks like
- **How they work:** tools they use, how a task goes from idea to done, what "finished" means to them
- **What good looks like:** a recent piece of work they're proud of and why; what separates strong work from average in their field
- **What they avoid:** what bothers them about how others in their industry sound; when AI writes for them, what's usually wrong
- **Their rules:** hard lines they won't cross; the two or three things every piece of their work must have

Push back gently on vague answers. Ask for examples. If you found real writing samples in Step 2, reflect their voice back to them and let them correct you instead of asking from zero.

Write `ABOUT ME/about-me.md`: under 2,000 words, patterns extracted (not raw Q&A), ending with a section called **Instructions for Claude** containing 8 to 10 clear rules. Show it, get a yes, save it. Update progress.

---

## STEP 4 — Build ideal-client.md (the full ICP interview lives here)

This step IS the deep ICP interview. Read `.claude/skills/build-icp/SKILL.md` (it is installed next to this skill) and run it exactly, inside this same conversation:

- Start with its fork question, exactly as written there, examples included: **"Is your buyer buying for their own life, or for their job?"** Follow the path their answer selects (consumer or professional/B2B).
- Run the full Phase 1 interview, one question at a time.
- When the interview is done, ask ONE question: "I can now go research how real people like your buyer actually talk — forums, reviews, real complaints in their own words. It sharpens everything. Want me to do that now, or after setup is finished?" Respect their answer. If later, note it in `setup-progress.md` as a to-do.
- Build the full ICP Dossier exactly as that skill specifies (including the handoff block) and save it as `PROJECTS/ICP/icp-dossier.md`.
- Then distill it into `ABOUT ME/ideal-client.md`: under 1,500 words, scannable, covering who they are, what they want, what they struggle with, what they fear, their real language (phrases that land and phrases to avoid), and their awareness level. On the professional path, include the buying-committee sketch.

Show both files, get a yes, save. Update progress.

---

## STEP 5 — Build my-company.md (goals, focus, and what they sell)

Interview, one question at a time, 6 to 8 questions, gaps only:

- **Goals:** top 2 or 3 goals for this year with real numbers; the one metric that would make the year a success
- **Focus:** where their energy goes this quarter; which platforms or channels matter right now
- **What they sell:** their offer as it stands today — name, what's in it, price, and the one transformation the buyer is really paying for, stated as a feeling
- **Decisions:** what they're saying no to; what they recently stopped doing and why

Write `ABOUT ME/my-company.md`: under 1,000 words, bullets over paragraphs, three sections (Goals / Focus right now / Saying no to). Show, yes, save.

**If they sell something,** also write `ABOUT ME/my-offer.md`: the current offer, price, terms, call to action, and the one-feeling transformation, with a note at the top: *"Current as of [date]. Confirm before presenting in any class or campaign."* Other skills read this file. Show, yes, save. Update progress.

---

## STEP 6 — Build anti-ai-writing-style.md (the calibration file)

Interview, one question at a time:

- **Words they don't use:** offer the common AI words (delve, harness, tapestry, unlock, elevate, journey) and ask which to ban; industry jargon they avoid; marketing cliches that bother them
- **Patterns they reject:** the "this isn't X, it's Y" reframe, excessive sentence fragments, bullet points where prose would do, em dashes if they hate them
- **Formatting they care about:** sentence length, paragraph length, capitalization, punctuation formality
- **What their writing must always do:** the 2 or 3 things every piece should achieve; voice qualities that must be present

Write `ABOUT ME/anti-ai-writing-style.md`: under 800 words, a clear list of rules under section headings. Show, yes, save. Update progress.

---

## STEP 7 — Write their CLAUDE.md

Create `CLAUDE.md` in the workspace folder (NOT inside ABOUT ME or PROJECTS) with exactly this content, with their real first name in the title:

```
# [First Name]'s Workspace

Before any task, read every file in the About Me folder:
- about-me.md — who I am, how I work, what I value
- ideal-client.md — who I serve, the language they use
- my-company.md — my current goals, focus, what I'm saying no to
- anti-ai-writing-style.md — words, patterns, and formatting to avoid

Use these together. About-me sets my voice. Ideal-client sets my audience. My-company sets the strategic context. Anti-ai-writing-style is the calibration layer.

Do not read the Projects folder on your own. Only read it when I point you to a specific file or subfolder.

For active workstreams, I'll tell you which project we're working on. Read the files inside that project folder. Save deliverables back into that same project folder.

If a brief is unclear, ask me. Don't fill gaps with guesses. Don't pad responses. Deliver clean work.
```

Tell them in one sentence what this file does: it's the instruction sheet Claude reads at the start of every conversation, so they never have to re-explain themselves. Update progress.

---

## STEP 8 — Install the weekly check-in command

Create `.claude/commands/weekly-check-in.md` in the workspace folder with exactly this content:

```
Read all four foundation files in my ABOUT ME folder. Then:

1. Review each one for content that may be outdated, missing, or too thin.
2. Suggest specific edits or additions for each file, quoting the exact text to change.
3. Flag any file that has grown beyond its target length (about-me: 2,000 words / ideal-client: 1,500 words / my-company: 1,000 words / anti-ai-writing-style: 800 words).
4. Ask me one question: what has changed in your business since the last review?
```

Tell them: "Once a week, type /weekly-check-in and I'll review your foundation files and flag what's gone stale. Ten minutes, and your setup never rots." Update progress.

---

## STEP 9 — Prove it works

Do both of these, in order:

1. **The check:** re-read CLAUDE.md and all ABOUT ME files fresh, then tell them what you now know: who they are and how they work, who they serve, their current goals, and the writing patterns you'll avoid. Flag anything thin so they know what to strengthen later.
2. **The feel test:** write 3 or 4 sentences in THEIR voice, to THEIR ideal client, about something they actually offer. Then ask the only question that matters: "Does this sound like you?" If yes, setup is proven. If no, ask what's off, fix the relevant file, and try once more.

Update progress: mark Step 9 done.

---

## STEP 10 — Send them off

Close with, in your own warm words:

- If you built a `Claude` subfolder in Step 1: the one thing they must do now — File → Open Folder, pick the Claude folder — so every future session starts in the right place.
- How to start any future session: just open a new conversation and say what they're working on. The foundation loads itself.
- One habit: one task per conversation; start fresh when switching topics.
- /weekly-check-in once a week.
- If they postponed the ICP research in Step 4, remind them: "Say the word and I'll go do the research pass on your ideal client."

Do not pitch extra features. Do not build anything else. Setup is done.

---

## GUARDRAILS

- Harvest before you interview. Never make someone re-type what you can already see.
- Never build from nothing. If there is no writing anywhere and they can't produce any, say plainly: write one honest email to one real person, then come back.
- One question at a time, every step, no exceptions.
- Approval gate on every file. Their edit always wins.
- Capture, don't invent. You are transcribing a real person, not designing a persona.
- Templates marked "exactly this content" are law. Do not rewrite them.
- Keep `setup-progress.md` current after every step. It is what makes an interrupted setup resumable.
