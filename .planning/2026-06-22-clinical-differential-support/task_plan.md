# Clinical Differential Support Planning

## Goal

Plan a professional clinical decision-support reference tool for qualified medical professionals. The MVP will focus on headache as the first chief complaint unless later evidence shows a better first slice.

## Non-Negotiable Safety Scope

- The product is not a patient-facing symptom checker.
- The product does not diagnose automatically.
- The product does not prescribe automatically.
- The product does not replace clinician judgment.
- All clinical suggestions must show source, version, review status, and last reviewed date.
- Real patient data, EHR integration, and production clinical deployment are out of scope for the first MVP.

## Current Assumptions

- Audience: qualified clinicians or supervised medical trainees.
- Market/context: Taiwan-first Chinese-language product, with enough architecture flexibility for international references later.
- First MVP: headache workflow with red flags, differential diagnosis, workup prompts, management pathways, medication-safety checks, and evidence citations.
- Tech decision is not locked yet; planning will compare options before selecting.
- Data should be structured and reviewable rather than generated free text.

## Phases

### Phase 1: Context and Boundary Research
Status: complete

- Confirm official regulatory and safety framing for clinical decision support and software as a medical device.
- Confirm evidence-source expectations for a professional tool.
- Capture relevant findings in `findings.md`.

### Phase 2: Product Approach Options
Status: complete

- Compare 2-3 viable product approaches.
- Select a recommended approach with trade-offs.

### Phase 3: Product Design
Status: complete

- Define MVP scope.
- Define core user workflows.
- Define information architecture.
- Define clinical knowledge model.
- Define audit/review workflow.
- Define safety, disclaimers, and out-of-scope behavior.

### Phase 4: Implementation Roadmap
Status: complete

- Break the product into buildable milestones.
- Identify files/modules for a future implementation.
- Define testing and validation strategy.

### Phase 5: Final Planning Summary
Status: complete

- Summarize the agreed goal, architecture, MVP deliverables, risks, and next steps.
- Do not start coding until the planning output is complete.

### Phase 6: Safe Staff Setup Entry
Status: complete

- Add a Windows-friendly staff reviewer setup entry for the local manual account blocker.
- Keep Django `createsuperuser` interactive; do not automate, print, or store credentials.
- Wire the entry into Final Gate, Launch Control, Local Setup Assistant, README, and Quick Start.
- Verify with targeted tests, full regression, system check, live smoke, evidence recorder, CRLF checks, whitespace checks, and safety/readability scans.

### Phase 7: Final Handoff Package
Status: complete

- Confirm Final Gate reports `final_complete` after the local staff reviewer exists.
- Export a fresh handoff bundle into `clinical_differential_support\verification_artifacts\handoff-bundle.zip`.
- Verify the handoff bundle with the standalone verifier.
- Re-run Final_Check and live smoke to confirm the final package matches the final-complete app state.
- Scan the handoff bundle and edited local entry files for credential/trading safety markers.

### Phase 8: Deployment Readiness Beyond Localhost
Status: complete

- Add production-safe Django settings without changing local default behavior.
- Add Render Blueprint, build/start configuration, and deployment documentation.
- Verify with targeted deployment tests, full regression, production checks, collectstatic, Final_Check, smoke, and safety scans.
- Stop before actual public deployment if Git remote, cloud login, or secrets are unavailable.

### Phase 9: Deployment Operations Center
Status: complete

- Add a deployment status report, CLI, Windows entrypoint, and public local page.
- Show the exact next external deployment action after local final-complete.
- Link deployment status from Launch Control, Final Project Gate, README, Quick Start, and Deployment docs.
- Verify with targeted tests, full regression, smoke, Final_Check, CRLF, whitespace, and safety scans.

### Phase 10: Git Remote Setup Assistant
Status: complete

- Add a safe local assistant for the `create_git_remote` deployment step.
- Validate user-supplied Git remote URLs without handling credentials.
- Configure `origin` only when explicitly given a valid remote URL.
- Push only when an explicit `--push` flag is supplied.
- Link the assistant from Deployment Operations Center and deployment docs.
- Verify with red-green targeted tests, full regression, smoke, Final_Check, CRLF, whitespace, and safety scans.

### Phase 11: Git Publish Readiness Assistant
Status: complete

- Add a read-only assistant for scoped clinical deployment package Git status.
- Detect uncommitted or untracked deployment-package files before remote setup.
- Link publish readiness into Deployment Operations Center before `create_git_remote`.
- Provide exact scoped review/stage/commit next actions without mutating Git state.
- Verify with red-green targeted tests, full regression, smoke, Final_Check, CRLF, whitespace, and safety scans.

### Phase 12: Scoped Deployment Package Commit
Status: complete

