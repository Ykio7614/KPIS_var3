import importlib.util
import tempfile
import unittest
from pathlib import Path

from app.models.entities import AppState
from app.repositories.file_repository import FileRepository
from app.services.import_export_service import ImportExportService
from app.services.report_service import ReportService


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

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib не установлен")
    def test_html_report_contains_embedded_charts(self) -> None:
        state = ImportExportService(FileRepository()).load_state("docs/examples/sample_data.json")
        report_service = ReportService()

        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "report.html"
            report_service.export_html(str(out_path), state)
            html = out_path.read_text(encoding="utf-8")

        self.assertIn("data:image/png;base64,", html)
        self.assertIn("Вклад компонентов и итоговый ИПУР", html)
        self.assertIn("Динамика ИПУР по периодам", html)
        self.assertIn("Сравнение сценариев", html)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib не установлен")
    def test_pdf_report_is_created(self) -> None:
        state = ImportExportService(FileRepository()).load_state("docs/examples/sample_data.json")
        report_service = ReportService()

        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "report.pdf"
            report_service.export_pdf(str(out_path), state)

            self.assertTrue(out_path.exists())
            self.assertGreater(out_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
