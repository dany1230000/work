# Reviewer access implementation plan

## Objective

Replace the default admin-login redirect for reviewer write routes with a product-level reviewer login flow while preserving strict staff-only governance writes.

## Steps

1. Add tests for reviewer login rendering, protected-route redirects, staff login continuation, and non-staff blocking.
2. Add a local `staff_required` decorator that redirects to `cds_core:review_login`.
3. Add reviewer login/logout class-based views and URL routes.
4. Replace the existing Django admin staff guard on governance write routes.
5. Add a Chinese-first bilingual login template and header login/logout controls.
6. Update README and progress notes.
7. Run targeted tests, full tests, Django check, safety scan, restart the local server, and live-verify the access flow.

## Constraints

- No hardcoded credentials.
- No credential logging.
- No patient-identifying data.
- No diagnosis or treatment order behavior.
- No changes under unrelated TWQuant or ShopReport workspaces.
