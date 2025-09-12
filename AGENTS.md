# AGENTS

This document defines how AI coding agents should operate in this repository. Keep changes minimal, focused, and consistent with existing patterns. When in doubt, ask for clarification.

## Project Overview

- Stack: Static HTML + CSS + Alpine.js in `src/` (no build step).
- Shell: Lightweight dev server with live‑reload in `devserver.py` serving `src/`.
- App model: `src/index.html` loads sub‑pages (`*.html`) dynamically and evals their `<script>` blocks. Navigation uses URL hash routing (updates to `location.href` / `location.hash`).

## Run Locally

- Start server: `python3 devserver.py 8002` (serves `src/` at `http://localhost:8002`).
- Live reload: HTML/CSS/JS changes under `src/` trigger a reload.

## Page Architecture

- Entry: `src/index.html` owns layout and page loading via `loadPage(name)`. It listens to `hashchange` and loads the page from `location.hash`.
- Sub‑pages: Each page in `src/` is a self‑contained HTML fragment plus:
  - A `<script>` block that registers an `Alpine.data('name', ...)` component and any page logic.
  - An optional `<style>` block (CSS nesting is used—keep it consistent, do not add a build step).
  - Markup that will be injected into `<dashboard-shell>`.
- Navigation: Set `location.href = '#some-page.html?param=value'` (or `location.hash = 'some-page.html?param=value'`). Avoid full page navigations that leave the shell.

## Data/API Conventions

- Base URL: `http://localhost:4567/` (dev). Include `Authorization: Bearer ${token}` where `token = localStorage.getItem('token')`.
- Fetching: Use `fetch(url, { headers: { Authorization: ... } })`; check `response.ok`; log concise errors.
- State: Keep page state inside its Alpine component. Avoid global variables beyond reading the token and fixed preferences. Pass per‑navigation data via query params in the hash (e.g., `#audiobook.html?id=123`).

## Code Conventions

- Language: Vanilla JS and Alpine.js only. Do not add packages or bundlers.
- Style: Follow existing patterns:
  - 4‑space indentation, no semicolons, double quotes in JS strings unless template literals are needed.
  - CSS: Use the same nested style syntax already present in `src/*.html`.
  - Minimal inline comments; prefer clear, short code.
- Components: Prefer small Alpine components per page (`Alpine.data('name', () => ({ ... }))`).
- Events: Do not use `$dispatch('load-page', ...)` for navigation. Use hash routing by setting `location.href`/`location.hash`.

## Agent Operating Rules

- Changes: Use minimal, surgical diffs. Keep file structure and naming consistent.
- Tools: Prefer ripgrep for search (`rg`) and `apply_patch` for edits. Do not introduce new tooling.
- Commits: Do not create commits or branches unless explicitly requested.
- Network: Assume restricted; do not fetch external resources during build/dev.
- Plans: Use a short plan for multi‑step or ambiguous tasks; skip for trivial edits.
- Validation: If runnable, you may suggest running `python3 devserver.py` for manual verification. Do not add tests to repos without an existing test setup.

## Common Tasks

- Add a new page:
  1) Create `src/new-page.html` with `<script>`, `<style>`, and markup following existing pages.
  2) Trigger navigation by setting `location.href = '#new-page.html'` (add query params as needed, e.g., `#new-page.html?foo=bar`).

- Edit an audiobook from the list:
  - Navigate with `location.href = '#audiobook.html?id=' + audiobook.id` (the page reads `id` from `location.hash`).

- API calls with auth:
  ```js
  const token = localStorage.getItem("token")
  const r = await fetch("http://localhost:4567/resource", {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (r.ok) { /* handle */ } else { console.error("Request failed") }
  ```

## Safety and Privacy

- Do not exfiltrate tokens or user data. Never print tokens to logs.
- Do not install dependencies or change runtime assumptions without approval.
- Avoid destructive actions (e.g., `rm`, resets) unless explicitly requested and clearly justified.

## Contribution Style for Agents

- Response style: concise, action‑oriented updates; explain what you’re about to do before running tools; summarize outcomes after.
- Keep related changes grouped; avoid drive‑by refactors outside the task scope.

That’s it—follow the existing patterns and keep edits tight.
