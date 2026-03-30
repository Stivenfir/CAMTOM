import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from camtom_replacement.core.config import get_settings  # noqa: E402


if __name__ == "__main__":
    settings = get_settings(validate=False)
    uvicorn.run(
        "camtom_replacement.api.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
