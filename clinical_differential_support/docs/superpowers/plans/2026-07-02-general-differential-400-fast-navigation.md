# Plan: General Differential 400 + Fast Navigation

## Phase 1: Tests

- Add catalog quality test for 400 conditions, 478 sources, no warnings, and completed `expand_condition_catalog_to_400` action.
- Add text-search regression test for the 25 new conditions.
- Add UI regression test for fast navigation status, hover/focus prefetch, and fast-nav request headers.

## Phase 2: Catalog

- Add 25 source definitions from NIH, CDC, MedlinePlus, NIAMS, NICHD, NCI, and NINDS.
- Append an eleventh generalist condition batch using the existing condition helper.
- Update the expansion target from 375 to 400.
- Regenerate the reviewed runtime JSON from the static catalog.

## Phase 3: Fast Navigation

- Add a compact live status node to the shared base layout.
- Refactor prefetch into `prefetchFastNavTarget`.
- Reuse the helper for idle nav prefetch and user-intent prefetch on hover/focus.
- Mark prefetched links with `data-fast-nav-prefetched`.

## Phase 4: Verification and Release

- Run focused red/green tests.
- Run related Django test modules and full `cds_core.tests`.
- Run both catalog validators and reviewed-catalog dry import.
- Commit and push only the phase files, excluding unrelated `home.html`.
- Smoke-test Render after deployment propagation.
