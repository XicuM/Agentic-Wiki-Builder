import os

def _load_env():
    """Minimalist .env loader to avoid external dependencies."""
    # Root is 4 levels up from .agents/skills/research/scripts/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(current_dir, "../../../../"))
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key] = val

_load_env()
API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
