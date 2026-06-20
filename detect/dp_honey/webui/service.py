"""Service layer for the DP-HONEY web UI.

Pure-ish functions that wrap the core :mod:`detect.dp_honey` library: they enforce
count caps, sanitize model names, and raise :class:`DPHoneyError` subclasses. No
FastAPI/HTTP imports live here, so every function is unit-testable without a server.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from ..errors import DPHoneyError

# Reserved label the UI uses for the committed synthetic golden fixture.
GOLDEN_NAME = "golden-fixture"
GOLDEN_PATH = Path("tests/fixtures/dp_honey/golden_model.json")

_SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


class InvalidModelName(DPHoneyError):
    """A model name contains unsafe characters or path components."""


def _models_dir(models_dir: Optional[Path]) -> Path:
    return Path(models_dir) if models_dir is not None else Path("models")


def resolve_model_ref(name: str, models_dir: Optional[Path] = None) -> Path:
    """Resolve a client-supplied model *name* to a safe on-disk path.

    Accepts the reserved golden-fixture label, or a name matching
    ``[A-Za-z0-9._-]+`` resolved inside ``models_dir``. Rejects empty names,
    ``..``, and any path separators (blocks traversal).
    """
    if name == GOLDEN_NAME:
        return GOLDEN_PATH
    if not name or ".." in name or not _SAFE_NAME.match(name):
        raise InvalidModelName(f"unsafe or unknown model name: {name!r}")
    filename = name if name.endswith(".json") else f"{name}.json"
    return _models_dir(models_dir) / filename
