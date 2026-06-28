# Git Remote Setup Assistant Design

## Goal

Add a safe, step-by-step Git remote setup assistant for `clinical_differential_support` so the Deployment Operations Center can move past `ready_for_remote_setup` without asking the user to invent raw Git commands.

## Context

The clinical product is locally complete and deploy-ready, but the workspace has no configured Git remote. Render Blueprint deployment needs the project pushed to a supported hosted repository before Render can read `render.yaml`. This phase must make the next step executable while staying within the safety boundary: no cloud account creation, no credential capture, no password storage, no automatic push unless explicitly requested, and no clinical workflow changes.

## Options Considered

1. Keep showing raw Git commands in Deployment Operations Center.
   - Low code cost, but it leaves the user without validation or guardrails.

2. Add a local command-line assistant and Windows wrapper.
   - Recommended. It can validate the URL, refuse credential-bearing URLs, avoid remote overwrites, and explain the next action in Chinese-first output.

3. Integrate directly with GitHub/Render APIs.
   - Too much credential surface for this phase. It would require external auth and would violate the current "no credential handling" deployment boundary.

## Selected Design

Create a small pure Python report/action module, `cds_core.git_remote_setup`, with a command-runner injection point for tests. It will inspect `git remote -v`, validate a supplied remote URL, add `origin` only when there is no existing origin, refuse conflicting existing origins, and run `git push -u origin <branch>` only when `--push` is explicitly present.

Expose it through `clinical_differential_support/scripts/configure_git_remote.py` and a Windows wrapper, `clinical_differential_support/Configure_Git_Remote.cmd`. The default no-argument flow reports `remote_url_required`, exit code `2`, and shows the exact next command:

```powershell
clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>
```

Supported URLs are normal hosted Git remotes for GitHub, GitLab, or Bitbucket over HTTPS or SSH. HTTPS URLs containing embedded credentials are rejected and sanitized in reports.

## Deployment Integration

Update `cds_core.deployment_status` so `ready_for_remote_setup` points to the new wrapper rather than raw `git remote add` and push commands. The public `/deployment/` page, CLI output, README, Quick Start, and DEPLOYMENT guide will describe the assistant as the next step.

## Safety Scope

- Does not create GitHub, GitLab, Bitbucket, or Render accounts.
- Does not ask for, store, print, or transform passwords or tokens.
- Does not run `git push` unless `--push` is explicitly provided.
- Does not overwrite a different existing `origin`.
- Does not change clinical data, diagnosis logic, treatment logic, medication logic, or patient data handling.
- Does not touch TWQuant, broker APIs, trading flags, or live-order behavior.

## Verification

Use TDD:

1. Add failing tests for missing URL, invalid credential-bearing URL, adding origin, conflicting origin, explicit push, CLI JSON/text output, Windows wrapper safety, deployment status integration, and docs links.
2. Verify the targeted test command fails before implementation.
3. Implement the minimal assistant and integrations.
4. Verify targeted tests pass.
5. Run the full Django regression, system check, live smoke, evidence recorder, Final_Check, CRLF checks, whitespace checks, credential scans, and trading-safety scans.
