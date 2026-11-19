# Contract Authority rollout contract

This remains a non-financial, one-hour organization self-use authority. Plane
owns person authentication, membership, host eligibility and admission. The
fixed policy is described and hashed by `POLICY_REVISION`; authenticated metadata
also reports the built source revision. Neither field is independent attestation.
Existing contract bytes, IDs and original expiry are unchanged by attribution.
Old builds without attributed metadata are unavailable for live canary admission.

`canary.Binding` defaults disabled. The deployment owner must supply trusted
private baseline/candidate routes, TLS peer identity, a scoped authority credential,
and declared fixture subjects before enabling it. Validate authenticated metadata
before evaluating a decision, and compare the complete original record on replay.
Timeouts, missing metadata, wrong revisions, malformed decisions and unexpected
statuses are unavailable; they cannot substitute for an expected denial. No
runtime scheduler, TLS binding, production route or credential is installed here.

The existing Infra scheduled authority fixture uses separate locked baseline and
candidate environments with actual owner migrations and APIs, one disposable
PostgreSQL store and in-process ASGI transport. It exercises both-direction record
reads, first writes by each build, code rollback retaining the current database,
restart, cross-tenant and changed-party refusal, and original-expiry refusal.
Expiry uses an explicit clock input at the stored boundary instead of an hour wait.
Fixture subjects and lease IDs are checked into Infra. Private per-run credentials
are removed with the fixture. No shared validation is dispatched by hand.

Current owner migration is the existing additive table creation. Its idempotence
and rollback readability are checked; this is not a claim of a new production DDL
transition. A separate PR database contract adds an optional fixture column to
check current explicit-column inserts. That column is a schema double, not an
owner migration or a claim that an older positional writer supports that expansion.
Future real schema expansions must pass the same baseline/current checks; retain
schema during code rollback and defer contraction until older writers are retired.

Infra #1967 retains live route/identity/credential bindings, supported version
windows, actual schema-transition qualification and measured observation thresholds.
The isolated checks do not qualify deployed Plane eligibility, TLS or production
recovery. Billing and inactive bindings stay disabled.
