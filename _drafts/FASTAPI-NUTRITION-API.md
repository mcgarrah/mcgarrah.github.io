---
layout: none
date: 1999-12-31
sitemap: false
---

# FastAPI Nutrition API — Project Planning & Reference

Extracted from: `Google Gemini - Building a FastAPI Nutrition API.pdf` (exported 4/22/2026, PDF deleted 7/29/2026)

This convenience file preserves the full Gemini conversation and serves as the planning
document for a blog article series and the project itself.

---

## Project Goal

Demonstrate to potential employers the ability to design and build a production-grade API
that showcases architecture, development, infrastructure, and data engineering best
practices. FastAPI is the preferred framework for exposing insights and content.

The project bridges existing open-source Python packages (`usda_fdc_python`,
`gs1_gpc_python`) with a modern async API gateway, deployed via container-native CI/CD.

---

## Why FastAPI

- Built on ASGI (Asynchronous Server Gateway Interface) — handles concurrent requests
  efficiently, critical for AI and Cloud Architecture roles
- Type hints and Pydantic models auto-generate OpenAPI (Swagger) documentation
- Async-native with `httpx` for non-blocking external API calls
- Modern Python ecosystem alignment (vs Flask/Django for new API work)

---

## Architecture: The "Unified Food Intelligence API"

A single FastAPI gateway that aggregates three free external data sources:

| Service | Primary Strength | Role |
|---------|-----------------|------|
| USDA FoodData Central (FDC) | Scientifically validated nutrition | Gold standard for nutrient precision |
| Open Food Facts (OFF) | Crowdsourced, global, 3M+ products | Fallback for GTINs not in USDA; product images |
| GS1 GPC | Administrative classification | Source of truth for industry taxonomy |

### Key Architectural Patterns

- **Parallel Execution**: `asyncio.gather` across all three sources to keep latency <500ms
- **Ranked Truth Model**: USDA prioritized for precision, OFF for breadth/media, GS1 for classification
- **Graceful Degradation / Circuit Breaker**: If USDA is down, return OFF data with a `warning` flag — never crash
- **Conflict Resolution**: If USDA says 100 calories and OFF says 110, prefer USDA
- **Schema Normalization**: Map disparate field names (`energy-kcal_100g` vs `nutrients.calories`) into a single Pydantic `CanonicalProduct` model

---

## The Engineering Trifecta

| Discipline | How This Project Proves It |
|-----------|---------------------------|
| Infrastructure / DevOps | Deploying via App Platform using `app.yaml` (IaC) and Dockerfile |
| Application Engineering | FastAPI with async endpoints for high-performance, scalable interfaces |
| Data Engineering | Aggregating disparate sources and mapping to a unified Pydantic model (ETL) |

### Machine Learning Connection

- **Data Validation**: Pydantic for the API = same logic used for ML pipeline feature validation
- **Latency Management**: `asyncio.gather` is critical in ML inference where you fetch user profile, product history, and model prediction simultaneously
- **API as Interface**: PyTorch/Scikit-learn models eventually get wrapped in FastAPI for business consumption
- This project is a "Feature Engineering Pipeline-Lite" — raw external data → cleaned, normalized, structured format

---

## Resume Connections

### Drug Lookup Precedent (Blue Cross NC)
- DLC project: enterprise-wide REST API for fast sub-string lookups and cost calculations for pharmaceuticals
- Same "lookup logic" applied to food science and supply chain data using a modern async stack

### Microservices & Service Mesh (Envestnet)
- UPA project: containerized microservices on a service mesh
- Dockerfile and `app.yaml` designed with "microservice-first" mindset — architecturally ready for a larger service mesh or EKS cluster

### Serverless ETL (Medicare Guided Selling, BCBSNC)
- SLS implementation: Python 3 REST API backed by custom event-driven ETL with DynamoDB/DAX
- Mirrors the USDA/GS1 data aggregation pattern; in-memory caching replaces DynamoDB

### Data Engineering at Scale (USPS)
- 25-node SAS Viya cluster, 26TB RAM, 1PB Hadoop Data Lake
- Python Fabric extensions and Ansible for cluster stabilization
- This project is the modern, cloud-native evolution: building the "faucets" (APIs) that deliver intelligence

