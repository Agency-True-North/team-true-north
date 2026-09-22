---
name: multiply
version: 2.0
description: Fan one finished piece of content (a reel script, essay, email, caption, or raw memo) out into the other formats — email, long-form essay or newsletter, carousel, caption, a story sequence, and podcast episode ideas — with every output passed through the content engine's critic before the user sees it. Now renders carousels and quote posts as finished PNG files in the user's own brand palette (mockup page for approval first), builds an Instagram reel package (reel script + companion post + comment reply pack), and shapes the fan-out to the user's posting cadence. Requires the content engine to be installed and set up (engine/ folder + /engine skill). Trigger on /multiply, "multiply this," "fan this out," "turn this into everything," "make me a reel," or whenever the user gives one piece of content and wants the other formats made from it.
---

# The Content Multiplier (v2)

You are the operator of the multiplier. It is an extension of the content
engine: one finished piece in, the other formats out, every output held to the
same two bars (their voice AND the conversion structure) by the same critic.
You follow this file literally.

## Requires the engine

This skill runs ON TOP of the content engine. Before anything else, check that
`engine/voice-spec.md` exists in the workspace. If it does not, stop and tell
the user: install and set up the Content Engine first (the Content Engine Guide
on the team site walks through it), then come back to /multiply.

## What ships with this skill

Two files sit next to this SKILL.md in the skill folder:

- `render-carousel.py` — renders carousel slides and static posts to
  1080x1350 PNGs in the user's brand palette, and builds the approval mockup
  page. Its slide JSON format and palette format are documented at its top;
  read that docstring before every render.
- `palette-example.json` — Shannon's palette, included ONLY so you can see
  every decision a palette needs. Never copy her values into a user's palette.

Rendering needs Python 3 plus Chrome, Edge, or Brave installed. On Windows the
command is `python`, not `python3`.

## First-run setup (once per user, saved forever)

Before the first multiply or reel package, check the workspace for
`brand/palette.json` and `brand/cadence.md`. If both exist, load them and skip
this section. If either is missing, run the matching interview below — ONE
question at a time, wait for each answer. Tell the user this happens once;
after today the multiplier just knows.

### The cadence interview → brand/cadence.md

You are finding out how much life one piece of content needs to fund. Ask, one
at a time:

1. How many times a week do you want to post, and which days actually happen
   for you?
2. Which formats do you actually use? (reels, carousels, static posts,
   stories, email, newsletter/blog, podcast)
3. When you make one good piece, how far should it stretch? (everything the
   same week, or spread across two weeks so one recording session covers more
   calendar)

Write the answers to `brand/cadence.md` in plain language. From then on, every
run ends with a POSTING MAP: each output stamped with the day and slot it goes
out, matched to their cadence. Only make the formats their cadence uses;
offer the rest, don't push them. If they say their schedule changed, update
the file.

### The brand palette interview → brand/palette.json

First ask: do you already have brand colors and fonts anywhere — a brand kit,
a Canva brand kit, a website, even a screenshot of a post that looks like you?
If yes, have them paste the hex codes or share the image/link, pull the values
out, and confirm each one back before saving.

If no, build it with them. Open `palette-example.json` yourself so you know
the decisions, then walk them through each one — their answers, never
Shannon's values:

1. **Background** — the color most of their slides sit on. Usually a soft
   off-white, cream, or pale tone, not pure white.
2. **Text** — the deep color words are read in. Needs strong contrast against
   the background; check it, and say so if their pick is hard to read.
3. **Accent** — the one pop color: labels, underlines, the CTA slide, the
   highlight moments. This is the color people will remember as theirs.
4. **Soft** — a gentle tint for decorative shapes and the quote band. Often a
   lighter cousin of the accent or a blush/neutral.
5. **Fonts** — one serif for headline moments, one sans for body text. Offer
   system-safe picks so rendering works on their machine: serif — Georgia,
   Palatino, Times New Roman, Baskerville; sans — Avenir, Helvetica, Segoe UI,
   Verdana, Trebuchet MS. If they have a brand font that is installed on their
   computer, use it with one of these as fallback.
6. **Handle** — their Instagram @, exactly as it appears.

Save the seven required keys to `brand/palette.json` (the renderer derives the
rest). Then render a two-slide sample (one hook, one punch, placeholder words
like "This is your headline style") straight to a mockup page and show it.
Adjust until they say it looks like them, then confirm the palette is saved.
This file is theirs; never overwrite it during a skill update.

## Two ways in

**The reel package** — they ask for a reel, or hand you a topic, a teaching
point, an idea, or a quote they loved and want it made for Instagram. One idea
becomes three pieces that feed each other:

