# Plan: implementation-parent closure

Date: 2026-08-11 12:42 CEST
Area: orchestration, Cardine, Study Agent Harness
Status: immutable coordinator contract; closure only

## Goal and scope

Close existing implementation parents with verified outcomes. This is not a
specification or backlog-creation run. Do not create new specs, HR-01–HR-12 or
CP-01–CP-17 beads, architecture-closure work, opportunistic scans, duplicate
reviews, idle-capacity filler, or future work. Architecture and ownership
decisions are closed unless a concrete blocking contradiction is demonstrated.

The only parents in this run are browser sandbox, PF-05 citation, PF-06
pathname safety, optional package execution, and CA-02 transition. Keep Beads
and Agent Mail state under their canonical tools; do not edit their registries.

## Ordered frontier and SHA contract

Integrate in this order. A base SHA is immutable evidence, not permission to
integrate an unreviewed or rejected commit directly.

| Order | Existing parent | Current base / action | Required outcome |
|---:|---|---|---|
| 1 | `study-agent-harness-integration-browser-sandbox-bind-mk7z` via `.1` | `3248e0e5252543854d3c0467647147a019a0f858`; restore the public smoke in `.1` | Focused test and Terra-approved descendant; close child and parent. |
| 2 | `study-agent-harness-integration-pf05-receipt-facade-fix-04g5` via `.4` | `ad002e9fa18fa19ad77a0be1def3b3c6790b3461`; run open `.4.1/.4.2/.4.3`, then one aggregate fix if findings | Course-owned citation/replay proof and exact facade; integrate only a green reviewed descendant. |
| 3 | `study-agent-harness-integration-4jvl` | `861659dd3bf46c846d3ade3ba1f4035998b14b9f`; apply sidecar and read-only mutation fixes | No victim mutation; independent test, Terra, and Sol green; integrate reviewed descendant. |
| 4 | `study-agent-harness-integration-725b` | `76f1dc7b199b2d0fe824678584e7d6013b677537`; close package trust/child-authority findings | Bounded verified execution and cleanup; independent test, Terra, and Sol green; integrate reviewed descendant. |
| 5 | `cardine-harness-program-ca-02-39k` | Start atomically from `ca8706b6ec3bed4b0d0a781076f2571b0292f838` | Replacement commit has that exact parent, then independent test and Terra review; no Sol unless a concrete security surface appears. |

Rejected checkpoints, never final integrations or ancestors:
`2a954f05b9f0da7acee02643ae392c901bd26a14` (`2a954f0`),
`0a3a3b8906727a31d7889869a9da1fa1d3259493` (`0a3a3b8`),
`5df1e54b0552ce36d70ead9781e1a1f5b1685884` (`5df1e54`),
`861659dd3bf46c846d3ade3ba1f4035998b14b9f` (`861659d`), and
`76f1dc7b199b2d0fe824678584e7d6013b677537` (`76f1dc7`). The last two are
allowed as immutable fixer bases only where the named parent says so; they are
never final integrations. CA-02 must replace `2a954f0` atomically and must not
make it an ancestor.

## Dispatch gates

Before any lane starts, the coordinator must prove all of the following and
record the evidence in the parent report:

1. Git: `git cat-file -e <base>^{commit}` and `git cat-file -e <base>^{tree}`
   succeed for the exact full SHA; every listed worktree has a valid commit,
   correct branch, writable files, and an isolated index. Never share a
   checkout or repair a missing object during this run.
2. Beads: the canonical registry is reconciled with parent/child dependencies,
   status, and the existing reports. IDs in this plan match the registry;
   stale in-progress entries are resolved before dispatch. No registry edits by
   hand and no new bead.
3. Agent Mail: mailbox database write, identity, exclusive reservations, and
   progress/report writes succeed in a disposable probe. `Operation not
   permitted` is a hard stop; do not bypass reservations or use a shared index.
4. SHA: worker branch/worktree starts at the exact base above; `git rev-parse
   HEAD` and `git diff --quiet` are captured before edits. A rejected SHA or
   unexpected ancestor fails closed.
5. Scope: the reservation is disjoint from every active writer. One writer
   owns each path; independent-test and review workers are read-only; tests
   never edit implementation files.
6. Budget: reserve the complete cycle before launch: one Luna xhigh
   implementation or approved fixer, one independent test, one Terra xhigh
   review, one aggregated Luna fixer when findings exist, and final
   verification/integration. Add one Sol high slot for security-relevant
   surfaces. Minimum reservation is five worker stages per non-security parent
   and six per security parent; if the remaining external budget cannot cover
   every stage, pause without launching a partial wave.

