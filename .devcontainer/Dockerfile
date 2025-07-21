FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# uv (イメージに含まれていなければインストール)
RUN pip install --no-cache-dir uv

WORKDIR /workspace
# 依存ファイルのみ先にコピーしてキャッシュ層を活かす
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-editable || true

# 任意ツール
RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep tree && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/workspace/app
