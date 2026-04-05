# CoQuery Persona Review

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

Purpose:

Create a recurring evaluation snapshot using multiple product personas so the CLI does not evolve only from implementation momentum.

## 1. Product planner view

### Evaluation

CoQuery's strongest current value is not "AI SQL expert system."
Its strongest current value is:

- a SQLite-first assistant
- that can inspect schema
- run simple queries
- generate starter SQL
- and expose a path toward safer write operations

The current product risk is scope inflation.
The repository is trying to be:

- a beginner SQL tutor
- a write-safe DB tool
- a natural-language SQL generator
- a multi-DB platform
- a future expert system

all at once.

### Product direction recommendation

The product should be framed as:

`a practical SQLite-first SQL copilot for learning and lightweight local database work`

not as a full multi-DB expert platform yet.

### Planner ideas

- Add a `doctor`-style command for DB path, table count, and driver availability
- Add a `skills` command that lists supported generation patterns clearly
- Add one "safe write" walkthrough mode later, but only after the write contract is frozen

## 2. Developer view

### Evaluation

The repository is much healthier than before, but the code still shows signs of phase stacking:

- old and new docs coexist
- raw-SQL and structured ideas coexist
- SQLite-first runtime and multi-DB scaffolding coexist

### Development recommendation

The next engineering priority should be contract cleanup, not feature breadth.

### Developer ideas

- Move all command payload shaping into one dedicated contract layer
- Introduce one fixture-per-command write test set
- Reduce duplicate or stale docs that imply obsolete state
- Keep package handlers as the single runtime source of truth

## 3. Manager view

### Evaluation

The biggest management problem is not technical inability.
It is release signaling.

The project has repeatedly described future phases as complete before they were fully verified.

### Management recommendation

Use stricter release language:

- `working baseline`
- `experimental`
- `stabilizing`
- `planned`

Reserve `complete` only for slices with:

- runtime proof
- test proof
- document alignment

### Manager ideas

- Create one release gate checklist for every minor version
- Add a short "what is actually verified" section to release notes
- Make every phase claim point to one concrete command and one concrete test

## 4. QA view

### Evaluation

QA has improved, but coverage is still baseline-oriented.
The most valuable next tests are not more happy-path generation tests.
They are safety and contract tests.

### QA recommendation

The next QA focus should be:

- write flag enforcement
- warning surfaces
- affected-row contracts
- unsupported-driver behavior for PostgreSQL/MySQL placeholders

### QA ideas

- Add a smoke matrix:
  - schema
  - query
  - generate
  - insert
  - update
  - delete
  - natural
- Add one negative test per command
- Add a "docs example still works" smoke pass

## 5. Product development ideas

These are the highest-value product ideas, ordered conservatively.

### Now

- `skills` command for discoverability
- `doctor` command for environment and DB readiness
- safer write envelopes with warnings and safety levels

### Next

- beginner-friendly explain mode for generated SQL
- table-aware query suggestions from current schema
- reusable sample fixture workflow for learning mode

### Later

- real PostgreSQL and MySQL integration
- richer NL interpretation
- schema-aware optimization hints
- expert-system style learning or memory

## 6. Recommended persona review cadence

Run a short persona review at these points:

1. before starting a new phase
2. after a command contract changes
3. before claiming a release milestone

Use the same four questions every time:

- Planner: is this still the right product?
- Developer: is the architecture staying coherent?
- Manager: are we overstating maturity?
- QA: what is still unproven?

## 7. Current conclusion

CoQuery is in a good position if it stays disciplined.

The product has enough baseline value already.
The next gains will come from:

- sharper scope
- safer contracts
- more honest release signaling

not from maximum feature count.