Preparation baseline: root `main` is repaired at
`b77a09b29bfdf9a956dd71f2d2a514b32384500f`, equal to `origin/main`; the index
is healthy and connectivity `fsck` passes. The 1,020 pre-existing tracked
worktree differences and unrelated untracked `dev` content are outside scope;
only these two dev-memory paths may be staged or committed.

## Worker lifecycle

`immutable SHA -> Luna xhigh implementer -> independent test -> one Terra
semantic review -> Sol security review only when security-relevant -> one
aggregated Luna fixer -> final verification/integration`.

An existing implementation SHA with already-closed reports satisfies the
implementation and completed review stages; do not blind-restart it. Resume at
the first missing stage, use one aggregate fixer for all approved findings,
then rerun only the focused acceptance checks needed for that fixer. Never
create another review fan-out for the same evidence.

## Compact worker briefs

Every dispatch message must contain: goal, parent bead, full base SHA, exact
allowed/forbidden paths, invariants, known findings, acceptance criteria,
focused verification, and this report schema:

```text
parent/id + stage; base SHA; worker/branch/worktree; changed paths;
commands and concise results; report paths; verdict PASS/CHANGES/BLOCK;
findings mapped to acceptance; resulting commit SHA (or none); residual risk;
next lifecycle stage; reservation released (yes/no)
```

### 1. Browser sandbox

- Goal: restore `create_server`/`serve_forever`/`HTTPConnection`/shutdown
  lifecycle coverage while retaining the sandbox-safe handler journey.
- Parent/base: `.1`, `3248e0e5252543854d3c0467647147a019a0f858`.
- Allowed: `tests/integration/demo/TUT08/test_browser_surface.py` only.
  Forbidden: every other source/test/docs/dev/Beads/Agent Mail path.
- Invariants/findings: skip only `PermissionError` at valid loopback
  construction; all other failures fail. Existing independent test passed but
  found residual real-socket risk; Terra requested public lifecycle coverage
  and flagged private seam coupling.
- Acceptance: public lifecycle smoke is restored; constrained handler,
  malformed-request, framing, and shutdown behavior remains covered.
- Focused verification in the Harness worktree:
  `python3.12 -m pytest -q tests/integration/demo/TUT08/test_browser_surface.py`;
  repeat with `python3.13`; then
  `python3.12 -m ruff check tests/integration/demo/TUT08/test_browser_surface.py`;
  `python3.12 -m mypy`; `git diff --check`.

### 2. PF-05 citation

- Goal: close course-owned citation provenance, bounded replay, timestamp
  migration, and exact public facade behavior.
- Parent/base: `.4`, `study-agent-harness-integration-pf05-receipt-facade-fix-04g5`,
  base `ad002e9fa18fa19ad77a0be1def3b3c6790b3461`.
- Allowed: the eleven base-touched paths only:
  `src/study_agent/api/sources.py`, `src/study_agent/application/export.py`,
  `src/study_agent/ingestion/projection.py`,
  `src/study_agent/retrieval/content.py`,
  `src/study_agent/tutor_snapshot/reader.py`,
  `tests/architecture/test_public_facade_boundaries.py`,
  `tests/contract/sources/test_source_revision_contract.py`,
  `tests/contract/test_public_sources_facade.py`,
  `tests/integration/test_source_projection_replay.py`,
  `tests/security/test_pf05_source_remediation.py`,
  `tests/unit/retrieval/test_content.py`. Forbidden: all other paths,
  registry/config/spec changes, and unrelated refactors.
- Invariants/findings: one course-owned authority; no public self-mintable
  binding; exact course/event/source/revision/chunk/substrate/unit proof;
  <=16 MiB pre-decode bound; immutable bytes; no-snippet v0.1 compatibility;
  reports for earlier `5df1e54` findings are already incorporated into `.4`.
- Acceptance: open `.4.1` independent test, `.4.2` Terra review, and `.4.3`
  Sol review pass against `ad002e9`; apply all approved findings once in `.4`;
  mixed-history replay/export/tutor/FSRS and facade exactness remain green.