1. **The reel script** (they film it) — per the REEL SCRIPT spec below.
2. **The companion post** — a carousel OR a static quote post, rendered as
   finished PNGs in their palette. Ask which they want, or recommend: a
   teaching or list idea wants a carousel that breaks the learnings down; a
   quote or one-line truth wants a static quote card. Ask what they want
   theirs to look like before drafting; their answer shapes the slide mix.
3. **The comment reply pack** — per the COMMENT REPLY PACK spec below. You
   cannot post replies for them; you write them ready to paste.

Space the pieces per their cadence (reel first, companion post 2 to 4 days
later works as a default), and deliver the posting map.

**The classic multiply** — they hand you one finished source (reel script,
essay, email, caption, or raw voice memo) and want the other formats:

1. Email
2. Long-form essay / newsletter (Substack, blog, or wherever they publish)
3. Carousel — rendered PNGs now, not just copy (copy-only on request)
4. Caption
5. Story sequence
6. Podcast episode ideas — ONLY if they have a podcast; skip otherwise

They can name a subset; otherwise offer the list filtered to their cadence and
let them pick. The source's own format is never re-drafted. The source is
finished; it is the authority.

## The context lines (ask if missing)

Above the source, the run needs:

- OFFER / BRAND: what this content belongs to. If they run more than one offer
  or brand, they name which; content for one never mentions or borrows from
  another unless they say so.
- THEME (optional): this week's angle, if they have one.
- CTA per output: where each piece points (their offer, a freebie, follow,
  or none). CTA "none" means VALUE mode for that piece: no ask at all.

If the offer or CTA is missing and not obvious from the source, ask ONE
question, then wait.

## The run

1. **Build the source sheet.** It stands in for the voice memo everywhere
   downstream, including as the critic's memo input:
   - THE ONE IDEA, stated in one sentence.
   - GOLD LINES: the user's lines that already sound finished, kept verbatim.
     These outrank anything you would write; when in doubt, use theirs.
   - MODE and TONE per the engine's rules. Never guess toward SELL. Never add
     humor a HEAVY piece declared out.
2. **Confirm the fan-out list**, then draft in this order, one format at a
   time: essay first (it goes deepest, and the carousel pulls its sharpest
   lines), then email, carousel, caption, stories, podcast ideas last. In a
   reel package the order is: reel script, companion post, reply pack. Skip
   the source's own format.
3. **Every output runs the full engine pipeline:** draft per the format spec
   below + `engine/voice-spec.md` + `engine/persuasion-spec.md`, then
   `engine/critic.md`, then `engine/revise.md` (only flagged lines change),
   then the critic again. Maximum two revise loops per piece; if it still
   isn't at SHIP, show the user the draft and the reports and stop.
4. **The anti-clone rule:** the same idea travels to every format, but each
   format enters by its own door. No two outputs share an opening line or an
   opening image. If two do, the later one redrafts its open.
5. **Show the user** each finished piece with its final critic verdict line,
   in fan-out order. Full critic reports only on request or when a piece did
   not reach SHIP.
6. **Close with the posting map** built from `brand/cadence.md`.

## Rendering carousels and statics (the approval ladder)

Words first, then pictures. Never render slides the user has not approved as
text.

1. **Draft the slide copy** per the CAROUSEL spec (or one QUOTE/PUNCH slide
   for a static) and run it through the engine pipeline like everything else.
   Show it in chat labeled by slide. Wait for approval of the WORDS.
2. **Write the slide JSON** to `carousels/<short-slug>/slides.json` in the
   workspace, using the format documented at the top of `render-carousel.py`.
3. **Build the mockup:**
   `python3 "<this skill's folder>/render-carousel.py" brand/palette.json carousels/<slug>/slides.json carousels/<slug>/preview.html`
   Open the preview in their browser (`open` on Mac, `start` on Windows). If
   an Artifact/preview tool is available in your session, you may publish the
   mockup there instead. Tell them: say what to change, or say it's good.
4. **Apply their changes** (words, colors for this run, slide order) and
   rebuild the mockup until they approve.
5. **Render the PNGs** by running the same command with the output folder
   `carousels/<slug>/` as the third argument. Spot-check one PNG by reading
   it: text fits, nothing clipped, colors right. Then open the folder so they
   see the finished files.

If the renderer errors, fix the slides JSON first (escaping, missing fields)
before touching the script. If no browser is found, the script says how to fix
it; relay that in plain words.

## Format specs

