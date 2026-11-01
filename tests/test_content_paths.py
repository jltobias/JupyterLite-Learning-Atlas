import tempfile
import unittest
from pathlib import Path

from scripts.atlas_paths import canonical_notebooks, content_files


class ContentPathsTests(unittest.TestCase):
    def test_checkpoints_do_not_become_chapters_or_published_content(self):
        work = Path(__file__).resolve().parents[1] / "_build/test-content-paths"
        work.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            root = Path(folder).resolve()
            self.assertTrue(root.is_relative_to(work.resolve()))
            visible = root / "projects/example/index.ipynb"
            checkpoint = visible.parent / ".ipynb_checkpoints/index-checkpoint.ipynb"
            hidden = root / ".draft/unfinished.ipynb"
            asset = root / "assets/diagram.svg"
            for path in [visible, checkpoint, hidden, asset]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            self.assertEqual(canonical_notebooks(root), [visible])
            self.assertEqual(set(content_files(root)), {visible, asset})


if __name__ == "__main__":
    unittest.main()
