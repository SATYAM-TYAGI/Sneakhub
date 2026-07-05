# AI Context — Sneaker Recommendation System

Quick reference for AI assistants working on this project. Read this first before making changes.

---

## What This Project Is

A production-style **sneaker recommendation web app**. Users pick preferences (brand, category, budget, gender, color, material) and get the **top 5 most similar sneakers** with images, scores, and plain-English reasons.

Target API latency: **under 150ms** after server warmup.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React, Vite, TypeScript, React Query, React Router |
| Backend | FastAPI, Pydantic, SQLAlchemy, Alembic |
| Database | Neon PostgreSQL |
| ML | Scikit-learn Random Forest, Joblib, Pandas |
| Images | Cloudinary (URLs in DB only) |
| Hosting | Vercel (frontend), Railway/Render (backend) |
| Dataset | Kaggle CSV (~1006 rows) at `backend/data/Shoes.csv` |

---

## Architecture Rules (Do Not Break)

```
Routers → Services → Repositories → SQLAlchemy Models
```

- **Never** put business logic in routers
- **Never** put database queries in services (use repositories)
- **Never** store images in PostgreSQL — URLs only
- **Never** use FAISS or embedding-only recommendations
- **Never** use Sentence Transformers as the primary recommender
- **Never** put guides inside `backend/` or `frontend/` — use `guides/`
- **Never** over-engineer — keep code beginner friendly

---

## ML Pipeline (Critical)

Primary model **must be trained from scratch**.

```
CSV → Clean → Feature Engineering → Pairwise Similarity Dataset
  → Random Forest Regressor → Evaluate → model.pkl → FastAPI inference
```

- **Pairwise features:** match flags, price diff, color Jaccard, etc. between user prefs and each sneaker
- **Inference:** score all ~1k sneakers in memory — no FAISS needed
- **Optional rerank:** Sentence Transformers on top-20 only, behind `ENABLE_ST_RERANK=false` flag
- **Artifacts:** `backend/ml/artifacts/model.pkl` + `encoders.pkl`
- **XGBoost** is acceptable alternative to Random Forest — document swap in `ml/train.py`

---

## Data Pipeline

Offline CLI — not part of live API path.

```
Shoes.csv → clean → dedupe → search → download image → describe
  → Cloudinary upload → import DB → update pipeline_cache
```

- **Dedup key:** SHA256 of `(brand, model, type, gender, color, material)` — Size dropped
- **Search query:** multi-attribute, e.g. `"Nike Air Max 90 White Men Running Mesh"` — never model alone
- **Search provider:** pluggable interface, default SerpAPI (`pipeline/search/`)
- **Cache:** `pipeline_cache` table — rerun skips completed products with `--resume`

---

## Database (Key Tables)

| Table | Purpose |
|-------|---------|
| brands | Brand lookup |
| categories | Category lookup (CSV `Type` column) |
| sneakers | Main catalog — one row per deduped product |
| pipeline_cache | ETL resume tracking |
| pipeline_runs | Pipeline audit log |
| users | Future auth — **not MVP** |
| recommendation_logs | Optional analytics |

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for full details.

---

## API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/health` | Liveness + model status |
| GET | `/api/v1/filters` | Dropdown options |
| POST | `/api/v1/recommendations` | **Main endpoint** — top 5 results |
| GET | `/api/v1/sneakers` | Paginated browse |
| GET | `/api/v1/sneakers/{id}` | Single sneaker detail |

No auth in MVP. See [API_SPEC.md](./API_SPEC.md).

---

## Folder Structure (Key Paths)

