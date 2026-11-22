# Contract authority ownership

## Host and CI test boundary

Do not run, plan, or propose integration, end-to-end, or full-flow tests on
hosts, VMs, or shared resources. Those run only in CI and the nightly batch
against main. In PRs, issues, comments, plans, and chat, report unit and
contract test results only. Never use the words l-i-f-e-c-y-c-l-e,
r-e-c-e-i-p-t, or e-v-i-d-e-n-c-e outside .github/workflows.

Close the issue when its PR merges with green CI. Do not leave issues open
pending the nightly batch or any live run. Nightly failures are filed as new
issues.

This repository owns only durable non-financial organization self-use contracts.
The plane authenticates the person and verifies membership, host ownership and
admission. Do not add billing, payments, AIuditor policy/execution, fake
certification or a successful fallback when authority/storage is unavailable.

Run `bash scripts/check-package.sh`; source, wheel and rebuilt sdist must execute
the same tests without skips. Preserve the one-hour original expiry across retries.

Never create or change version tags or publish/promote/replace/delete releases
without explicit owner approval for that specific action. Preparing artifacts,
merging code and continuing work are not release authorization. Do not add human
approval gates, required reviewers or branch protection without a specific owner
request. Private CI uses `[self-hosted, linux, x64, debrunner]`.

## Nightly integration batch

No agent runs integration or end-to-end tests by hand on hosts
or other shared resources, and none run those suites outside CI. On a pull
request, agents run only unit and contract tests. CI may add a smoke check
scoped to the services the pull request touches. A toggle or configuration
change needs a unit or contract test for that change, not a full integration or
end-to-end suite.

The full integration suite runs once as a nightly CI batch against main.
That batch uses a single concurrency group and cancels any run it supersedes.
When a nightly run fails on something whose issue is already closed, CI files
a new issue for that failure and links the closed issue when one exists.

CI results and full integration output are not a Product Sign-off gate. Green
CI and clean reviews are enough for Sign-off.

Authorized CI workflows, including test-bundle publication and existing smoke
or owner-integration jobs, may keep running in CI. Agents must not start or
repeat those jobs by hand on shared hosts.

## Service deployments and binary provenance

Each TEST service automatically tracks the latest PR merged into its repository's default branch. Deploy the tested build through a moving TEST channel. Do not pin running services to versions, commit SHAs or image digests, require manual pin updates, or require peer services to run matching builds. Preserve patch compatibility, including during early development, and verify it through the service contract.

Use exact versions and digests for downloadable bundles and to record or verify which binary was built, tested or released. A running service may report its revision for diagnostics. Production follows its existing promotion policy and explicit release authorization.

## Scope and new resources (required)

### Stay in your repo
- Only change files in this repository. Don't edit another repo's code, workflows, deploy config, Terraform or registry references, even to unblock your own run.
- When a failure comes from another repo or service (a broken dependency, image, workflow, setting or API), open an issue in the owning repo, or comment on an existing one, with the failing run link and the error. Link it from your PR or issue, then stop work on that path and wait. Don't build a workaround, a copy, or a parallel path around it.
- Don't help another service's failing run unless an issue in that service's repo assigns the work to this repo.

### Design note before new resources
- Before adding any new Azure or cloud resource type, new service, new repository, new registry, Key Vault, database server, workspace or environment, or a second copy of anything that already exists, open a design note issue that says what it is, why the existing one can't be used, and its cost. Wait until Chris approves it in that issue.
- The PR that implements it must link the approved design note. PRs that add such resources without one will be closed.
- All cloud resources are declared in Terraform in FyberLabs/infra. Never create, change or delete cloud resources by hand (CLI, portal, SDK or scripts).
