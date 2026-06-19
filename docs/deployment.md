# Deployment

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+
- Qwen Cloud API key (`DASHSCOPE_API_KEY`)

### Backend
```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env  # edit with your credentials
alembic upgrade head
python seed/load.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## Docker (Local)
```bash
export DASHSCOPE_API_KEY=sk-your-key
docker compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Production (Alibaba Cloud)

### ECS (Backend)
1. Provision ECS instance (Ubuntu 22.04, 2vCPU/4GB min)
2. Install Docker and Docker Compose
3. Clone repo, configure `.env`
4. Run `docker compose up -d`

### RDS (PostgreSQL)
1. Create RDS PostgreSQL 16 instance
2. Configure security group to allow ECS access
3. Set `DATABASE_URL` in ECS environment

### Redis
1. Create Redis instance (or use Alibaba Cloud Redis)
2. Configure security group
3. Set `REDIS_URL` in ECS environment

### Frontend (Vercel or Alibaba Cloud)
1. Deploy frontend to Vercel:
   - Connect GitHub repo
   - Set `NEXT_PUBLIC_API_URL` to deployed backend URL
   - Deploy

### Verification Checklist
- [ ] Health check: `GET /health` returns `{"status": "ok"}`
- [ ] Demo cases load: `GET /demo/cases` returns 4 scenarios
- [ ] Deliberation runs end-to-end
- [ ] SSE stream delivers events
- [ ] Frontend loads and displays dashboard
- [ ] Qwen Cloud integration returns structured responses
