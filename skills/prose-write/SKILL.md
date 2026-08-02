---
name: prose-write
description: Write or rewrite prose with a pinned Claude model version (e.g. opus 4.6), keeping structure, numbers, quotes and markup byte-identical. Use whenever the user names a model version for writing, or wants a draft rewritten for voice.
allowed-tools: Bash(claude *), Bash(cat *), Bash(cp *), Bash(python3 *), Read, Write
argument-hint: [path-to-file]
---

# Prose Write

Rewrite the prose of a document without touching anything that carries meaning:
numbers, quotes, headings, tables, markup, and front matter.

The rewrite runs in a separate headless `claude` process so you can pin a
specific model version. Model choice matters for prose. Newer models tend to
write in short declarative sentences, which reads clipped and cold in
first-person authorial writing. Older Opus versions write longer, warmer
sentences. The user usually has an opinion about which one they want.

## Why a subprocess and not a subagent

The `Agent` tool's `model` parameter only accepts family aliases (`opus`,
`sonnet`, `haiku`, `fable`). It cannot pin a version. The `claude` CLI can:

```bash
claude --model claude-opus-4-6 -p "..."
```

So spawn a CLI subprocess instead of a subagent whenever the user names a
version.

## Find a valid model ID

Full model names work; date-suffixed variants and dotted forms usually do not.
Probe before committing to a long run:

```bash
for m in claude-opus-4-6 claude-opus-4-5 claude-opus-5; do
  printf "%-24s " "$m"
  timeout 90 claude --model "$m" -p "reply with exactly: OK" 2>&1 | head -1
done
```

An unavailable model returns "There's an issue with the selected model".

## Run the rewrite

Pipe the source in and capture stdout. Do not let the subprocess write files
itself, because it will hit permission prompts in headless mode.

```bash
cat brief.txt source.md > prompt.txt
timeout 580 claude --model claude-opus-4-6 -p "$(cat prompt.txt)" > rewrite.md 2> err.txt
echo "exit=$?"
```

Pass the prompt as an argument, not on stdin. `claude -p` with piped stdin
races and warns "no stdin data received in 3s".

Long documents can exceed the 600s Bash ceiling. If so, run it with
`run_in_background: true` and wait for the completion notification.

## The brief

Always include these three parts. The DO-NOT-CHANGE list is what makes the
output safe to install without re-checking every fact.

**1. Context.** Who wrote it, who reads it, what the document is for. Include
any SEO or LLM-retrieval goal, because that constrains structure.

**2. A DO-NOT-CHANGE list.** Be exhaustive and literal:

- YAML front matter, reproduced verbatim
- Heading structure and heading text: same headings, same order, same levels
- Every HTML block (`<figure>`, `<img>`, `<div>`), reproduced verbatim with all attributes
- Every markdown table: same rows, same numbers
- Every blockquote: real quotes from real people, not one word reworded, attributions and links unchanged
- Template tags (Liquid `{% include %}`, MDX, shortcodes)
- Every number, percentage, price, and estimate
- Every link URL
- Proper nouns and company names

**3. A voice spec.** Describe the target voice concretely rather than naming an
adjective. What has worked:

- Warm and conversational, like a founder writing a real email to someone who asked a genuine question. Not marketing copy, and not clipped corporate prose either.
- Let sentences breathe. Longer sentences with subordinate clauses are welcome where they carry the thought naturally.
- Confident but not boastful. The numbers do the bragging, so the prose does not have to.
- First person throughout. Use contractions.
- No em dashes. Use commas, colons, or split the sentence.
- No hype words: unparalleled, game-changing, leverage, unlock, supercharge.

Add any structural block that must keep its job. For a page targeting LLM
retrieval, say so explicitly:

> The opening paragraph must stay a compact definitional block under 80 words.
> LLMs extract it verbatim, so improve its wording, not its job.

Tell it to output the finished file and nothing else, starting at the front
matter, with no preamble and no surrounding code fence.

## Verify before installing

Never install a rewrite unchecked. Diff the invariants mechanically:

```python
import re, pathlib
src = pathlib.Path("source.md").read_text()
new = pathlib.Path("rewrite.md").read_text()

heads = lambda x: re.findall(r'^#{1,6} .+$', x, re.M)
figs  = lambda x: re.findall(r'<figure>.*?</figure>', x, re.S)
quotes= lambda x: [l for l in x.splitlines() if l.startswith('> ')]
nums  = lambda x: sorted(re.findall(r'\b\d[\d,]*\+?\b',
                 re.sub(r'<figure>.*?</figure>', '', x, flags=re.S)))

print("headings:", heads(new) == heads(src))
print("figures: ", figs(new)  == figs(src))
print("quotes:  ", quotes(new)== quotes(src))
print("numbers: ", nums(new)  == nums(src))
print("tables:  ", new.count("|---|") == src.count("|---|"))
print("includes:", new.count("{% include") == src.count("{% include"))
print("em dashes:", new.count("—"))
```

Then back up the original and install:

```bash
cp source.md source.original.md
cp rewrite.md source.md
```

