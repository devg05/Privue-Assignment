# Privue — SDE 1 Software Engineer (Python Backend)
## Take-Home Assignment: Vendor Score Microservice

This assignment evaluates practical backend engineering skills: API design, database modeling, validation, scoring logic, testing, deployment, and reasoning.  
No domain expertise is required.

---

# 1. Overview

You will build a small backend microservice that:

- Registers **vendors**
- Accepts **performance metrics** for each vendor
- Computes a **numeric score** (0–100) for each vendor
- Exposes APIs to retrieve vendor details and score history
- Recomputes scores **periodically** (daily or using any scheduling method you choose)
- Is **deployed online** so it can be tested via HTTP  
  **Local execution of your code will NOT be performed**

This assignment is intentionally small but covers real backend engineering.

---

# 2. Deployment Requirement (Mandatory)

Your service **must** be deployed to a publicly accessible environment.

Acceptable hosts include (but are not limited to):

- Render  
- Railway  
- Fly.io  
- AWS / GCP / Azure  
- Any equivalent platform

Your README must include:

- **Base URL** (e.g. `https://your-app.onrender.com`)
- **Working curl commands** for all required endpoints

If there is **no working deployment**, the submission is considered **incomplete**.

---

# 3. Technology Requirements

You must use:

- **Python 3.12+**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy or SQLModel**
- **Alembic (or similar)** for migrations
- **pytest** (or equivalent) for automated tests

Additional libraries are allowed but must be documented.

---

# 4. Functional Requirements

Your service must support the following:

---

## 4.1 Create Vendor  
`POST /vendors`  
Register a new vendor with basic details like name and category.

---

## 4.2 Ingest Vendor Metrics  
`POST /vendors/{vendor_id}/metrics`

Accept a JSON payload containing vendor performance metrics.  
Validation is required.

Example fields:

- `on_time_delivery_rate` (0–100)
- `complaint_count` (integer)
- `missing_documents` (boolean or integer)
- `compliance_score` (0–100)
- `timestamp` (ISO datetime, representing when the metric applies)

Your service must:

- Validate the payload
- Reject invalid data with clear 4xx error messages
- Handle multiple submissions (including out-of-order timestamps)

---

## 4.3 Get Vendor Details (with Latest Score)  
`GET /vendors/{vendor_id}`

Returns vendor info and the **latest computed score**  
(or a clear indication if no score exists yet).

---

## 4.4 Get Vendor Score History  
`GET /vendors/{vendor_id}/scores?limit=&offset=`

Paginated or simple limit/offset parameters are acceptable.

---

## 4.5 Health Check  
`GET /health`  
Returns a simple success response.

---

# 5. Data Model Requirements

Your database must contain at least the following tables:

---

## 5.1 Vendor

Fields:

- `id`
- `name`
- `category` (string or enum: e.g. supplier, distributor, dealer)
- `created_at`
- `updated_at`

---

## 5.2 VendorMetric

Each metric submission must be stored.

Fields:

- `id`
- `vendor_id` (FK → Vendor)
- `timestamp` (represents when the metrics apply)
- `on_time_delivery_rate`
- `complaint_count`
- `missing_documents`
- `compliance_score`
- (optional) `raw_payload` JSON for storing original input

---

## 5.3 VendorScore

Stores computed score snapshots.

Fields:

- `id`
- `vendor_id` (FK)
- `calculated_at`
- `score` (0–100)

---

# 6. Scoring Logic Requirements

You must implement a **deterministic** function producing a score between **0 and 100**.

### The formula must consider:

- Higher `on_time_delivery_rate` → higher score
- Higher `complaint_count` → lower score
- `missing_documents = true` → penalty
- Higher `compliance_score` → higher score
- Vendor `category` influences scoring weight in some meaningful way

### Requirements:

- Clamp final score to **[0, 100]**
- Handle multiple metrics intelligently (e.g., latest by timestamp)
- Document your scoring formula clearly in the README

The exact formula is **your choice**, but it must be reasonable and explained.

---

# 7. Score Recalculation Mechanism

You must provide a mechanism to recompute scores for **all vendors**.  
Choose any of the following:

- CLI command executed via cron
- APScheduler job
- Celery / RQ worker task
- Admin endpoint that triggers score recomputation
- Any equivalent approach

Your README must explain:

- How your recomputation works  
- How it *would* be scheduled daily in production  

---

# 8. Validation & Edge Cases

Your service must:

- Reject invalid JSON with descriptive errors
- Enforce constraints such as:
  - numeric ranges (0–100)
  - required fields
  - correct types
- Handle:
  - out-of-order metric timestamps
  - multiple metrics per vendor
  - duplicate or near-duplicate submissions (your chosen strategy must be documented)

Document your decisions in the README.

---

# 9. Testing Requirements

Automated tests are required.

---

## 9 Unit Tests

You must test:

- Scoring logic  
- Input validation logic  

Use pytest or any equivalent test framework.

---

# 10. Recommended Implementation Steps

This section is a suggested workflow to help approach your solution.

---

## Step 1 — Project Setup

- Set up FastAPI
- Add `/health` endpoint
- Prepare dependencies (`requirements.txt` or `pyproject.toml`)

---

## Step 2 — Database Schema

- Define models for Vendor, VendorMetric, VendorScore  
- Create migrations using Alembic

---

## Step 3 — Core API Endpoints

Implement:

- `POST /vendors`
- `POST /vendors/{vendor_id}/metrics`
- `GET /vendors/{vendor_id}`
- `GET /vendors/{vendor_id}/scores`

Ensure validation and error handling is solid.

---

## Step 4 — Scoring Logic

- Write a clear scoring function
- Document the formula in README

---

## Step 5 — Score Recalculation

Implement a recomputation mechanism: cron, scheduler, worker, or admin endpoint.

Document:

- How it works
- How it is intended to run daily

---

## Step 6 — Testing

Write:

- Unit tests for scoring + validation  
- Integration test for basic workflow  

---

## Step 7 — Deployment

Deploy publicly to any provider.

Your service must be reachable at the given URL.

---

## Step 8 — Final Polish

- Clean project structure (routers, schemas, services, db modules)
- Add logging where appropriate
- Improve error messaging
- Finalize README describing your decisions

---

# 11. Deliverables

Your submission must include:

1. **A Git repository** containing:
   - Source code
   - Tests
   - Database migrations
   - Requirements/pyproject
   - README with:
     - Live base URL  
     - Working curl examples  
     - Data model explanation  
     - Scoring logic explanation  
     - Scheduling/recompute explanation  
     - Notes, trade-offs, and assumptions  

2. **A publicly deployed version** of the service

Both are required for completion.

---

# 12. Evaluation Criteria

Your solution will be assessed on:

---

## Correctness
- APIs behave as expected  
- End-to-end flow works on deployed service  

---

## Code Quality
- Clean structure  
- Good naming  
- Clear separation of layers  

---

## Database Design
- Appropriate types  
- Foreign keys  
- Migrations  

---

## Scoring Logic
- Clear reasoning  
- Deterministic and consistent  
- Well-documented formula  

---

## Testing Quality
- Meaningful coverage  
- Tests are readable and maintainable  

---

## Deployment
- Public URL  
- Curl commands work as provided  

---

## Documentation
- Clear explanations in README  
- Logical decisions and reasoning  

---

**Good luck — we look forward to reviewing your submission.**
