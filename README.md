# Privue — Vendor Score Microservice

This repository implements a small FastAPI microservice that:

- Registers vendors
- Stores vendor performance metrics
- Computes and snapshots vendor scores (0–100)
- Exposes endpoints to retrieve vendor details and score history
- Provides an admin endpoint and options for daily score recomputation


## Base URL

Replace the placeholder below with your deployed base URL (required for submission):

BASE_URL=http://13.204.62.20:8000


## Quick curl examples
Replace `{BASE}` with your base URL and `<vendor_id>` with an actual UUID returned from the create vendor call.

- Create vendor
	```sh
	curl -X POST "{BASE}/vendors" \
		-H "Content-Type: application/json" \
		-d '{"name":"Acme","category":"supplier"}'
	```

- Submit a metric
	```sh
	curl -X POST "{BASE}/vendors/<vendor_id>/metrics" \
		-H "Content-Type: application/json" \
		-d '{
			"timestamp":"2025-11-29T12:00:00+00:00",
			"on_time_delivery_rate":95.0,
			"complaint_count":0,
			"missing_documents":false,
			"compliance_score":98.0
		}'
	```

- Get vendor detail (includes latest score)
	```sh
	curl "{BASE}/vendors/<vendor_id>"
	```

- Get vendor scores (paginated)
	```sh
	curl "{BASE}/vendors/<vendor_id>/scores?limit=10&offset=0"
	```

- Health
	```sh
	curl "{BASE}/health"
	```

- Admin: recompute single vendor
	```sh
	curl -X POST "{BASE}/admin/vendors/<vendor_id>/scores/recompute"
	```

- Admin: recompute all vendors
	```sh
	curl -X POST "{BASE}/admin/vendors/scores/recompute"
	```


## Data model (summary)

- `vendors` (`VendorModel`)
	- `id` (UUID, PK)
	- `name` (string)
	- `category` (enum: `supplier`, `distributor`, `dealer`, `manufacturer`)
	- `created_at`, `updated_at` (timezone-aware datetimes)

- `vendor_metrics` (`VendorMetricModel`)
	- `id` (UUID, PK)
	- `vendor_id` (FK -> `vendors.id`)
	- `timestamp` (when the metric applies)
	- `on_time_delivery_rate` (float 0–100)
	- `complaint_count` (int)
	- `missing_documents` (bool)
	- `compliance_score` (float 0–100)
	- `raw_payload` (JSON, optional)

- `vendor_scores` (`VendorScoreModel`)
	- `id` (UUID, PK)
	- `vendor_id` (FK -> `vendors.id`)
	- `calculated_at` (when score was recorded)
	- `score` (float 0–100)


## Scoring logic (deterministic)

Implemented in `src/services/scoring_service.py`. For a single metric the score is computed as:

- delivery_component = `on_time_delivery_rate * 0.45`
- compliance_component = `compliance_score * 0.4`
- reliability_component = `max(0, 15 - complaint_penalty)`, where `complaint_penalty = min(complaint_count * 1.25, 25)`
- penalty_component = `10` if `missing_documents` is true, else `0`
- raw_score = delivery_component + compliance_component + reliability_component - penalty_component
- final_score = clamp(raw_score * category_weight, 0, 100)

Category weights (in code):
- `supplier`: 1.0
- `distributor`: 0.95
- `dealer`: 0.9
- `manufacturer`: 1.05


## Recompute / Scheduling

Supported approaches:

- **Admin endpoint (implemented)** — `GET /admin/vendors/scores/recompute` (bulk) and `GET /admin/vendors/{vendor_id}/scores/recompute` (single). Intended for scheduled or manual invocation.

- **AWS EventBridge + Lambda (used in this deployment)** — Created a small Lambda function that can perform an authenticated GET to the admin recompute endpoint, then added an EventBridge scheduled rule to invoke that Lambda daily. 


## Running locally

1. Create virtualenv and install deps:
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Provide `.env` (or env vars):
```ini
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
DATABASE_ECHO=false
ADMIN_API_KEY=replace_me
```

3. Run migrations:
```sh
export PYTHONPATH=$(pwd)
alembic upgrade head
```

4. Start the app (dev):
```sh
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```


## Tests

- Run unit and integration tests with pytest:
```sh
python -m pytest
```

Tests are in `tests/`.


## Future improvements

- **Protect admin endpoints with an API key**

- **Use JWT (Bearer) tokens for user/role-based access**

- **Operational improvements**
	- Use an external scheduler (cloud scheduler or cron) to trigger daily recomputes for higher reliability. Add retries and alerts on failure. Consider running recompute as a background job (Celery/RQ) for better scalability.