- Review the scoped deployment package at file level before staging.
- Exclude generated local verification artifacts from Git.
- Stage and commit only `clinical_differential_support`, `docs/superpowers`, `.planning/2026-06-22-clinical-differential-support`, and `render.yaml`.
- Verify Deployment Status advances from `ready_for_publish_package` to `ready_for_remote_setup`.
- Stop before Git remote setup, push, Render login, cloud account creation, or credential handling.

### Phase 13: Remote and Render Preflight
Status: complete

- Verify the scoped deployment package is still clean after Phase 12 commits.
- Check whether Git remote setup can proceed without user-provided repository URL.
- Check local GitHub CLI and Render CLI availability.
- Check whether the active GitHub connector can create a new repository.
- Record the external blocker and exact next command.
- Stop before creating a repository, configuring remote, pushing, installing CLIs, logging in to Render, or handling credentials.

### Phase 14: Git Remote Configuration
Status: complete

- Validate the user-provided GitHub remote URL for embedded credentials.
- Configure `origin` through the existing `Configure_Git_Remote` assistant.
- Do not push because `--push` was not explicitly requested.
- Verify Deployment Status advances from `ready_for_remote_setup` to the Render CLI/Dashboard step.
- Stop before push, Render login, Render deployment, CLI installation, or credential handling.

### Phase 15: Clean GitHub Publish
Status: complete

- Avoid a direct root `git push` because the current repository HEAD also tracks `tw_quant_v2/`.
- Build an isolated clinical-only publish tree from the verified package paths.
- Push only the clean clinical deployment package to `https://github.com/dany1230000/work.git`.
- Verify the remote branch contains no `tw_quant_v2/`, `shop_report_lite/`, credentials, broker/order API material, or generated verification artifacts.
- Verify local Publish Status remains `publish_package_ready`, Final Check remains `final_complete`, and Deployment Status stops at the Render CLI/Dashboard handoff.
- Stop before Render CLI installation, Render login, Render deployment, cloud account creation, or secret handling.

### Phase 16: Render Dashboard Sign-In Handoff
Status: awaiting_confirmation

- Open the Render Blueprint deeplink for the pushed clinical-only GitHub repository.
- Confirm whether the Render Dashboard can create the Blueprint without additional authentication.
- Stop at Render sign-in, GitHub OAuth, account creation, or any credential/API-key prompt.
- Keep the Render page available for the user to complete authentication.
- Stop before clicking `Deploy Blueprint` because that creates Render cloud resources and can affect account costs.
- After the user authenticates and applies the Blueprint, verify the public deployment health endpoint and deployment logs.

### Phase 17: Render Build Failure Fix
Status: complete

