
import yaml
from pathlib import Path

_CONFIG_CACHE = None


def load_config():
    """
    Loads RAG configuration from config/rag_config.yaml
    Uses caching to avoid re-reading the file multiple times
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = Path("config") / "rag_config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path.resolve()}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f)

    return _CONFIG_CACHE
