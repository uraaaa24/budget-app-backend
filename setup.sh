#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# ========= Config (env overrideable) =========
WORKDIR="${WORKDIR:-/app}"
DB_URL_DEFAULT="postgresql://budget:budget@db:5432/budget_app"
DB_TIMEOUT="${DB_TIMEOUT:-60}"  # sec
MIGRATION_FILE="${MIGRATION_FILE:-app/infrastructure/db/migrate.py}"
MIGRATION_MODULE="${MIGRATION_MODULE:-app.infrastructure.db.migrate}"

# ========= Logging helpers =========
info() { echo "📣 $*"; }
ok()   { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
die()  { echo "❌ $*"; exit 1; }

trap 'die "Setup failed at line $LINENO"' ERR

echo "🚀 Setting up Budget App Backend development environment..."

# ========= Workdir =========
if [[ -d "$WORKDIR" ]]; then
  cd "$WORKDIR"
else
  warn "WORKDIR '$WORKDIR' not found. Using script directory instead."
  cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# ========= uv install (if missing) =========
if ! command -v uv >/dev/null 2>&1; then
  warn "uv not found. Installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # uv installer puts binaries in ~/.local/bin by default
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || die "uv installation failed (PATH=$PATH)"
fi

# ========= Python deps =========
info "Installing Python dependencies (uv sync)..."
uv sync
ok "Dependencies installed."

# ========= Wait for DB =========
# Use DATABASE_URL if provided; otherwise fall back to default.
# psycopg.connect expects 'postgresql://', so strip '+psycopg' if present.
info "Waiting for database to be ready..."
start=$SECONDS
until DATABASE_URL="${DATABASE_URL:-$DB_URL_DEFAULT}" uv run python - <<'PY' >/dev/null 2>&1
import os, sys
import psycopg
url = os.environ["DATABASE_URL"].replace("+psycopg", "")
try:
    with psycopg.connect(url, connect_timeout=2):
        pass
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
do
  elapsed=$(( SECONDS - start ))
  if (( elapsed >= DB_TIMEOUT )); then
    die "Database connection timeout after ${DB_TIMEOUT}s.
   - Check docker compose services
   - Ensure PostgreSQL container is healthy
   - Verify container networking"
  fi
  echo "⏳ Waiting for database... (${elapsed}s/${DB_TIMEOUT}s)"
  sleep 2
done
ok "Database is ready!"

# ========= Migrations (optional) =========
if [[ -f "$MIGRATION_FILE" ]]; then
  info "Running database migrations..."
  if ! uv run python -m "$MIGRATION_MODULE"; then
    warn "Migration failed, please check your database setup."
  else
    ok "Migrations completed."
  fi
else
  info "No migration file found at '$MIGRATION_FILE'. Skipping."
fi

# ========= pre-commit (optional) =========
if [[ -f ".pre-commit-config.yaml" ]]; then
  info "Setting up pre-commit hooks..."
  if uv run python - <<'PY' >/dev/null 2>&1
import importlib.util, sys
sys.exit(0 if importlib.util.find_spec("pre_commit") else 1)
PY
  then
    uv run pre-commit install || warn "Pre-commit setup failed."
  else
    warn "pre-commit package not installed. Skipping hook setup."
  fi
else
  info "No .pre-commit-config.yaml. Skipping pre-commit setup."
fi

# ========= Summary =========
echo ""
ok  "Setup complete!"
echo ""
cat <<EOF
📋 Available commands:
  task dev          # Start dev server
  task test         # Run tests
  task format       # Format code
  task lint         # Lint code
  task type-check   # Type check

🌐 Services:
  FastAPI:   http://localhost:8000
  API Docs:  http://localhost:8000/docs
  PostgreSQL localhost:5432
EOF
echo ""
echo "✨ Ready for development!"