### Portfolio Summary Statement

> "Building on my experience developing enterprise lookup APIs for the healthcare sector
> (BCBSNC) and managing petabyte-scale data lakes (USPS), this project demonstrates a
> modern, asynchronous approach to supply chain data aggregation using FastAPI and
> container-native deployment."

---

## Technical Implementation

### Core Endpoint

```python
from fastapi import FastAPI
from usda_fdc_python import FDCClient
from gs1_gpc_python import GPCClient
import asyncio

app = FastAPI(title="Unified Food Intelligence API")

fdc = FDCClient(api_key="YOUR_FREE_USDA_KEY")
gs1 = GPCClient()

@app.get("/api/v1/lookup/{gtin}")
async def lookup_product(gtin: str):
    usda_task = asyncio.create_task(fdc.get_nutrition(gtin))
    off_task = asyncio.create_task(off.get_product(gtin))
    gs1_task = asyncio.create_task(gs1.get_brick(gtin))

    usda, off_data, gs1_data = await asyncio.gather(usda_task, off_task, gs1_task)

    return {
        "gtin": gtin,
        "name": usda.name or off_data.name or "Unknown Product",
        "category": gs1_data.category,
        "nutrition": merge_nutrition(usda, off_data),
        "images": off_data.images,
        "data_sources": ["USDA" if usda else None, "OFF" if off_data else None]
    }
```

### Canonical Data Model (Pydantic)

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

class NutrientValue(BaseModel):
    value: float
    unit: str = "g"

class CanonicalProduct(BaseModel):
    """Single Source of Truth model hiding upstream complexity."""
    gtin: str
    product_name: str
    brand: Optional[str] = None

    # GS1 classification
    category_hierarchy: Optional[List[str]] = Field(
        default=[], description="GS1 GPC Bricks and Families"
    )

    # Normalized nutrition (per 100g/ml)
    calories_kcal: Optional[float] = None
    protein: Optional[NutrientValue] = None
    fat: Optional[NutrientValue] = None
    carbohydrates: Optional[NutrientValue] = None

    # Media & labels from Open Food Facts
    image_url: Optional[HttpUrl] = None
    ingredients_text: Optional[str] = None

    # Data governance metadata
    data_sources: List[str] = []
    upstream_latency_ms: Dict[str, float] = {}
```

### Data Orchestrator (Mapper)

```python
class DataOrchestrator:
    @staticmethod
    def map_to_canonical(gtin: str, usda: dict = None, off: dict = None, gs1: dict = None) -> CanonicalProduct:
        product = CanonicalProduct(gtin=gtin, product_name="Unknown")

        # Layer 1: Open Food Facts (name, images, ingredients)
        if off:
            product.product_name = off.get('product_name', product.product_name)
            product.brand = off.get('brands')
            product.image_url = off.get('image_url')
            product.ingredients_text = off.get('ingredients_text')
            product.data_sources.append("OpenFoodFacts")

        # Layer 2: USDA (scientific nutrient data — overrides OFF)
        if usda:
            product.product_name = usda.get('description', product.product_name)
            nutrients = usda.get('labelNutrients', {})
            product.calories_kcal = nutrients.get('calories', {}).get('value')
            product.protein = NutrientValue(value=nutrients.get('protein', {}).get('value', 0))
            product.data_sources.append("USDA_FDC")

        # Layer 3: GS1 (taxonomy)
        if gs1:
            product.category_hierarchy = gs1.get('hierarchy', [])
            product.data_sources.append("GS1_GPC")

        return product
