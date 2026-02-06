# Docker Architecture for NYC TLC Data Pipeline

## Overview
This pipeline ingests NYC taxi data into PostgreSQL using Docker containers. It has two main components:

### Component 1: Taxi Trip Data (`ingest_data.py`)
- **Purpose**: Downloads and ingests monthly yellow taxi trip data
- **Data Source**: GitHub release (yellow taxi CSVs)
- **Table**: `yellow_taxi_data`
- **CLI Parameters**:
  - `--year`: Year of data (default: 2021)
  - `--month`: Month of data (default: 1)
  - `--chunksize`: Rows per batch (default: 100000)
  - `--pg-user`, `--pg-password`, `--pg-host`, `--pg-port`, `--pg-db`: DB credentials
  - `--target-table`: Table name (default: yellow_taxi_data)
- **Logic**:
  1. Constructs URL: `https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_YYYY-MM.csv.gz`
  2. Reads file in chunks (100K rows at a time)
  3. First chunk: Creates table schema (if_exists='replace')
  4. Subsequent chunks: Appends data (if_exists='append')
  5. Prints progress with tqdm

### Component 2: Lookup Data (`ingest_lookup_data.py`)
- **Purpose**: Downloads and ingests reference tables (zones, colors)
- **Data Source**: GitHub misc release
- **Tables**:
  - `taxi_zone_lookup`: Zone information for pickup/dropoff locations
  - `taxi_colors`: Taxi company colors (reference data)
- **CLI Parameters**:
  - `--data-type`: 'all' | 'zones' | 'colors' (default: all)
  - `--pg-user`, `--pg-password`, `--pg-host`, `--pg-port`, `--pg-db`: DB credentials
- **Logic**:
  1. Tests database connection
  2. Based on `--data-type`, selects files to download
  3. Reads CSV from GitHub
  4. Replaces tables (if_exists='replace')
  5. One-time ingestion (no chunking needed - small files)

---

## File Structure

### `Dockerfile`
```dockerfile
FROM python:3.13.11-slim

# Multi-stage: copy uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

# Copy dependencies (pyproject.toml, uv.lock, .python-version)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

ENV PATH="/app/.venv/bin:$PATH"

# Install all dependencies
RUN uv sync --locked

# Copy both ingestion scripts
COPY ingest_data.py ingest_lookup_data.py .

# Entry point: Python interpreter
# Script name comes from docker-compose command or docker run
ENTRYPOINT [ "python" ]
CMD [ "ingest_data.py" ]
```

**Key Points**:
- `ENTRYPOINT [ "python" ]` → Runs Python
- `CMD [ "ingest_data.py" ]` → Default script (can be overridden)
- Both scripts copied to `/app`
- Virtual environment in PATH
- Dependencies locked for reproducibility

---

### `docker-compose.yml`
```yaml
services:
  # PostgreSQL Database
  pg-database:
    image: postgres:18
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    volumes:
      - ny_taxi_postgres_data:/var/lib/postgresql
    ports:
      - "5432:5432"

  # PgAdmin Web UI
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: root
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    ports:
      - "8085:80"

  # Lookup Data Ingestion (Reference Tables)
  ingest-lookup-data:
    build: .  # Uses Dockerfile in current directory
    command: python ingest_lookup_data.py --pg-host pg-database --pg-user root --pg-password root --pg-db ny_taxi
    depends_on:
      - pg-database  # Waits for DB to start first
    networks:
      - default  # Auto-connected to same network

volumes:
  ny_taxi_postgres_data:  # PostgreSQL data persistence
  pgadmin_data:  # PgAdmin data persistence
```

**Key Points**:
- `pg-database` hostname used for inter-container communication
- `depends_on` ensures DB is created before ingestion
- `networks: default` allows container-to-container DNS resolution
- Port 5432 exposed on host (5432:5432)

---

## Relationships

```
┌─────────────────────────────────────────────────────────────┐
│               Docker Compose (Orchestration)                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌─────────────┐ ┌──────────┐ ┌────────────────┐
        │ pg-database │ │ pgadmin  │ │ ingest-lookup- │
        │ (postgres)  │ │ (web)    │ │ data (Python)  │
        └─────────────┘ └──────────┘ └────────────────┘
              ▲                              │
              │                              │
              └──────────────────────────────┘
              (uses Dockerfile to build image)

        ┌──────────────────────────────────────────┐
        │         Dockerfile (Image Template)      │
        │  - Base: python:3.13.11-slim             │
        │  - Install: uv, dependencies             │
        │  - Copy: ingest_data.py                  │
        │  - Copy: ingest_lookup_data.py           │
        │  - ENTRYPOINT: python                    │
        └──────────────────────────────────────────┘
```

---

## Usage Examples

### 1. Start all services
```bash
docker-compose up -d
```

### 2. Ingest lookup data (reference tables)
```bash
docker-compose up ingest-lookup-data
# Or run independently:
docker run -it --rm \
  --network=pipeline_default \
  pipeline-ingest-lookup-data:latest \
  python ingest_lookup_data.py \
  --pg-host=pg-database \
  --pg-user=root \
  --pg-password=root \
  --pg-db=ny_taxi \
  --data-type=zones
```

### 3. Ingest taxi trip data (main script)
```bash
# Run directly
docker run -it --rm \
  --network=pipeline_default \
  pipeline-ingest-lookup-data:latest \
  python ingest_data.py \
  --pg-host=pg-database \
  --pg-user=root \
  --pg-password=root \
  --pg-db=ny_taxi \
  --year=2021 \
  --month=1 \
  --chunksize=100000
```

### 4. Check logs
```bash
docker-compose logs ingest-lookup-data
docker-compose logs pg-database
```

### 5. Stop services
```bash
docker-compose down
```

---

## Data Flow

### Trip Data Flow
```
GitHub (CSV.gz)
    │
    ▼
ingest_data.py
    │
    ├─ Read in chunks (100K rows)
    ├─ Parse dates
    ├─ Convert types
    ▼
PostgreSQL (yellow_taxi_data table)
```

### Lookup Data Flow
```
GitHub (Misc Release)
    │
    ├─ taxi_zone_lookup.csv
    ├─ taxi_colors.csv
    │
    ▼
ingest_lookup_data.py
    │
    ├─ Download each file
    ├─ Parse as DataFrame
    ▼
PostgreSQL
    ├─ taxi_zone_lookup table
    └─ taxi_colors table
```

---

## Connection String Format
```
postgresql://username:password@hostname:port/database
postgresql://root:root@pg-database:5432/ny_taxi
         └─ user    └─ password └─ host (DNS)     └─ db
```

When running in Docker:
- Use service name as hostname: `pg-database`
- Port stays 5432 (internal to network)
- From host machine, use `localhost:5432`

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Connection refused" | DB not ready | Use `depends_on` or add retry logic |
| "No such service" | Wrong image name | Check `docker-compose up ingest-lookup-data` |
| "ingest_lookup_data.py not found" | Not copied in Dockerfile | Ensure `COPY ingest_lookup_data.py .` in Dockerfile |
| Script keeps hanging | Downloading large file | Add timeout or check network |
| Port 5432 already in use | Host collision | Change docker-compose port: `5433:5432` |

