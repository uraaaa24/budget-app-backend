FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /code

# Copy dependency files first (better caching)
COPY ./pyproject.toml ./uv.lock /code/

# Install dependencies
RUN uv sync --frozen --no-dev

# Create virtual environment
ENV PATH="/code/.venv/bin:${PATH}"

# Set default port environment variable
ENV PORT=8080

# Copy application code
COPY . /code/

# Start the application
CMD ["sh", "-lc", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
