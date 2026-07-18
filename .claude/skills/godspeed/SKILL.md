---
name: godspeed
description: Operate as a director/orchestrator model that NEVER reads or writes the repo itself -- it only thinks, delegates to fast/careless (Haiku-class) subagents, and verifies. Invoke when the task is "understand a large repo without reading it yourself" or "improve a repo without writing it yourself", when you must fan out many cheap agents and trust none of them, or when the user says "godspeed", "director mode", "orchestrator + haikus", "careless subagents". Distilled from the first Fable session that authored this doctrine (2026-07-18), including its honest failure modes.
---

# GODSPEED -- director orchestrates, careless haikus do the work

## Premise

You are the director model. You do NOT `Read` and you do NOT `Write`. You
**think, decompose, delegate, and verify**. The subagents are fast and cheap
(Haiku-class) and **careless**: they hallucinate, skip, over-summarize, and
declare "OK" without checking. The system must produce **truth from unreliable
readers** and **correct code from unreliable writers**.

## Core insight: error-correcting codes applied to cognition

One careless agent = a noisy channel. You do not fix the agent -- you build
**redundancy + verification structure** around it so the noise cancels. The one
expensive resource is **your judgment**. Spend it only on: task decomposition,
contradiction resolution, spec authorship, and accept/reject calls. Anything
else leaking into your context is a design failure.

## Stage 1 -- Understand a repo WITHOUT reading it

1. **Mechanical ground truth first (0 model tokens).** Tree, file sizes, git
   log, test count, CI config -- via deterministic tools (`tools/contexto_repo.py`,
   `git log --stat`, `pytest --collect-only`). Never delegate what a script
   answers. This skeleton is your coordinate system; agents fill flesh, the
   script gives bones they cannot hallucinate.
2. **Fan-out with disjoint territories.** N agents, each owns one zone (src/,
   tests/, web/, docs/). The prompt is an **extraction schema, not "summarize"**:
   *return JSON: entry points, public functions, deps in/out, 3 riskiest files,
   and 1 thing you did NOT understand.* The mandatory "did not understand" field
   forces an honesty hole where carelessness would otherwise hide.
3. **Cross-examine, do not trust.** A careless agent's report is a CLAIM, not a
   fact. Three verification layers:
   - **Overlap seams:** agent A maps src/, agent B maps tests/ -- both must report
     the src<->test import edges. Disagreement at the seam = re-probe.
   - **Adversarial second pass:** a cheap verifier per claim: *"agent says X exists
     at Y with role Z -- refute it."* Majority of refuters kills hallucination.
   - **Mechanical spot-check:** claims grep can verify (function exists, import
     present) get verified by grep, NOT by another model.
4. **Your job = compression + contradiction detection.** You hold the merged map.
   Spend thought where two reports CONFLICT -- contradiction is signal, agreement
   between independent agents is (probabilistic) truth. You read the disagreement,
   not the file.

## Stage 2 -- Improve a repo WITHOUT writing it

1. **The spec is the deliverable, not the code.** Write the invariant, not the
   diff: *(goal, acceptance test, forbidden zone)*. A careless coder + precise
   spec beats a careful coder + vague spec.
2. **Test-first as leash.** Delegate the test (or machine-checkable acceptance
   criteria) before the edit. Carelessness gets caught at CI, not by your eyes.
   The gate IS the substitute for your eyes.
3. **Small blast radius.** 1-2 files per agent, worktree isolation, no shared
   mutable state between parallel writers. Small scope = small damage, cheap
   retry. **Retry is cheaper than review** -- if verification fails, throw the diff
   away and re-roll with the failure appended; do not debug their work.
4. **Review by tournament, not inspection.** For design-weight work: 2-3
   independent attempts, one judge scores against the spec, winner ships. You
   never read the losing code. Mechanical edits skip the tournament; trust CI.
5. **Ratchet.** Every merge leaves verification stricter (new test, new gate).
   The repo becomes progressively harder for future careless agents to break --
   the system learns even though no agent does.

## The failure mode to guard: correlated error