- Focused verification:
  `python3.12 -m pytest -q tests/contract/sources/test_source_revision_contract.py tests/contract/test_public_sources_facade.py tests/integration/test_source_projection_replay.py tests/security/test_pf05_source_remediation.py tests/unit/retrieval/test_content.py`;
  repeat with `python3.13`; `python3.12 -m ruff check src/study_agent/api/sources.py src/study_agent/application/export.py src/study_agent/ingestion/projection.py src/study_agent/retrieval/content.py src/study_agent/tutor_snapshot/reader.py tests/architecture/test_public_facade_boundaries.py tests/contract/sources/test_source_revision_contract.py tests/contract/test_public_sources_facade.py tests/integration/test_source_projection_replay.py tests/security/test_pf05_source_remediation.py tests/unit/retrieval/test_content.py`; `python3.12 -m mypy`; `git diff --check`.

### 3. PF-06 pathname safety

- Goal: make central SQLite observation fail closed and prevent sidecar victim
  mutation while retaining the accepted pathname-continuity guarantee.
- Parent/base: `study-agent-harness-integration-4jvl`,
  `861659dd3bf46c846d3ade3ba1f4035998b14b9f`.
- Allowed: the thirteen base-touched paths:
  `src/study_agent/adapters/filesystem/repository_target.py`,
  `src/study_agent/adapters/sqlite/{__init__.py,_database.py,capability_gap_store.py,event_store.py,fts_retrieval.py,lexical_surfaces.py,lifecycle_observer.py,run_store.py}`,
  `src/study_agent/cli/repository.py`,
  `tests/contract/event_store/test_sqlite_event_store.py`,
  `tests/integration/test_capability_gap_sqlite.py`,
  `tests/security/test_pf06_sqlite_path_continuity.py`. Forbidden: every other
  path, A/B/restore work, registry/config changes, or unrelated refactor.
- Invariants/findings: fd-relative regular no-symlink `st_nlink==1` retained
  identity for `-journal/-wal/-shm`; reject hardlinks; observation may not
  create/delete/truncate/chmod/modify main or sidecars; fail closed on live
  WAL, mutable/missing SHM, and hot rollback journal; typed redaction stays.
- Acceptance: add the separate-process snapshot, each-sidecar victim,
  hot-journal, writable-WAL/checkpoint, cleanup/fd, and typed-redaction
  regressions; independent test, Terra, and Sol all pass on the descendant.
- Focused verification:
  `python3.12 -m pytest -q tests/contract/event_store/test_sqlite_event_store.py tests/integration/test_capability_gap_sqlite.py tests/security/test_pf06_sqlite_path_continuity.py`;
  repeat with `python3.13`; `python3.12 -m ruff check src/study_agent/adapters/filesystem/repository_target.py src/study_agent/adapters/sqlite src/study_agent/cli/repository.py tests/contract/event_store/test_sqlite_event_store.py tests/integration/test_capability_gap_sqlite.py tests/security/test_pf06_sqlite_path_continuity.py`; `python3.12 -m mypy`; `git diff --check`.

### 4. Optional package execution

- Goal: close the full reachable trust graph, interpreter/bootstrap identity,
  bounded framed IPC, process-group cleanup, and safe readiness/error mapping.
- Parent/base: `study-agent-harness-integration-725b`,
  `76f1dc7b199b2d0fe824678584e7d6013b677537`.
- Allowed: the five base-touched paths:
  `src/study_agent/adapters/host/openai_responses.py`,
  `src/study_agent/adapters/package_trust.py`,
  `src/study_agent/adapters/scheduling/py_fsrs.py`,
  `src/study_agent/adapters/workarounds/worker.py`,
  `tests/security/test_optional_package_trust.py`. Forbidden: every other
  path, new dependency, public facade, registry/config change, or unrelated
  refactor.
- Invariants/findings: no claim of a complete hostile-code sandbox; trust is
  host-owned and fail-closed; authenticate transitive dependencies,
  interpreter/bootstrap and child outcome/EOF; prevent mutable export
  substitution; terminate/reap process groups; safe CWD; validate key format
  without client construction; bounded `PdfWorkerError`.
- Acceptance: hostile transitive finder, ancestor bootstrap, same-stat,
  descendant exit, export mutation, forged success/bad exit, secret CWD,
  valid framed subprocess, and invalid readiness regressions pass on one
  reviewed descendant; independent test, Terra, and Sol approve.
