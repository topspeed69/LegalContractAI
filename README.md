# Legal Contract App

A small Vite + React + TypeScript app for legal document assistance: contract drafting, clause classification, compliance checks, loophole detection and case summaries. The project uses Google Generative AI (Gemini) for text generation, Supabase for backend storage, and shadcn/ui + Tailwind for the UI components.

This README explains how to set up, run, and develop the project locally.

## Table of contents

- About
- Features
- Requirements
- Quick start
- Environment variables
- Available scripts
- Project structure
- Development notes
- Contributing
- License

## About

This application demonstrates an opinionated UI and integrations for legal tasks powered by generative AI. It provides:

- Contract drafting templates
- Clause classification
- Compliance checks
- Loophole detection and analysis
- Case summaries

The app is built with:

- Vite + React + TypeScript
- Tailwind CSS and shadcn/ui components
- Google Generative AI (Gemini) REST API client (browser key via header)
- Supabase client for persistence (optional)

## Features

- Pre-built pages for common legal tasks (see `src/pages`)
- Reusable UI primitives under `src/components/ui`
- AI client using `VITE_GEMINI_API_KEY` with a strict system instruction for direct outputs
- Lightweight Supabase integration (`VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`)

## Requirements

- Node.js (18+ recommended)
- npm, yarn, or bun (project was bootstrapped with Vite)

Note: This repository includes a `bun.lockb` but the project works with npm/yarn as well. Use your preferred package manager.

## Quick start

1. Clone the repository

```powershell
git clone <repo-url> "legal-contract-app"
cd "legal-contract-app"
```

2. Install dependencies

```powershell
npm install
# or
pnpm install
# or
bun install
```

3. Create a `.env` file at the project root (see Environment variables below)

4. Start the dev server

```powershell
npm run dev
# or with pnpm/bun
pnpm dev; bun dev
```

Open `http://localhost:5173` (Vite default) in your browser.

## Environment variables

Create a `.env` file in the project root and add the variables below. Vite expects variables prefixed with `VITE_`.

- `VITE_GEMINI_API_KEY` (required for AI features) — your Google Generative API key. The client sends this in the `x-goog-api-key` header.
- `VITE_GEMINI_MODEL` (optional) — the Gemini model name to use (defaults to `gemini-2.5-flash` in code).
- `VITE_SUPABASE_URL` (optional) — Supabase project URL if using persistence.
- `VITE_SUPABASE_ANON_KEY` (optional) — Supabase anon/public key.

Example `.env` (do NOT commit to git):

```text
VITE_GEMINI_API_KEY=sk-...
VITE_GEMINI_MODEL=gemini-2.5-flash
VITE_SUPABASE_URL=https://xyzcompany.supabase.co
VITE_SUPABASE_ANON_KEY=public-anon-key
```

Security note: Do not expose secret keys in public repositories. The current AI client implementation sends the API key in a browser header (`x-goog-api-key`) which is appropriate for browser API keys. For production consider proxying requests through a backend to keep secrets server-side and to manage usage.

## Available scripts

Scripts are defined in `package.json`. Use them through your package manager, e.g. `npm run <script>`.

- `dev` — start Vite dev server
- `build` — build production assets with Vite
- `build:dev` — build using the `development` mode
- `preview` — locally preview the production build
- `lint` — run ESLint

Examples (PowerShell):

```powershell
npm run dev
npm run build
npm run preview
npm run lint
```

## Project structure

Top-level highlights:

- `src/` — application source code
	- `components/` — UI components and shadcn wrappers
	- `pages/` — route pages (e.g. `ContractDrafting.tsx`, `LoopholeDetection.tsx`)
	- `lib/` — integrations and clients (`ai-clients.ts`, `supabase.ts`)
	- `hooks/`, `contexts/`, `types/`, `services/` — utilities and app logic

Files worth inspecting:

- `src/lib/ai-clients.ts` — Gemini client and prompt composition
- `src/lib/supabase.ts` — Supabase client initialization (exports `supabase` or `null`)

## Development notes

- The AI client enforces a strict system instruction to avoid extra prose and returns raw Markdown/plain text. Be careful when editing prompts.
- Supabase client exports `null` if env vars are missing — components should handle null-safe usage.
- The UI uses shadcn-style primitive components in `src/components/ui` and Tailwind CSS.

Testing & linting

- ESLint is configured; run `npm run lint`.
- Add tests as needed — no test runner is included by default.

Building for production

```powershell
npm run build
npm run preview
```

CI recommendations

- Validate PRs with `npm ci && npm run build && npm run lint`.
- Run unit/e2e tests if you add them.

## Contributing

Contributions are welcome. Please open issues for bugs or feature requests and send pull requests with clear descriptions. Keep changes small and focused.

Before opening a PR:

- Run `npm run lint` and ensure no lint errors.
- Build the project locally with `npm run build`.

## License

This repository does not include a license file. Add a `LICENSE` file if you intend to publish the project and want to specify terms.