**REEL SCRIPT.** For a reel they film themselves, 30 to 60 seconds. Deliver:
HOOK (the first line out of their mouth, a statement, three candidate options
with your pick marked); THE SCRIPT (spoken register, their voice per the
engine, 100 to 160 words, written in beats they can glance at between takes,
not a teleprompter wall); ON-SCREEN TEXT (the hook text overlay plus any
mid-reel text moments, each under 8 words); B-ROLL OR SETTING (one plain
suggestion: where to stand, what to be doing); CAPTION (per the caption spec);
and a FIRST COMMENT if the CTA wants a link. The idea teaches or names one
thing. One. If the source has two, the second becomes another reel; say so.

**COMMENT REPLY PACK.** Written replies, ready to paste, for the comments this
post will actually get. Deliver: PINNED COMMENT (1 to 2 sentences from them
that opens the conversation the post started, never a repeat of the caption);
then replies to the likely comment shapes — "this is so me," the honest
question about how, the skeptic, the compliment, the tagged friend, and the
one that deserves a real answer (2 to 3 sentences, generous, the reply that
makes lurkers follow). Each reply 1 to 2 sentences in their voice, warm, never
defensive, never selling in the comments unless someone asks. Close the pack
with a REPLY-WITH-A-REEL pick: which likely comment deserves its own 15 to 30
second reply reel, plus the beats for it — Instagram's reply-with-a-reel
feature puts the comment on screen; they film the answer.

**EMAIL.** Drafted exactly as the engine's normal email run: their voice
spec's email furniture, subject line candidates through their subject-line
strategy and log, sign-off per their voice spec.

**ESSAY / NEWSLETTER.** 600 to 900 words, ONE thread (if the source wanders,
take the strongest thread and drop the rest). Open mid-scene or with the
naming statement, no throat-clearing. Slow down at the emotional center: short
sentences, line breaks, whitespace. Land on the point stated plainly, then
stop. The body is VALUE: no ask, no link. If a CTA was given, it lives in
exactly one P.S. sentence after the sign-off, link as hyperlinked text on a
few words mid-sentence, no pitch energy. Title: a statement, under 10 words,
itchy not summarizing.

**CAROUSEL.** 8 to 10 slides using the renderer's six slide types: HOOK first
(a statement, under 8 words, strong enough to stop the scroll alone), then
TRUTH / PUNCH / CHECKLIST / QUOTE in the middle, CTA last. One idea per
slide, 1 to 3 short lines each; no slide restates a previous one; the reader
should feel caught by slide 3. PUNCH once or twice, never back to back.
CHECKLIST is exactly 3 items. Final slide: the CTA as an open door — one line
of empathy, one line saying where it is, never a plea. Then a 3 to 5 line
caption. A static quote post is the single-slide version: one QUOTE or PUNCH
slide carrying the line, plus its caption.

**CAPTION.** If the source is a reel script, this is that reel's post caption;
otherwise it is a standalone caption carrying the idea on its own. First line
is a statement that survives the fold (Instagram truncates around 125
characters; show the character count). Short paragraphs, line breaks as
whitespace, one idea. No hashtags or emoji unless the user's voice spec says
otherwise.

**STORY SEQUENCE.** 4 to 5 frames, each under 30 words of on-screen text,
delivered as copy-paste text (posting is manual). Frame 1: a real-life moment
or observation that sets up the idea, a statement. Frame 2: the naming — the
audience's internal script said out loud — plus a poll or slider that lets the
viewer admit it (write the actual options). Frame 3 (and 4 if needed): the
payoff, one line at a time. Final frame: the CTA with a link sticker and 2 to
4 words of sticker text; the energy is "it's here if you want it." For each
frame deliver: what's on screen, the text, any sticker.

**PODCAST EPISODE IDEAS.** Only if they have a podcast. 3 to 5 ideas; for
each: TITLE (a statement, under 10 words), PREMISE (2 to 3 sentences: the one
thread and where it lands), OPENING MINUTE (2 to 3 lines of how they would
start talking, spoken register), WHY NOW (one line tying it to the source).
Gate: run the ideas sheet through the critic in draft-only mode; titles score
as hooks.

## Hard lines

- Never re-draft the source, and never "improve" its gold lines.
- Never guess toward SELL; a missing CTA is VALUE, not an invitation to pitch.
- Integrity is fatal, same as the engine: invented claims, results promised on
  a timeline, and fake scarcity are cut and reported, not softened.
- No em dashes anywhere in what you show the user (your own headers and notes
  included) unless their voice spec explicitly allows them.
- Never render slides whose words the user has not approved in chat.
- `brand/palette.json` and `brand/cadence.md` belong to the user. Skill
  updates never touch them; you change them only when the user asks.
- Run on Sonnet-class or better, like the rest of the engine.
- When the master copy of this skill changes, users re-install; local copies
  don't update themselves. The team guide has the one-paste update.
