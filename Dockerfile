FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /code

# Copy dependency files first (better caching)
COPY ./pyproject.toml ./uv.lock /code/

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . /code/

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8080}"]