```
backend/
  app/
    main.py              # FastAPI + lifespan model loader
    routers/             # thin HTTP only
    services/            # business logic
    repositories/        # DB access only
    models/              # SQLAlchemy ORM
    schemas/             # Pydantic DTOs
  ml/
    features.py          # feature engineering
    pairwise.py          # pairwise dataset
    train.py             # train RF, save model.pkl
    inference.py         # score at request time
    artifacts/model.pkl
  pipeline/
    run.py               # CLI orchestrator
    search/              # pluggable search providers
  data/Shoes.csv
frontend/
  src/
    pages/HomePage.tsx
    pages/ResultsPage.tsx
    components/forms/PreferenceForm.tsx
    components/cards/SneakerCard.tsx
    hooks/useFilters.ts
    hooks/useRecommendations.ts
guides/                  # user docs ONLY here
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full tree.

---

## Performance Strategy

1. Load `model.pkl` + encoders at FastAPI startup (lifespan)
2. Precompute sneaker feature matrix in memory
3. Vectorized numpy scoring over full catalog (~10ms)
4. Fetch metadata for top 5 IDs only (single DB query)
5. Optional ST rerank adds ~50-80ms — disabled by default

---

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| DATABASE_URL | backend | Neon connection |
| CLOUDINARY_CLOUD_NAME | backend | Image upload |
| CLOUDINARY_API_KEY | backend | Image upload |
| CLOUDINARY_API_SECRET | backend | Image upload |
| SERPAPI_KEY | backend | Pipeline search |
| ENABLE_ST_RERANK | backend | Default false |
| CORS_ORIGINS | backend | Vercel URL |
| MODEL_PATH | backend | Default ml/artifacts/model.pkl |
| VITE_API_BASE_URL | frontend | Backend URL |

---

## Documentation Tone

- Human, simple English — not corporate AI voice
- Slight grammar mistakes OK in comments/docs
- Module READMEs with examples required
- Comments sound like a real dev: `# just loading this once so reqs stay fast`

---

## Implementation Order

Follow [TASKS.md](./TASKS.md) — 58 tasks in 7 phases:

1. Foundation (repo, scaffolds)
2. Database (models, Alembic, repos)
3. Data Pipeline (enrichment CLI)
4. ML (train, evaluate, inference)
5. Backend API (FastAPI services)
6. Frontend (React UI)
7. Deploy + guides

---

## Common Mistakes to Avoid

| Mistake | Why It's Wrong |
|---------|----------------|
| Using embeddings as primary recommender | ML rules require trained RF/XGBoost |
| Adding FAISS | Dataset too small; rules forbid it |
| Business logic in routers | Breaks layered architecture |
| Storing images in DB | DB rules — URLs only |
| Searching with model name only | Pipeline rules — multi-attribute queries |
| Docker in MVP | Explicitly excluded from scope |
| Guides in backend/frontend | Docs rules — guides/ only |
| Skipping pairwise dataset | ML rules require it |
| Over-abstracting code | Project priority is beginner friendly |

---

## Key Design Decisions (Locked)

| Decision | Choice |
|----------|--------|
| Primary ML model | Random Forest Regressor |
| Inference | Brute-force all ~1k sneakers in memory |
| Size column | Dropped at dedupe |
| Category | CSV `Type` → `categories.name` |
| Search | Pluggable; SerpAPI default |
| Auth | Schema stub only; public API in MVP |
| Explanations | Required on every recommendation result |

---

## Related Documents

| Doc | Contents |
|-----|----------|
| [PROJECT_SPEC.md](./PROJECT_SPEC.md) | Requirements, features, NFRs |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, flows, deployment |
| [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | Tables, indexes, relationships |
| [API_SPEC.md](./API_SPEC.md) | All endpoints with schemas |
| [TASKS.md](./TASKS.md) | 58 implementation tasks |

---

## Cursor Rules

Project rules live in `.cursor/rules/`:

- `AI_RULES.mdc` — project overview and priorities
- `backend_rules.mdc` — FastAPI layered architecture
- `frontend_rules.mdc` — React, React Query, components
- `database_rules.mdc` — Neon, SQLAlchemy, no images in DB
- `ml_rules.mdc` — RF, pairwise, no FAISS, no embedding-primary
- `documentation_rules.mdc` — tone, guides/ location

Always follow these rules when generating code.
