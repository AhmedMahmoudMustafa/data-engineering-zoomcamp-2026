FROM python:3.13.11-slim

# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# RUN pip install pandas pyarrow (since we use uv there is no need for using pip)

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Add virtual environment to PATH so we can use installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked

COPY ingest_data.py ingest_lookup_data.py ./

ENTRYPOINT ["python"]
