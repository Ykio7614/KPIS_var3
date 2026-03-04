from app.controllers.main_controller import MainController
from app.models.entities import AppState
from app.repositories.file_repository import FileRepository
from app.services.import_export_service import ImportExportService
from app.services.report_service import ReportService
from app.views.main_view import MainView


def run() -> None:
    state = AppState()
    repository = FileRepository()
    import_export_service = ImportExportService(repository)
    report_service = ReportService()
    view = MainView()
    MainController(
        view=view,
        state=state,
        import_export_service=import_export_service,
        report_service=report_service,
    )
    view.start()
