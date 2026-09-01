# ADR-0001: Deploy Audio-to-Sbobina as a separate Vercel project

Date: 2026-09-01
Status: Accepted

## Context

`sbobby-web.vercel.app` currently serves a working medical-study dashboard. Its
deployed source cannot be recovered from this checkout or the reachable Git
history, while the local `sbobby-web/` application tree is empty. Replacing that
deployment would destroy existing product behavior and contradict the user's
request to create a new app.

## Decision

Keep `sbobby-web/` as the repository source directory required by the feature
specification, but link and deploy it to a new Vercel project named
`audio-to-sbobina`. Do not change, promote over, alias to, or copy secrets from
the existing `sbobby-web` Vercel project.

## Consequences

- The existing Sbobby production application remains available and unchanged.
- Audio-to-Sbobina receives its own previews, production deployment, domains,
  environment variables, budgets, and release history.
- The new app must be configured independently; existing Sbobby credentials are
  not inherited.
- Local implementation remains scoped to `sbobby-web/`, so the slice paths and
  repository rules do not need a directory migration.

## Alternatives Considered

- Replace the existing `sbobby-web` deployment: rejected because it would
  overwrite a live product whose source is not present locally.
- Reconstruct the live application from deployment artifacts: rejected because
  the source artifacts are unavailable and reconstruction is outside this app's
  product scope.