- Focused verification:
  `python3.12 -m pytest -q tests/security/test_optional_package_trust.py`;
  repeat with `python3.13`; if supported extras are present also run
  `python3.12 -m pytest -q tests/unit/adapters/host/test_openai_responses.py tests/unit/adapters/scheduling/test_py_fsrs.py tests/unit/adapters/workarounds/test_pdf_markdown.py`; `python3.12 -m ruff check src/study_agent/adapters/host/openai_responses.py src/study_agent/adapters/package_trust.py src/study_agent/adapters/scheduling/py_fsrs.py src/study_agent/adapters/workarounds/worker.py tests/security/test_optional_package_trust.py`; `python3.12 -m mypy`; `git diff --check`.

### 5. CA-02 atomic transition

- Goal: implement the Cardine namespace expansion and narrow transition seam
  atomically, replacing the broken rename-only checkpoint.
- Parent/base: `cardine-harness-program-ca-02-39k`,
  `ca8706b6ec3bed4b0d0a781076f2571b0292f838`.
- Allowed: exactly the reservation in
  `/private/tmp/ca02-transition-architecture-contract-20260810.md`, SHA-256
  `45c1271bf3b23b58c525ec03fe2abc62f3519e327b004ce0525008b25e82a27d`:
  86 `CARDINE_OWNER` targets; the 33 listed copied-core import-point files
  with import/initializer-export edits only; the specified Cardine package
  markers/seam; overlay/audit/transition tests; and narrowly justified import
  or resource updates. Forbidden: all other `src/study_agent` edits,
  `cardine.integrations.study_agent`, copied aliases, dynamic hooks, second
  namespace, Harness dependency/lock changes, state migration, dual write,
  specs, beads, and Agent Mail state.
- Invariants/findings: exactly seven seam names and two consumers; exact 33
  import-point equality; 86 owner moves plus the verified frozen
  `flashcard_routing.py` digest; five `cardine*` entry points and no Cardine
  `study-agent*`; CA-01 ledger hashes/dispositions unchanged; no reachable
  `2a954f0` ancestor.
- Acceptance: one atomic commit whose parent is exactly `ca8706b...`; the
  transition AST/ownership/collision gates, negative imports, behavior,
  static, distribution, and full offline gates pass. Then close CA-02 before
  CA-03; CA-03 is not part of this run.
- Exact verification is the contract’s focused gate, behavior gate, full gate,
  and `git diff --check`; do not substitute a sibling checkout or
  `PYTHONPATH` injection.

## Interruption, compaction, and command discipline

- An interrupted worker that has not delivered the report schema is aborted;
  its edits are untrusted and do not count. Preserve the isolated worktree,
  reconcile its reservation, and resume only from the immutable base with a
  fresh brief. Never blind-restart or cherry-pick an unreported branch.
- Compaction is a stop signal when the worker cannot restate base SHA, scope,
  invariants, and next stage. Do not continue from memory or launch a second
  worker against the same scope.
- Use exact, narrow commands and quiet output (`pytest -q`, named tests,
  explicit paths, `--maxfail=1` for diagnosis). Write full reports to the
  named `/private/tmp` report path and return counts, verdict, changed paths,
  and residual risk only. Do not dump full files, repeat passed scans, or run
  full architecture sweeps.
- Do not count a commit or close a parent until the report links its exact
  base, descendant, commands, and review findings. Release reservations after
  the final report.

## Definition of Done and metrics

Done means all five existing parents are closed against reviewed descendants
or the CA-02 atomic replacement; every acceptance command is green; no
rejected checkpoint is an ancestor/final integration; no source-scope overlap,
unresolved blocker, or unverified worker edit remains; Beads and Agent Mail
state is reconciled through their canonical interfaces; and the final
integration report links parent -> implementation/fix SHA -> test/Terra/Sol
reports -> verification result. No new spec, HR/CP bead, architecture scan,
or filler work is created.

Track these metrics, with the five parents as the denominator:

- parent closure: `closed implementation parents / 5`;
- verified outcome: `parents with green focused + final gates / closed parents`;
- review efficiency: duplicate reviews `0`, aggregate fix cycles `<=1` per parent;
- execution hygiene: maximum WIP `<=3`, file-scope collisions `0`, blind restarts `0`, interrupted unreported attempts `0`;
- integration integrity: rejected ancestors `0`, exact-base mismatches `0`,
  final integrations linked to reports `5/5`.

Until Git object health, worktrees, Beads reconciliation, Agent Mail
writability, and full-cycle budget all pass, the Definition of Done is blocked
and the coordinator must stop without repair or partial integration.
