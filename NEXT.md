# NEXT — open work, observations, suggestions

Written from memory at the end of the 2026-09-07 session, without re-reading
the tree. Re-measure any number here before acting on one.

**This is not a contract and not a source of facts.** `AGENTS.md` is the
contract, `DECISIONES.md` holds decisions, and facts come from the command that
reads the machine. If this file and the "Para quien continúe" section of
`AGENTS.md` ever disagree, `AGENTS.md` wins. Delete this file when its items
are closed rather than maintaining it -- the document set was consolidated on
purpose, and a ninth permanent root document would undo that.

## Decisions that belong in `DECISIONES.md`

**The `py` prefix.** Around 98 documented commands are written `py -m flujo
...`. `docs/CLI.md` says in its own words that `py` is what you can use instead
of `python` on Windows, and the Windows node is retired -- there is no `py`
binary, no alias, and no `python` either; the working invocation is
`.venv/bin/python`. So the documented commands do not run as printed.

It was left alone on purpose. No test fails on it: one pins the prefix
deliberately, and it passes. The prefix also appears in RD product documents,
which the language rule keeps in the operator's hands. Changing it means the
generator, 98 regenerated lines, that test, and several documents -- a
repository-wide convention, which is a decision and not a cleanup.

**The `AGENTS.md` reversal is unrecorded.** A test's docstring cites an order
from 2026-09-05 to delete `AGENTS.md` as well, leaving zero contract files.
That was reversed: the file was restored as the single entry point and
`CONTRIBUTING.md` names reading it as the mandatory first step. Neither the
deletion nor the restoration appears in `DECISIONES.md`, and a reversal is
exactly what the active document is for. It was not written by an agent because
that file holds the operator's own dated decisions.

## Observations worth acting on

**A passing test with a false docstring.**
`test_the_core_domain_routes_to_the_only_contract_that_exists` still says there
is no contract file at the root and that `AGENTS.md` was deleted. It passes
only because it checks the routing configuration and the absence of `CLAUDE.md`
and lowercase `agents.md`, not whether `AGENTS.md` exists. Underneath it is a
real question: `CONTRIBUTING.md` calls reading `AGENTS.md` mandatory, while the
test asserts `core` must not route to it. One of those two is wrong.

**Two suites, two meanings.** `pyproject.toml` selects `-m mak`, which is 13
tests. The unmarked run is 243 test files and is now green. Both are useful and
they answer different questions; a green result should say which one it was.

**Two stashes are waiting.** Labelled from memory as "pre-mision tracked
changes del operador" and "pre-mision ramas y animacion". Untouched. A stash
that outlives the session it was made in tends to be forgotten.

**`main` diverges from its remote**, roughly one commit ahead and six behind
from memory. The branch `MAK` is current and pushed; `main` was not touched.

## What this session changed here

Two failing tests were fixed. `MAPA.md` and `context/comandos.json` were
regenerated because they documented `rd-datos ingest` writing to a database
path the CLI had moved away from -- the wrong path for the command that ingests
privacy-first RD field records. And
`test_there_is_exactly_one_contract_file_and_no_case_variant` pinned zero
contract files and failed for holding one; it now pins the property the trap was
about, which is one contract and no case variant.

`tools/idioma.py` gained the dossiers tree in `AUTHORSHIP_ZONE`, alongside
`borradores/`, because that is the category the zone's own comment describes.
The baseline was not regenerated: lowering the pin to absorb new offenders
would have blunted the ratchet for the repository's own code. A Spanish
probe in `tools/` still fails it, checked.

The six sibling clones -- FARMAKSIA, VIZZ, PUPILA, XIO, LUCIDA, IRIS -- were
added to `.git/info/exclude`, the local practice already used for WACHUMA,
`flujo` and `bucle`, so they stop appearing as untracked noise.

## Not audited

Almost everything. The 243 test files were run, not read. `GENESIS.md`,
`MAPA.md`, `CAPACIDADES_MAK.md`, `MEMORIAS.md` and the `docs/` tree were not
reviewed. The RD data paths were not opened. The security surface was not
examined anywhere.

The agent memory directory was reduced from 24 files to 17 and its index from a
stale two to two live entries; the fifteen remaining are project facts that are
deliberately not loaded each session. One pointer was removed because five of
the seven documents it named were deleted in the commit that made `AGENTS.md`
the single entry point.
