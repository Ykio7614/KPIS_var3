import tempfile
import unittest
from pathlib import Path

from app.models.entities import AppState
from app.repositories.file_repository import FileRepository
from app.services.import_export_service import ImportExportService


class ImportExportTests(unittest.TestCase):
    def test_json_roundtrip(self) -> None:
        service = ImportExportService(FileRepository())
        source = service.load_state("docs/examples/sample_data.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "state.json"
            service.save_state_json(str(out_path), source)
            loaded = service.load_state(str(out_path))

        self.assertIsNotNone(loaded.current_result)
        self.assertEqual(loaded.current_result.value, 0.608)
        self.assertEqual(len(loaded.periods), 3)
        self.assertEqual(len(loaded.scenarios), 3)

    def test_csv_import(self) -> None:
        service = ImportExportService(FileRepository())
        loaded = service.load_state("docs/examples/sample_data.csv")

        self.assertIsInstance(loaded, AppState)
        self.assertIsNotNone(loaded.current_result)
        self.assertEqual(loaded.current_result.value, 0.608)
        self.assertEqual(loaded.scenarios[1].result.value, 0.24)


if __name__ == "__main__":
    unittest.main()
