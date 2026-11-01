"""Canonical content excludes editor checkpoints and other hidden working files."""
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1] / "content"


def content_files(root=CONTENT):
    root = Path(root)
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def canonical_notebooks(root=CONTENT):
    return [path for path in content_files(root) if path.suffix == ".ipynb"]
