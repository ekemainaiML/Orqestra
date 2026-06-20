# Orqestra Frontend

Next.js 16 frontend for the Orqestra autonomous AI workforce platform. Provides the operator dashboard, demo case library, case management, audit trail, benchmark comparison, and governance replay interface.

## Tech Stack

- **Framework:** Next.js 16, React 19
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4 with CSS custom properties (dark/light theme)
- **Icons:** lucide-react
- **API Client:** Custom REST client + SSE event streaming

## Pages

| Route | Description |
|---|---|
| `/` | Organization health dashboard — KPI metrics, active cases, quick actions |
| `/demo` | Demo case library — 4 pre-configured scenarios with launch buttons |
| `/cases/new` | New business request form with customer selection |
| `/cases/[id]` | Case detail — workflow graph, decision board, deliberation timeline, actions |
| `/cases/[id]/audit` | Full event audit trail with search and expandable payloads |
| `/cases/[id]/benchmark` | Side-by-side single-agent vs organization comparison |
| `/cases/[id]/replay` | Animated governance replay with step-through playback |

## Development

```bash
npm install
npm run dev
```

The dev server starts on `http://localhost:3000`. API requests are proxied to the backend via Next.js rewrites configured in `next.config.ts`. Set `NEXT_PUBLIC_API_URL` in `.env.local` to override the default (`http://localhost:8000`).

## Build

```bash
npm run build
npm start
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |
