# Reviewer access design

## Goal

Build a professional app-level reviewer access flow for the clinical governance workspace.
Staff-only governance write routes should redirect to `/review/login/` instead of the Django admin login page.

## Scope

- Add a Chinese-first, English-supported reviewer login page.
- Add a staff-only access guard for governance write actions.
- Add reviewer logout through a POST-only form.
- Keep public read-only reference views open.
- Do not add default passwords, committed credentials, patient-identifying data, treatment orders, diagnosis orders, or any trading/order behavior.

## User experience

- Anonymous reviewers can open the read-only clinical support, cases, governance dashboard, queue, source library, and item detail pages.
- Anonymous access to write routes redirects to `/review/login/?next=...`.
- Staff users can sign in from the app and are returned to the originally requested reviewer route.
- Non-staff authenticated users remain blocked from staff-only routes.
- Header navigation shows reviewer sign-in for anonymous users and a logout control for signed-in staff users.

## Protected routes

- `GET/POST /review/sources/new/`
- `GET/POST /review/sources/<id>/edit/`
- `GET/POST /review/items/new/`
- `GET/POST /review/items/<id>/edit/`
- `POST /review/items/<id>/sources/`
- `POST /review/items/<id>/decision/`

## Acceptance checks

- Tests prove protected routes redirect to `/review/login/`.
- Tests prove staff login can continue to the requested governance form.
- Tests prove non-staff authenticated users remain blocked.
- Full Django test suite and system check pass.
- Live server verifies `/review/login/`, `/review/queue/`, and an unauthenticated protected-route redirect.