Rebuild the site if there is one, and re-validate any JSON-LD or templating the
page depends on.

## Offer both drafts

Keep the pre-rewrite version alongside the new one. The user will often want to
graft a paragraph back. Say where the backup is.

## Interaction with prose linters

If the project uses `stylint` or similar, run it **after** the rewrite, not
before. Rewriting invalidates every line number, so a pre-pass is wasted work.

Expect a large raw count and do not panic at it. But do not treat the count as
someone else's problem either.

**The default is to fix, not to override.** Stylint encodes the user's house
style. Wanting a page to rank well is not a licence to ignore it. If you think
a rule should be overridden, that is a decision for the user to make, so put it
to them explicitly and get an answer before you ship. Do not bury it in a
sentence at the end of a status report and treat silence as agreement. Being
asked twice why a finding is still there means you got this wrong.

**Check the house norm before arguing structure.** Before claiming a rule is
routinely ignored in this repo, count it:

```bash
grep -l "^### " _posts/*.md | wc -l          # how many files use the construct
ls _posts/*.md | wc -l                        # out of how many
stylint _posts/<some-other-post>.md | head -1 # what a typical file scores
```

If most existing files already violate the rule, say so with the numbers and
the argument is settled. If they do not, your page is the outlier and you
should fix it.

**Genuinely unfixable, worth stating once:**

| Rule | Why it cannot be fixed |
| --- | --- |
| `semicolon` | Fires on inline CSS inside `<img style="...">`, not on prose |
| `blockquote-long` | Testimonials are verbatim quotes from real people |
| `third-person` | The author's own name in a self-introduction and signature |
| `contraction` | Fires on expanded forms at the end of a sentence, which the rule's own exemption covers |

**Judgment, not blanket fixing:** `many-commas`, `long-clause-likely`,
`long-list-likely`, `colon-inline`. Stylint's own guide says so. These fire on
well-formed long sentences, and mechanically splitting all of them recreates
the clipped, staccato voice the rewrite existed to remove. Fix the ones that
genuinely read better split, leave the rest, and say which.

**Fix these. They are real defects:**

`banned-word`, `banned-phrase`, `abstract-subject`, `choppy-rhythm`,
`contraction`, `past-tense-fragment`, `lead-in`, `prose-question`, `em-dash`,
`third-person`.

Use `--ignore` only to make a long list readable while you work:

```bash
stylint file.md --ignore semicolon,blockquote-long,many-commas,long-clause-likely
```

Then run the full check without `--ignore` at the end, and **re-run it after
every subsequent edit**, including one-line wording changes. Rewriting
invalidates line numbers, and a "quick fix" pushed without a verification pass
is how regressions ship.

**Removing bold has a side effect.** Bold labels at the start of a paragraph
(`**Weekly newsletter.** Every Monday we send it to...`) become bare sentence
fragments once the bold is stripped, and `choppy-rhythm` fires on all of them.
Rewrite those paragraphs so the label becomes the subject of a real sentence
("Our weekly newsletter goes out every Monday to..."), rather than leaving the
fragment in place.

**Renaming question-word headings.** `heading-question-word` fires on any
heading that starts with Why / Who / What / How / Where, not just literal
questions. Rename to a noun phrase, and watch for `lazy-heading` on the
replacement: "The reason for this page" trips it, "Sponsors keep this community
free" does not. Name what the section says, not what kind of section it is.

Worked renames:

| Flagged | Replacement |
| --- | --- |
| Who you reach | The audience |
| What they do | Roles |
| How senior they are | Seniority |
| Where they are | Geography |
| Where they work | Industries |
| What you can sponsor | Sponsorship formats |
| What sponsors say | Sponsor feedback |

**Findings that survive on purpose.** Some are correct to leave. In a
first-person article the author's own name in the self-introduction and in the
signature above their email will both trip `third-person`, and they have to stay.
`contraction` fires on expanded forms at the end of a sentence, which the rule's
own exemption already covers.

**Words that actually came up** in real rewrites, worth pre-empting in the
brief: `itself`, `very`, `carry` as a metaphor, `shape` as a verb, `at once`,
and `worth <gerund>` framing. Content-as-actor subjects are the most common
structural slip: "This article is that email" and "The article stays up
permanently" both need a named actor, as in "I've written that email once" and
"We keep the article up permanently".

Always tell the user which rules you overrode and why, up front and as a
question, not as a footnote. Give the raw count, the fixed count, and the count
you deliberately kept.

## Workflow summary

1. Probe for a valid model ID if the user named a version.
2. Assemble brief + source into one prompt file.
3. Run `claude --model <id> -p "$(cat prompt.txt)" > rewrite.md`.
4. Verify invariants mechanically. Do not skip this.
5. Back up the original, install the rewrite.
6. Rebuild and re-validate JSON-LD or templating.
7. Stylint pass. Fix by default; ask before overriding anything.
8. Rebuild, then report what changed and what you kept.
9. Re-run stylint after every later edit, however small, before pushing.

Expect the user to iterate on individual sentences afterwards. Keep the backup
until they say they are done.