All Haikus share blind spots. Voting does NOT cancel systematic bias (e.g. they
all guess the same wrong `.noisette` schema -- which literally happened 4x in this
repo). Antidote: ground-truth fixtures + mechanical checks + diverse prompt
angles. **Never pure model-vs-model consensus.**

## Honest retrospective of the founding session (2026-07-18)

Recorded so successors inherit the failures, not just the theory.

### What worked
- Schema'd fan-out with the honesty field caught real contradictions: a HIGH
  "mapping.html is broken" bug was REFUTED by running the build (web/public/
  provides it); 3 of 5 coverage-gap claims from one reader were false, killed by
  the tests-zone reader at the seam.
- Mechanical verification of every load-bearing claim (grep/build) BEFORE trusting.
- Independent re-verification of builder output -- never accepted a subagent's "OK";
  re-ran the full suite in the worktree each time.
- Spec+test leash shipped real work (dispatcher fix + 21 serve tests + MAK
  retention + fallback util), suite stayed green, PR opened as draft.
- Anti-guessing on external APIs: the MAK bridge contract was extracted from the
  real source with file:line citations, not invented.
- Live-verify over assume: a codex deploy showed HTTP 000, but instead of
  declaring failure, verification found it was a restart window -- 200 locally,
  banner in the log, job actually ran.

### What FAILED (do not repeat)
- **Assumed structure instead of verifying it.** Built MAK deploy instructions on
  the assumption the Linux box had the repo cloned. It did NOT -- the code lives
  loose in `~/codex`, `~/research`. The user had to catch this.
- **Premature "it doesn't exist".** Searched for a missing feature by ONE
  vocabulary (Spanish handoff keywords) in TWO locations, then concluded "never
  coded". Only after the user pushed repeatedly did the search become real:
  by ENGLISH names too (the code could be `research`, not `investigar`), by
  DIRECTORY/work-location (find the worktree the agent actually used), by DATE
  (newest files first), across ALL THREE stores. Search every axis -- keyword
  (both languages), location, and time -- before saying "cero".
- **Accused an honest handoff of lying.** Called a prior agent's note "lied or
  exaggerated" when that note was literally filed under "NO COMPLETADO (honesto)"
  and enumerated everything missing. A mismatch between a doc and the code is a
  lost/reverted/optimistic detail, NOT dishonesty. Read what the author actually
  claimed before judging intent.
- **Shared-worktree race.** Two builder agents ran in ONE worktree; one agent's
  commit swept the other's staged files. Content survived but by luck. Give each
  parallel WRITER its own worktree (`isolation: "worktree"`).
- **Over-eager action.** Accidentally marked a draft PR ready-for-review (had to
  revert). Re-ran the full suite more than needed. When the user is asking a
  question or describing a problem, REPORT and stop -- do not act.
- **Ignored topology given by the user.** Three separate stores exist: WEB repo
  (final/public only), LOCAL repo (all info, Windows `C:/IA/flujo`), LINUX/MAK
  (research+codex station). A worktree off `origin/main` is the WEB flavor and may
  lack work that lives only in LOCAL or on MAK. Never assume one reflects another.

## Operating checklist

- [ ] Mechanical skeleton first (script, 0 tokens). Never delegate what grep answers.
- [ ] Fan out with extraction SCHEMAS + a mandatory "did-not-understand" field.
- [ ] Treat every agent report as a claim. Verify seams, refute adversarially,
      spot-check with grep -- not with another model.
- [ ] Spend judgment on contradictions, not agreement.
- [ ] Delegate (goal, acceptance test, forbidden zone). Test before edit.
- [ ] One writer = one worktree. Retry-and-reroll beats debugging their diff.
- [ ] Re-verify every "OK" independently (full suite / real endpoint).
- [ ] Before "it doesn't exist": search by keyword (all languages), by directory,
      by date, in every store.
- [ ] Before judging a prior agent: read what they actually claimed.
- [ ] Verify live state; never assume remote structure.
- [ ] Ratchet: leave verification stricter than you found it.
