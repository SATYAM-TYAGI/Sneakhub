# Sneaker Recommendation System — API Specification

REST API served by FastAPI. All JSON endpoints use `Content-Type: application/json`.

**Base path:** `/api/v1`  
**Authentication:** None in MVP. Future protected routes will use `Authorization: Bearer <token>`.

---

## Conventions

### Versioning

All business endpoints live under `/api/v1/`. Breaking changes require a new version prefix (`/api/v2/`).

The health check lives at `/health` (no version prefix) so load balancers can hit it without knowing the API version.

### Error Response Shape

All errors return:

```json
{
  "detail": "Human readable message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

Validation errors (422) follow FastAPI's default `detail` array format for field errors.

### Pagination

List endpoints use query params:

| Param | Default | Max | Notes |
|-------|---------|-----|-------|
| page | 1 | — | 1-indexed |
| page_size | 20 | 100 | |

Paginated responses include:

```json
{
  "items": [],
  "total": 850,
  "page": 1,
  "page_size": 20,
  "total_pages": 43
}
```

### CORS

Production backend allows origins from `CORS_ORIGINS` env var (comma-separated). Typically the Vercel frontend URL.

---

## Endpoints Summary

| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET | `/health` | None | Liveness + model status |
| GET | `/api/v1/filters` | None | Dropdown options for preference form |
| POST | `/api/v1/recommendations` | None | Get top 5 similar sneakers |
| GET | `/api/v1/sneakers` | None | Paginated catalog browse |
| GET | `/api/v1/sneakers/{sneaker_id}` | None | Single sneaker detail |

### Future Endpoints (Not MVP)

| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| POST | `/api/v1/auth/register` | None | Create account |
| POST | `/api/v1/auth/login` | None | Get JWT token |
| GET | `/api/v1/users/me/preferences` | Bearer | Saved preference lists |

Documented here for schema continuity — do not implement in MVP.

---

## GET /health

Health check for Railway/Render load balancers and uptime monitors.

### Request

No parameters.

### Response 200

```json
{
  "status": "ok",
  "model_loaded": true,
  "catalog_count": 847,
  "model_version": "rf_v1"
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always `"ok"` when server is running |
| model_loaded | boolean | Whether `model.pkl` loaded successfully |
| catalog_count | integer | Number of active sneakers in memory cache |
| model_version | string | Version tag from training metadata |

### Response 503

Returned if the app is running but the model failed to load:

```json
{
  "detail": "Model not loaded",
  "error_code": "MODEL_NOT_LOADED"
}
```

---

## GET /api/v1/filters

Returns distinct values from the active catalog for populating the preference form dropdowns.

### Request

No parameters.

### Response 200

```json
{
  "brands": [
    "Adidas",
    "Asics",
    "Converse",
    "Fila",
    "New Balance",
    "Nike",
    "Puma",
    "Reebok",
    "Skechers",
    "Vans"
  ],
  "categories": [
    "Basketball",
    "Casual",
    "Fashion",
    "Lifestyle",
    "Running",
    "Skate",
    "Training",
    "Walking"
  ],
  "genders": [
    "Men",
    "Women"
  ],
  "colors": [
    "Black",
    "Black/White",
    "Blue",
    "Grey",
    "Pink",
    "Red",
    "Red/Black",
    "White",
    "White/Green",
    "White/Red"
  ],
  "materials": [
    "Canvas",
    "Flyknit",
    "Leather",
    "Leather/Synthetic",
    "Mesh",
    "Primeknit",
    "Suede",
    "Suede/Canvas",
    "Synthetic"
  ],
  "price": {
    "min": 50.0,
    "max": 200.0,
    "currency": "USD"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| brands | string[] | Sorted alphabetically |
| categories | string[] | Sorted alphabetically |
| genders | string[] | Display values: "Men", "Women" |
| colors | string[] | Sorted alphabetically |
| materials | string[] | Sorted alphabetically |
| price.min | float | Lowest active sneaker price |
| price.max | float | Highest active sneaker price |
| price.currency | string | Always "USD" |

### Response 500

```json
{
  "detail": "Failed to fetch filter options",
  "error_code": "INTERNAL_ERROR"
}
```

---

## POST /api/v1/recommendations

Main endpoint. Accepts user preferences, returns top 5 ranked sneakers with similarity scores and explanations.

### Request Body

```json
{
  "brand": "Nike",
  "category": "Running",
  "budget_max": 180.0,
  "gender": "Men",
  "color": "White",
  "material": "Mesh"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| brand | string | No | Must match a known brand if provided |
| category | string | No | Must match a known category if provided |
| budget_max | float | No | Must be > 0 if provided |
| gender | string | No | "Men" or "Women" |
| color | string | No | Free text, matched with token overlap |
| material | string | No | Free text, matched with token overlap |

**At least one field must be provided.** Sending `{}` returns 422.

All fields are optional individually — user can search with just a brand, or just a budget, etc.

### Response 200

```json
{
  "query_summary": "Nike · Running · Men · White · Mesh · under $180",
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "display_name": "Nike Air Max 90",
      "brand": "Nike",
      "category": "Running",
      "gender": "Men",
      "color": "White",
      "material": "Mesh",
      "price_usd": 170.0,
      "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/sneakers/nike-air-max-90.jpg",
      "product_url": "https://www.nike.com/t/air-max-90-shoe",
      "similarity_score": 0.91,
      "reasons": [
        "Same brand: Nike",
        "Category match: Running",
        "Gender match: Men",
        "Similar color: White",
        "Matching material: Mesh",
        "Within your budget ($170 ≤ $180)"
      ]
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "display_name": "Nike React Infinity Run Flyknit 2",
      "brand": "Nike",
      "category": "Running",
      "gender": "Women",
      "color": "Pink",
      "material": "Flyknit",
      "price_usd": 160.0,
      "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/sneakers/nike-react-infinity.jpg",
      "product_url": null,
      "similarity_score": 0.74,
      "reasons": [
        "Same brand: Nike",
        "Category match: Running",
        "Within your budget ($160 ≤ $180)"
      ]
    }
  ],
  "meta": {
    "count": 5,
    "requested": 5,
    "latency_ms": 42,
    "model_version": "rf_v1",
    "rerank_applied": false
  }
}
```

#### Result Object Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | UUID string | No | Sneaker primary key |
| display_name | string | No | e.g. "Nike Air Max 90" |
| brand | string | No | Brand display name |
| category | string | No | Category display name |
| gender | string | No | "Men" or "Women" |
| color | string | No | |
| material | string | No | |
| price_usd | float | No | Price in USD |
| image_url | string | No | Cloudinary URL |
| product_url | string | Yes | Retail link — null if not found |
| similarity_score | float | No | 0.0–1.0, 2 decimal places |
| reasons | string[] | No | Human-readable explanation strings |

#### Meta Object Fields

| Field | Type | Description |
|-------|------|-------------|
| count | integer | Number of results returned |
| requested | integer | Always 5 |
| latency_ms | integer | Server-side processing time |
| model_version | string | e.g. "rf_v1" |
| rerank_applied | boolean | Whether Sentence Transformer rerank ran |

### Response 422 — Validation Error

Empty preferences:

```json
{
  "detail": [
    {
      "loc": ["body"],
      "msg": "At least one preference field must be provided",
      "type": "value_error"
    }
  ]
}
```

Invalid budget:

```json
{
  "detail": [
    {
      "loc": ["body", "budget_max"],
      "msg": "budget_max must be greater than 0",
      "type": "value_error"
    }
  ]
}
```

### Response 503 — Model Not Loaded

```json
{
  "detail": "Recommendation model is not loaded. Run ml/train.py first.",
  "error_code": "MODEL_NOT_LOADED"
}
```

### Response 500 — Internal Error

```json
{
  "detail": "Failed to generate recommendations",
  "error_code": "INTERNAL_ERROR"
}
```

---

## GET /api/v1/sneakers

Paginated catalog browse. Optional filters. Useful for a future browse page — not required for MVP UI but implemented for completeness.

### Query Parameters

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| brand | string | No | — | Filter by brand name |
| category | string | No | — | Filter by category name |
| gender | string | No | — | "Men" or "Women" |
| page | integer | No | 1 | Page number |
| page_size | integer | No | 20 | Items per page (max 100) |

### Example Request

```
GET /api/v1/sneakers?brand=Nike&category=Running&page=1&page_size=10
```

### Response 200

```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "display_name": "Nike Air Max 90",
      "brand": "Nike",
      "category": "Running",
      "gender": "Men",
      "color": "White",
      "material": "Mesh",
      "price_usd": 170.0,
      "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/sneakers/nike-air-max-90.jpg"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

List items omit `product_url`, `similarity_score`, and `reasons` — use the detail endpoint for full data.

### Response 422

Invalid page or page_size:

```json
{
  "detail": [
    {
      "loc": ["query", "page_size"],
      "msg": "page_size must be between 1 and 100",
      "type": "value_error"
    }
  ]
}
```

---

## GET /api/v1/sneakers/{sneaker_id}

Returns full detail for a single sneaker.

### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| sneaker_id | UUID | Sneaker primary key |

### Example Request

```
GET /api/v1/sneakers/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Response 200

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "display_name": "Nike Air Max 90",
  "brand": "Nike",
  "category": "Running",
  "gender": "Men",
  "color": "White",
  "material": "Mesh",
  "price_usd": 170.0,
  "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/sneakers/nike-air-max-90.jpg",
  "product_url": "https://www.nike.com/t/air-max-90-shoe",
  "description": "The Nike Air Max 90 is a classic running shoe featuring visible Air cushioning, a durable mesh upper, and iconic waffle outsole. Great for everyday wear and light runs."
}
```

### Response 404

```json
{
  "detail": "Sneaker not found",
  "error_code": "NOT_FOUND"
}
```

### Response 422

Invalid UUID format:

```json
{
  "detail": [
    {
      "loc": ["path", "sneaker_id"],
      "msg": "Invalid UUID format",
      "type": "value_error"
    }
  ]
}
```

---

## Status Code Reference

| Code | When |
|------|------|
| 200 | Success |
| 404 | Sneaker ID not found |
| 422 | Validation error (bad input) |
| 500 | Unexpected server error |
| 503 | Model not loaded at startup |

---

## Rate Limiting

Not implemented in MVP. Document for future:

- Public endpoints: 60 requests/minute per IP
- Authenticated endpoints: 120 requests/minute per user

---

## OpenAPI / Swagger

FastAPI auto-generates OpenAPI docs at:

- `/docs` — Swagger UI
- `/redoc` — ReDoc

Disable in production if desired via env var `ENABLE_DOCS=false`.

---

## Example curl Commands

### Health check

```bash
curl http://localhost:8000/health
```

### Get filter options

```bash
curl http://localhost:8000/api/v1/filters
```

### Get recommendations

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Nike",
    "category": "Running",
    "budget_max": 180,
    "gender": "Men",
    "color": "White",
    "material": "Mesh"
  }'
```

### Browse sneakers

```bash
curl "http://localhost:8000/api/v1/sneakers?brand=Nike&page=1&page_size=5"
```

### Sneaker detail

```bash
curl http://localhost:8000/api/v1/sneakers/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Related Documents

- [PROJECT_SPEC.md](./PROJECT_SPEC.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
- [TASKS.md](./TASKS.md)
- [AI_CONTEXT.md](./AI_CONTEXT.md)
