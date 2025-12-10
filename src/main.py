# main.py
# Единая точка входа для локального и "веб" запуска

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_root() -> None:
    """Добавляем корень репозитория в sys.path, чтобы можно было импортировать build."""
    repo_root = Path(__file__).resolve().parent.parent
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def main() -> None:
    _ensure_repo_root()
    from build import main as build_main  # pylint: disable=import-outside-toplevel

    build_main()


if __name__ == "__main__":
    main()