- Read the failed Render deploy logs before changing code.
- Fix the confirmed production build failure without changing clinical behavior.
- Verify the build script creates unmigrated `cds_core` tables before fixture loading.
- Push the scoped fix through the clinical-only publish tree.
- Let Render auto-sync/redeploy and verify `/health/` on the public URL.

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-22 | Use a professional clinician-reference scope rather than patient-facing or autonomous diagnosis. | User selected option B and asked for a professional version. |
| 2026-06-22 | Use headache as the default first MVP chief complaint. | It has clear red flags and useful differential depth for demonstrating professional workflows. |
| 2026-06-22 | Recommend a hybrid reference system: structured reviewed clinical core plus AI only for non-authoritative assistance later. | Best balance of professional depth, auditability, and future extensibility. |
| 2026-06-22 | Recommend Django + SQLite for the MVP. | Django provides auth/admin/review workflow quickly without early frontend tooling complexity. |
| 2026-06-22 | Make the product Chinese-first bilingual. | User wants Chinese as the primary language while retaining English support. |
| 2026-06-25 | Use `Create_Staff_Reviewer.cmd` as the primary local staff setup command. | The project cannot safely auto-create credentials, so the final gate must point users to an interactive wrapper while keeping raw `createsuperuser` as fallback. |
| 2026-06-26 | Treat `final_complete` as the stop condition for product development and shift the next phase to handoff packaging only. | Final Gate exit 0 proves no app blocker remains, so adding more product features would move the finish line instead of completing the project. |
| 2026-06-26 | Treat deployment as readiness work, not an automatic public launch. | The workspace has no Git remote and no Render CLI/login state, and clinical production launch requires separate approval and external review. |
| 2026-06-26 | Add a deployment operations center instead of adding more clinical content. | The remaining user pain is knowing the next deployment step; external deployment itself is blocked by missing Git remote and Render auth. |
| 2026-06-26 | Add a Git remote setup assistant instead of raw remote commands. | The Deployment Operations Center must tell the user exactly what to run next while refusing credential capture, remote overwrites, and implicit pushes. |
| 2026-06-27 | Add a publish-readiness gate before Git remote setup. | The scoped clinical deployment package is still untracked; setting a remote first could push an incomplete package. |
| 2026-06-27 | Commit the scoped deployment package locally before remote setup. | The user approved autonomous continuation, and the next blocker is a local Git package commit rather than remote/cloud work. |
| 2026-06-28 | Stop remote/deploy automation at the missing Git remote URL and missing deployment tooling. | Render requires a pushed Git repo, `gh` and Render CLI are missing locally, and the available GitHub connector cannot create a new repository. |
| 2026-06-28 | Configure the user-provided GitHub URL as `origin` without pushing. | The existing remote assistant requires an explicit `--push` flag for push operations; the user supplied a URL but not a push instruction. |
| 2026-06-28 | Publish through an isolated clinical-only Git tree instead of pushing the root repository history. | The current root HEAD tracks `tw_quant_v2/`; a direct push would publish unrelated trading research and violate the scoped clinical deployment boundary. |
| 2026-06-28 | Stop Render automation at the sign-in page. | Render deployment now requires user account authentication and possibly GitHub OAuth; credentials and account authorization are outside the safe autonomous boundary. |
| 2026-06-28 | Require explicit confirmation before clicking `Deploy Blueprint`. | The Render page states it will create a PostgreSQL database and web service, and future Blueprint syncs may affect costs. |
| 2026-06-28 | Fix Render build by adding `--run-syncdb` to the production build migration command. | Render logs show fixture loading failed because `cds_core_chiefcomplaint` did not exist; `cds_core` has no migrations and needs syncdb table creation before `loaddata`. |
| 2026-06-28 | Treat Render deploy `dep-d9096a99rddc73a8ure0` as the remote completion gate for this fix. | The deploy is for pushed commit `2a246ba`, Dashboard reports it as `live`, and the public `/health/` endpoint returns 200 with database ok. |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| Phase 10 combined patch failed on encoded Chinese context | Initial large `apply_patch` mixed new files with existing Chinese deployment-status lines | Split the patch into smaller additions and stable ASCII/command replacements; targeted tests passed |
| AIMD detail pages did not load reliably during fetch | Opened Taiwan AIMD detail URLs for PCCP and post-market software change guidance | Recorded as recheck item; did not rely on those pages for specific claims |
| Mistyped evidence-recorder workdir | First attempt used an invalid Windows path | Re-ran the recorder from `C:\新增資料夾`; evidence generation passed |
| Used Bash heredoc syntax in PowerShell for bundle scan | PowerShell rejected `<<` redirection syntax | Re-ran the same Python scan through a PowerShell here-string; bundle safety scan passed |
| Mistyped smoke-check workdir during Phase 9 | First live smoke command used an invalid Windows path | Re-ran from `C:\新增資料夾`; live smoke passed including `deployment_status` |
| Phase 11 full regression exposed a stale Phase 10 fake runner | Full regression first attempt failed when `test_git_remote_setup.py` did not handle the new publish-status git probe | Added clean publish-status handling to that fake runner; targeted and full regression passed |
| `Publish_Status.cmd --json` mixed wrapper text with JSON | Verification command could not parse the batch-file output as JSON | Added JSON-mode detection to suppress wrapper text; targeted test and live JSON parse passed |
| Phase 12 cached whitespace check found blank EOF lines | `git diff --cached --check` reported extra blank lines at EOF in 10 existing files | Removed only trailing blank EOF lines, re-staged the same scoped files, and re-ran full regression |
| Phase 13 remote setup cannot proceed autonomously | `git remote -v` is empty, `gh` is missing, Render CLI is missing, and the GitHub connector exposes existing-repo tools but no repository creation tool | Recorded the exact external blocker and next command; did not create remote, push, install tools, or handle credentials |
| Phase 15 direct root push would include unrelated tracked files | `git ls-tree -r --name-only HEAD` showed `tw_quant_v2/` is tracked in the same repository | Switched to an isolated clinical-only publish tree before pushing to the GitHub remote |
| Phase 15 PowerShell pipe corrupted `git archive` tar stream | `git archive HEAD -- ... | tar -x` returned `tar.exe: Unrecognized archive format` | Use `git archive -o <tar>` and then `tar -xf <tar>` so the archive stays binary-safe |
| Phase 15 temp Git repo lacked author identity | Initial isolated repo commit failed with `Author identity unknown` | Copied the main repo's local `Codex <codex@example.local>` identity into the temp repo's local Git config and committed without changing global Git config |
| Phase 17 first Render deploy failed during build | Render deploy `dep-d9092tn7f7vs73cg0ep0` exited with status 1 while loading `headache_mvp.json`; log showed `relation "cds_core_chiefcomplaint" does not exist` | Update Render build migration command from `migrate` to `migrate --run-syncdb` so unmigrated `cds_core` tables are created before fixtures load |