```

### Why This Design Shows "Lead" Level

1. **Immutability & Validation**: Pydantic auto-returns 422 if upstream sends garbage data — protects downstream ML models from null values
2. **Graceful Fallbacks**: `product.product_name = ... or product.product_name` ensures OFF fills gaps when USDA is missing
3. **Observability**: `upstream_latency_ms` and `data_sources` in the response tell consumers exactly where data came from and if a provider is lagging
4. **SOC2/Compliance Ready**: Single `CanonicalProduct` model provides one place to implement data masking or PII stripping

---

## Deployment: DigitalOcean App Platform

### Cost Strategy
- App Platform Basic Tier: ~$5/mo
- Container-native, mirrors K8s architectural patterns
- GitHub repo connection with automatic builds on push

### Dockerfile
- `python:3.11-slim` base for lightweight, secure container
- Binds to port 8080 (App Platform standard)
- Multi-stage build to keep image lean

### app.yaml (IaC)
- Placed in `.do/` directory at repo root
- Defines GitHub repo connection, instance size, environment variables
- USDA FDC API Key stored as a secret environment variable
- Health check pointing to `/docs` for zero-downtime deployments

### CI/CD
- GitHub Actions runs `pytest` and `flake8` before App Platform builds
- Automatic deployment on push to main

---

## "Day 2" Operations (Lead Principal Additions)

### 1. Advanced Observability (SRE Flex)
- OpenTelemetry middleware via `opentelemetry-instrumentation-fastapi`
- Distributed tracing: know whether USDA or GS1 caused slowness
- Integration with self-hosted SigNoz/GlitchTip

### 2. Graceful Degradation
- Circuit breaker / fallback mechanism for partial failures
- Return 200 OK with available data + metadata flag for unavailable sources
- Demonstrates resiliency, data governance, and systemic thinking

### 3. API Versioning & Documentation Polish
- URL-based versioning (`/v1/`)
- Rich OpenAPI metadata: custom logo, contact info linking to blog
- Pydantic `Field(description="...")` for detailed field docs
- `/health` endpoint checking upstream connectivity
- `/version` endpoint pulling current Git hash from environment

### 4. Data Freshness Telemetry
- Health check / telemetry endpoint reporting "Data Freshness" and "Upstream Latency"
- Shows you care about data reliability, not just code execution

---

## README Structure (Technical Decision Log / ADR)

1. **The Problem**: High cost of proprietary supply chain data ($40k/yr OneWorldSync)
2. **The Solution**: Asynchronous aggregator leveraging public data (USDA/GS1/OFF)
3. **The Architecture**: Why FastAPI? Why DigitalOcean App Platform?
4. **The Security**: SOC2-level concerns (environment secrets, TLS, least-privilege containers)
5. **The Data Engineering**: Normalizing disparate schemas from three government/industry sources

---

## Existing Repositories

- [openfoodfacts-python](https://github.com/openfoodfacts/openfoodfacts-python) — Open Food Facts Python SDK
- [usda_fdc_python](https://github.com/mcgarrah/usda_fdc_python) — Python package for USDA FoodData Central
- [gs1_gpc_python](https://github.com/mcgarrah/gs1_gpc_python) — Python package for GS1 Global Product Classification
- [oneworldsync_python](https://github.com/mcgarrah/oneworldsync_python) — Python package (key expired, $40k/yr — dropped)
- [shiny-quiz](https://github.com/mcgarrah/shiny-quiz) — Flask app deployed on DigitalOcean
- [legendary_quick_quiz](https://github.com/mcgarrah/legendary_quick_quiz) — Django app
- [shiny-shop](https://github.com/mcgarrah/shiny-shop) — Django shop app
- [jekyll-pandoc-exports](https://github.com/mcgarrah/jekyll-pandoc-exports) — Ruby gem

---

## Proposed Article Series

### Article 1: Architecture & Design — "Building a Unified Food Intelligence API with FastAPI"
- Problem statement: proprietary data costs vs free public APIs
- Why FastAPI over Flask/Django for new API work
- Three-source architecture: USDA FDC, Open Food Facts, GS1 GPC
- Ranked Truth Model and conflict resolution strategy
- Canonical Data Model design with Pydantic
- Connection to resume experience (USPS data engineering, BCBSNC drug lookup, Envestnet microservices)

### Article 2: Implementation — "FastAPI Async Patterns, Data Orchestration, and Graceful Degradation"
- Project scaffolding and dependency setup
- Async endpoint implementation with `asyncio.gather`
- DataOrchestrator mapper: normalizing USDA, OFF, and GS1 schemas
- Graceful degradation: circuit breaker pattern for partial upstream failures
- Pydantic validation as a data quality gate
- API versioning (`/v1/`) and OpenAPI documentation polish

### Article 3: Infrastructure & Deployment — "Container-Native CI/CD on DigitalOcean App Platform"
- Dockerfile: multi-stage build with `python:3.11-slim`
- `.do/app.yaml` as Infrastructure-as-Code
- Secret management for USDA API key
- GitHub Actions pipeline: `pytest`, `flake8`, automatic deploy
- Health check and zero-downtime deployment strategy
- `/health` and `/version` operational endpoints

### Article 4: Observability & Production Readiness — "Day 2 Operations for a Lead Engineer"
- OpenTelemetry instrumentation with `opentelemetry-instrumentation-fastapi`
- Distributed tracing: identifying which upstream source caused latency
- Data freshness telemetry and upstream latency reporting
- Prometheus metrics via `starlette-prometheus`
- Structured logging for production debugging
- SOC2/compliance considerations: data masking, PII stripping, least-privilege containers

---

## Work Outline

### Phase 1: Foundation
- [ ] Create new GitHub repository (`fastapi-nutrition-api` or similar)
- [ ] Set up project structure: `pyproject.toml`, `requirements.txt`, `.gitignore`
- [ ] Define Pydantic models (`CanonicalProduct`, `NutrientValue`)
- [ ] Implement `DataOrchestrator` mapper with layered merge logic
- [ ] Write basic FastAPI app with `/api/v1/lookup/{gtin}` endpoint
- [ ] Integrate `usda_fdc_python` and `gs1_gpc_python` packages
- [ ] Add Open Food Facts client (httpx async)

### Phase 2: Robustness
- [ ] Implement `asyncio.gather` for parallel upstream calls
- [ ] Add graceful degradation / circuit breaker for partial failures
- [ ] Add in-memory caching (`cachetools` LRU) for frequent lookups
- [ ] Pydantic input validation and 422 error handling
- [ ] API versioning (`/v1/`)
- [ ] `/health` endpoint (upstream connectivity check)
- [ ] `/version` endpoint (Git hash from environment)

### Phase 3: Deployment
- [ ] Write Dockerfile (multi-stage, `python:3.11-slim`, port 8080)
- [ ] Write `.do/app.yaml` for DigitalOcean App Platform
- [ ] Configure USDA FDC API key as environment secret
- [ ] GitHub Actions workflow: `pytest`, `flake8`, deploy trigger
- [ ] Verify health check and zero-downtime deployment

### Phase 4: Observability & Polish
- [ ] OpenTelemetry middleware integration
- [ ] `upstream_latency_ms` tracking in responses
- [ ] Prometheus `/metrics` endpoint
- [ ] Rich OpenAPI metadata (logo, contact, field descriptions)
- [ ] README as Technical Decision Log (ADR format)
- [ ] Write blog article series (4 articles, MWF cadence)

### Phase 5: Stretch Goals
- [ ] Redis caching layer (if budget allows)
- [ ] CORS middleware for specific domain restriction
- [ ] Structured logging integration (SigNoz/GlitchTip)
- [ ] "Data Freshness" telemetry endpoint
- [ ] USDA Branded Foods data (messier, bigger data engineering flex)

---

## Decisions Made

- **Dropped OneWorldSync**: $40k/yr, key expired — replaced with Open Food Facts (free, crowdsourced)
- **DigitalOcean App Platform over Droplet**: ~$5/mo, container-native, automatic deploys, no server management
- **In-memory cache over Redis**: Cost savings, sufficient for initial deployment
- **Proxmox not public-exposed**: Hosting on DigitalOcean, not homelab
- **Three external sources minimum**: Shows complex multi-vendor data management

---

## Raw Gemini Conversation

The sections above are organized from the full conversation. Key topics covered:

1. Why FastAPI over Flask/Django
2. Architectural strategy: "Lite Gateway" with async + in-memory caching
3. Implementation with existing Python packages (`usda_fdc_python`, `gs1_gpc_python`)
4. Cost-effective hosting on DigitalOcean App Platform (~$5/mo)
5. The "Engineering Trifecta": Infrastructure, Application, Data Engineering
6. Machine Learning connection: Feature Engineering Pipeline-Lite
7. Resume connections: USPS, BCBSNC, Envestnet
8. Adding Open Food Facts as third source for complex management
9. Canonical Data Model with Pydantic and DataOrchestrator mapper
10. "Day 2" operations: observability, graceful degradation, API versioning
11. README structure as Technical Decision Log (ADR)
