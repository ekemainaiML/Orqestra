# Contributing

## Getting Started

1. Fork the repository
2. Run the project locally with Docker Compose (see README)
3. Pick an open issue or feature

## Local Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # edit with your credentials

# Frontend
cd frontend
npm install
```

## Code Style

### Backend (Python)
- Follow PEP 8
- Use type hints on all function signatures
- Async-first: use `async def` and `await` for I/O
- Use SQLAlchemy 2.0-style `select()` queries (not legacy `Query` API)
- Pydantic v2 for all schemas

### Frontend (TypeScript/React)
- TypeScript strict mode — no `any` unless absolutely necessary
- Functional components with hooks
- CSS custom properties for theming (see `globals.css`)
- Use existing component library where possible (`MetricCard`, `StatusBadge`, etc.)

## Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=term-missing
```

## Pull Request Process

1. Create a feature branch from `main`
2. Write or update tests for your changes
3. Run the full test suite
4. Update documentation if changing API behavior
5. Open a PR with a clear description of the change and motivation

## Architecture Notes

### Adding a New Agent
1. Create agent class in `backend/app/agents/`
2. Register in `backend/app/agents/registry.py`
3. Add prompts and evaluation criteria
4. The agent is automatically included in deliberation pipelines

### Adding a Business Tool
1. Create tool module in `backend/app/business_tools/`
2. Use async functions
3. Return structured dicts (no ORM models from tools)
4. Tools are injected into agent contexts during deliberation

### Adding a Frontend Route
1. Create page in `frontend/src/app/` following Next.js App Router conventions
2. Add API call in `frontend/src/lib/api.ts` if needed
3. Use existing layout components (Sidebar, Header)
4. Follow the CSS variable theme system in `globals.css`
