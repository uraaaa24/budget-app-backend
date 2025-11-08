"""設定の読み込みテスト"""

import os
from unittest.mock import patch

import pytest


def test_env_variable_overrides_env_file():
    """環境変数が.envファイルより優先されることを確認"""
    # 環境変数を設定
    test_database_url = "postgresql+psycopg://test:test@neon.tech:5432/test"

    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": test_database_url,
            "DEBUG": "false",
            "CLERK_ISSUER": "https://test.clerk.accounts.dev",
            "CLERK_JWKS_URL": "https://test.clerk.accounts.dev/.well-known/jwks.json",
            "CLERK_SECRET_KEY": "sk_test_xxxxx",
            "CLERK_AUDIENCE": "test-app",
        },
    ):
        # settingsを再インポートして環境変数を読み込む
        from importlib import reload

        from app.core import config

        reload(config)

        # 環境変数が優先されていることを確認
        assert config.settings.DATABASE_URL == test_database_url
        assert config.settings.DEBUG is False


def test_settings_loads_from_env_file_when_no_env_vars():
    """環境変数がない場合は.envファイルから読み込むことを確認"""
    # 環境変数をクリア
    env_vars_to_remove = [
        "DATABASE_URL",
        "DEBUG",
        "CLERK_ISSUER",
        "CLERK_JWKS_URL",
        "CLERK_SECRET_KEY",
        "CLERK_AUDIENCE",
    ]

    with patch.dict(os.environ, {}, clear=False):
        # 指定した環境変数を削除
        for var in env_vars_to_remove:
            os.environ.pop(var, None)

        # settingsを再インポート
        from importlib import reload

        from app.core import config

        reload(config)

        # .envファイルから読み込まれていることを確認
        # （.envファイルが存在する場合のみ）
        assert config.settings.DATABASE_URL is not None
        assert isinstance(config.settings.DEBUG, bool)


def test_database_url_format():
    """DATABASE_URLのフォーマットが正しいことを確認"""
    from app.core.config import settings

    # PostgreSQLの接続文字列フォーマットであることを確認
    assert settings.DATABASE_URL.startswith("postgresql")
    assert "@" in settings.DATABASE_URL
    assert "/" in settings.DATABASE_URL


def test_production_env_ignores_env_file():
    """本番環境では.envファイルを読み込まないことを確認"""
    # 本番環境の設定
    test_database_url = "postgresql+psycopg://prod:prod@neon.tech:5432/prod"

    with patch.dict(
        os.environ,
        {
            "APP_ENV": "prod",
            "DATABASE_URL": test_database_url,
            "DEBUG": "false",
            "CLERK_ISSUER": "https://prod.clerk.accounts.dev",
            "CLERK_JWKS_URL": "https://prod.clerk.accounts.dev/.well-known/jwks.json",
            "CLERK_SECRET_KEY": "sk_prod_xxxxx",
            "CLERK_AUDIENCE": "prod-app",
        },
    ):
        # settingsを再インポートして環境変数を読み込む
        from importlib import reload

        from app.core import config

        reload(config)

        # 環境変数から読み込まれていることを確認
        assert config.settings.DATABASE_URL == test_database_url
        assert config.settings.DEBUG is False
        # 本番環境では.envファイルが読み込まれないため、
        # model_configのenv_fileがNoneであることを確認
        assert config.Settings.model_config.get("env_file") is None


def test_non_production_env_reads_env_file():
    """本番環境以外では.envファイルを読み込むことを確認"""
    test_database_url = "postgresql+psycopg://dev:dev@localhost:5432/dev"

    with patch.dict(
        os.environ,
        {
            "APP_ENV": "development",
            "DATABASE_URL": test_database_url,
            "DEBUG": "true",
            "CLERK_ISSUER": "https://dev.clerk.accounts.dev",
            "CLERK_JWKS_URL": "https://dev.clerk.accounts.dev/.well-known/jwks.json",
            "CLERK_SECRET_KEY": "sk_dev_xxxxx",
            "CLERK_AUDIENCE": "dev-app",
        },
    ):
        # settingsを再インポート
        from importlib import reload

        from app.core import config

        reload(config)

        # 環境変数から読み込まれていることを確認
        assert config.settings.DATABASE_URL == test_database_url
        assert config.settings.DEBUG is True
        # 開発環境では.envファイルが読み込まれるため、
        # model_configのenv_fileが".env"であることを確認
        assert config.Settings.model_config.get("env_file") == ".env"
