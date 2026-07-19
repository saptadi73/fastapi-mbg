from app.core.config.settings import get_settings


def test_database_urls_loaded_from_env() -> None:
    settings = get_settings()

    assert settings.database_url is not None
    assert "127.0.0.1:5433/mbg" in settings.database_url
    assert settings.database_sync_url is not None
