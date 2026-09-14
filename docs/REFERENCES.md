# References — citation policy & bibliography

## 0. Standard & exception

One citation standard for the whole repository: **APA, 7th edition**, per
Hanze's own library guide (Hanze University of Applied Sciences, Library,
n.d.-a) — see §7 for the exact pages this policy is built from. Every fact
pulled from outside this repo, and every piece of adapted code, is cited
in text (§2) and listed below (§5), the same way a thesis or report would
cite its sources — not with ad hoc "see this link" notes.

**One mandatory exception:** the graded report in `IEEE/` uses **IEEE's
own numbered citation style** `[1]`, `[2]`, ... with its own self-contained
reference list inside the report — not APA, and not this file. That's not
a style preference; the assignment requires "IEEE format" (E. Bergsma,
F. N. Martins, & F. J. Guzman, personal communication, September 11,
2026; see [docs/course-materials/](course-materials/), slide 3), and IEEE
format includes IEEE's citation convention. Nothing else in this
repository gets that exception.

## 1. Who this applies to

Every contributor — human or AI agent (see
[AGENTS.md, Golden Rule 6](../AGENTS.md#3-golden-rules)) — for every
artifact: `README.md`, `CONTRIBUTING.md`, ADRs, code comments and
docstrings, commit messages that state a fact. The report in `IEEE/`
follows §0's exception instead.

## 2. In-text citation (everywhere except `IEEE/`)

- Parenthetical: `(Author, Year)`.
- Narrative: `Author (Year) ...`.
- Add a page or slide number when pointing at a specific location:
  `(Author, Year, p. 4)` or "slide 6".
- Three or more authors: cite the first author followed by "et al." from
  the first citation onward (Hanze University of Applied Sciences,
  Library, n.d.-b).
- An in-text citation is never a substitute for the full entry in §5 (or
  the in-code URL required by CONTRIBUTING §10) — it points *at* that
  entry, it doesn't replace it.

## 3. Reference-list entry format

Element order: **WHO** (author/organization) → **WHEN** (year) → **WHAT**
(title) → **WHERE** (source/publisher/URL) (Hanze University of Applied
Sciences, Library, n.d.-c).

**Webpage / documentation:**

```
Author, A., or Organization. (Year, Month Day or n.d.). *Title of the
page*. Name of website (omit if identical to the author). Retrieved
Month Day, Year, from https://...
```

**Software, driver, or library** (the form to mirror when code is
adapted from it — see CONTRIBUTING §10):

```
Author or Organization. (Year). *Program name* (Version)
[Computer software]. Publisher. Retrieved Month Day, Year, from https://...
```

## 4. Personal communications — course material

Per Hanze's own rule, material a reader outside the course cannot
retrieve (a lecture, a kickoff presentation, an email) is **personal
communication**: cited in text only, never added to §5 (Hanze University
of Applied Sciences, Library, n.d.-d).

Use this exact in-text form for the project kickoff:

```
(E. Bergsma, F. N. Martins, & F. J. Guzman, personal communication,
September 11, 2026)
```

A working copy of the slides is archived at
[`docs/course-materials/`](course-materials/) for the team's own
traceability. That archive is a practical convenience — it does **not**
replace the citation form above in any text (report, docs, code comment)
that relies on it.

## 5. Reference list

Alphabetical by author/organization. Add an entry before citing a source
in text (§6).

- iRobot Corporation. (n.d.). *iRobot® Create® 3 Docs*. Retrieved
  September 11, 2026, from https://iroboteducation.github.io/create3_docs/

*(Add ROS 2 Jazzy docs, the Foxglove docs, Webots/Gazebo docs, and any
driver or library the team's code actually adapts from, as they're used —
see §6. Don't pre-populate entries for sources nothing cites yet.)*

## 6. Adding an entry

1. Open the source yourself and read the actual page — don't cite what an
   automated tool or cached copy returned without confirming it matches.
   *(While drafting this policy, an automated fetch of docs.ros.org
   returned an anti-bot challenge page, not ROS 2 content — see the
   caution below.)*
2. Format it per §3.
3. Insert it alphabetically in §5.
4. Cite it in text per §2, or in the code comment per
   [CONTRIBUTING.md §10](../CONTRIBUTING.md#10-source-attribution) — code
   comments still carry a direct URL for a quick jump, but the source
   also gets a full §5 entry so the bibliography stays complete.

> **Caution.** An automated fetch can return an anti-bot challenge or a
> stale cached page instead of the real source. Verify what you're
> citing actually is the source before adding it here.

## 7. Sources for this policy

- Hanze University of Applied Sciences, Library. (n.d.-a). *APA
  guidelines (7th)*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/apa_guidelines_7
- Hanze University of Applied Sciences, Library. (n.d.-b). *Basic
  principles of citations*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/c.php?g=696436&p=4999928
- Hanze University of Applied Sciences, Library. (n.d.-c). *Elements of
  reference list entries*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/c.php?g=696436&p=4999932
- Hanze University of Applied Sciences, Library. (n.d.-d). *Personal
  communications*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/c.php?g=696436&p=4999937
- Hanze University of Applied Sciences, Library. (n.d.-e). *Online media
  reference examples*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/c.php?g=696436&p=5026328
- Hanze University of Applied Sciences, Library. (n.d.-f). *Data sets and
  software reference examples*. Retrieved September 11, 2026, from
  https://libguides.hanze.nl/c.php?g=696436&p=5026330
