# Web Launch Guide Design

## Goal

Make the step-by-step launch flow visible inside the web app, not only in CLI output or Markdown.

## User Problem

The current project has working CLI guidance, but the first web experience is still not a guided flow. The shared page header also contains unreadable Chinese in several labels, which makes the product feel unfinished.

## Design

- Add a public `/launch/` route.
- Render `build_local_launch_status()` as a six-step guide.
- Show the current step clearly with command and URL.
- Add the launch guide to the shared navigation.
- Make `Start_Local_Server.cmd` open `/launch/`.
- Add `/launch/` to smoke checks.

## Safety Scope

- The launch guide is summary-only and local-only.
- It does not expose detailed clinical rule content.
- It does not bypass staff login.
- It does not create credentials.
- It does not add diagnosis, treatment, medication, trading, broker, or order behavior.
