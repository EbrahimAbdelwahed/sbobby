# Log: Audio-to-Sbobina web specification

Date: 2026-09-01 00:52 CEST
Area: sbobby-web

## Summary

Completed an implementation-ready specification for a new invite-only web app
that accepts M4A/MP3, transcribes through Groq, transforms text only through
DeepSeek V4 Flash, persists canonical text locally for 30 days, creates full and
study PDFs in the browser, and provides local literal search.

The spec was synthesized from three independent drafts and then revised through
architecture, security, and refactor-clean audits. It has ten independently
verifiable slices: S00–S06, S07a, S07b, and S08. No application implementation
was started.

## Files Changed

- `specs/audio-to-sbobina-web/README.md`: canonical product/technical spec,
  decisions, contracts, slice graph, release gates, and next-agent prompt.
- `specs/audio-to-sbobina-web/slices/*.md`: ten playable implementation slices.
- `specs/audio-to-sbobina-web/visualizations/architecture.html`: ownership and
  critical-path map.
- `specs/audio-to-sbobina-web/assets/README.md`: fixture/evidence ownership.
- `dev/plans/2026-09-01-0008--sbobby-web--audio-to-sbobina-web-spec--plan.md`:
  planning record.

## Verification

- `find specs/audio-to-sbobina-web -maxdepth 3 -type f -print | sort`: all 13
  expected feature files present.
- Relative Markdown link target loop over the README and slices: all targets
  exist.
- Required-section loop over every slice: all slices contain contract, scope,
  playable artifact, acceptance, verification, regression, feedback, and DoD
  sections.
- Screenshot-tool token loop: every visual slice names `screenshot-critique`,
  `compare-screenshots`, and `preview-shots` gates.
- `rg` decision/contract checks: pinned Groq/DeepSeek models, 30-day retention,
  M4A/MP3, literal search, structural-only validation, byte caps, auth, quota,
  and sole-owner modules are present.
- `git diff --no-index --check /dev/null <each new file>`: no whitespace errors.
- `xmllint`/system `tidy`: not a valid HTML5 oracle on this host; both reject
  standard semantic HTML5 elements. The visualization remains a standalone
  browser document with balanced authored structure.

## Audit Notes

- Architecture audit returned `ACCEPT_WITH_SIMPLIFICATIONS`. Accepted changes:
  S03 no longer duplicates S05 orchestration; document merge is deterministic;
  project truth has one repository; PDF layout has one owner; rate limiting has
  explicit global state; archive transfer is split from viewer/search.
- Security audit found seven pre-release gaps. The spec now defines live-route
  CSRF/origin controls, current Clerk Organization membership and revocation,
  raw bounded audio bodies, FFmpeg/WASM resource isolation, metadata-only global
  quotas, untrusted archive revalidation, and qualified third-party
  processing/deletion claims.
- A dedicated independent security-reviewer could not be spawned because the
  team thread limit was reached. S08 still requires a fresh independent security
  review of the implementation before release.
- The required Claude/Fable draft was attempted exactly once but the local CLI
  was not authenticated. No credentials were modified; a third independent
  Codex draft was used instead.

## Notes

- The worktree already contained extensive unrelated user changes and untracked
  `dev/` material. They were not modified.
- Root NLP policy still specifies GPT-5.6 Luna. S01 intentionally creates a
  scoped `sbobby-web/AGENTS.md` documenting the user's explicit DeepSeek-only
  exception for this new app without changing root policy.
