from __future__ import annotations

from app.controllers.validation import ValidationError, build_input_from_raw
from app.domain.formulas.ipur import calculate_ipur
from app.models.entities import AppState, PeriodRecord, ScenarioRecord
from app.services.import_export_service import ImportExportService
from app.services.report_service import ReportService
from app.utils.constants import WEIGHT_PRESETS
from app.views.main_view import MainView


class MainController:
    def __init__(
        self,
        *,
        view: MainView,
        state: AppState,
        import_export_service: ImportExportService,
        report_service: ReportService,
    ) -> None:
        self.view = view
        self.state = state
        self.import_export_service = import_export_service
        self.report_service = report_service
        self.view.set_callbacks(
            {
                "apply_preset": self.apply_preset,
                "calculate": self.calculate_current,
                "add_period": self.add_period,
                "add_scenario": self.add_scenario,
                "clear": self.clear_periods_and_scenarios,
                "load": self.load_from_file,
                "save_json": self.save_json,
                "export_csv": self.export_csv,
                "export_html": self.export_html,
            }
        )
        self.apply_preset()
        self.calculate_current()

    def apply_preset(self) -> None:
        preset_name = self.view.get_form_data()["preset"]
        weights = WEIGHT_PRESETS.get(preset_name)
        if not weights:
            return
        self.view.set_weights(*weights)

    def calculate_current(self) -> None:
        try:
            indicator_input = self._build_current_input(label="Текущий расчёт")
        except ValidationError as error:
            self.view.show_error(str(error))
            return

        result = calculate_ipur(indicator_input)
        self.state.current_input = indicator_input
        self.state.current_result = result
        self._refresh_view()

    def add_period(self) -> None:
        try:
            form_data = self.view.get_form_data()
            name = form_data["period_name"].strip() or f"Период {len(self.state.periods) + 1}"
            indicator_input = self._build_current_input(label=name)
        except ValidationError as error:
            self.view.show_error(str(error))
            return

        result = calculate_ipur(indicator_input)
        self.state.current_input = indicator_input
        self.state.current_result = result
        self.state.periods.append(PeriodRecord(period_name=name, data=indicator_input, result=result))
        self._refresh_view()

    def add_scenario(self) -> None:
        try:
            form_data = self.view.get_form_data()
            name = form_data["scenario_name"].strip() or f"Сценарий {len(self.state.scenarios) + 1}"
            indicator_input = self._build_current_input(label=name)
        except ValidationError as error:
            self.view.show_error(str(error))
            return

        result = calculate_ipur(indicator_input)
        self.state.current_input = indicator_input
        self.state.current_result = result
        self.state.scenarios.append(
            ScenarioRecord(scenario_name=name, data=indicator_input, result=result)
        )
        self._refresh_view()

    def clear_periods_and_scenarios(self) -> None:
        self.state.periods.clear()
        self.state.scenarios.clear()
        self._refresh_view()

    def load_from_file(self) -> None:
        path = self.view.ask_open_path()
        if not path:
            return
        try:
            loaded_state = self.import_export_service.load_state(path)
        except (OSError, ValueError, KeyError, ValidationError) as error:
            self.view.show_error(f"Не удалось загрузить файл: {error}")
            return

        self.state.current_input = loaded_state.current_input
        self.state.current_result = loaded_state.current_result
        self.state.periods = loaded_state.periods
        self.state.scenarios = loaded_state.scenarios
        if self.state.current_input:
            self.view.set_input_values(self.state.current_input)
            self.view.preset_var.set(self._resolve_preset_name(self.state.current_input))
        self._refresh_view()
        self.view.show_info("Данные загружены.")

    def save_json(self) -> None:
        if self.state.current_input is None or self.state.current_result is None:
            self.view.show_error("Сначала выполните расчёт.")
            return
        path = self.view.ask_save_json_path()
        if not path:
            return
        try:
            self.import_export_service.save_state_json(path, self.state)
        except OSError as error:
            self.view.show_error(f"Не удалось сохранить JSON: {error}")
            return
        self.view.show_info("Состояние сохранено в JSON.")

    def export_csv(self) -> None:
        if self.state.current_input is None or self.state.current_result is None:
            self.view.show_error("Сначала выполните расчёт.")
            return
        path = self.view.ask_save_csv_path()
        if not path:
            return
        try:
            self.import_export_service.export_state_csv(path, self.state)
        except (OSError, ValueError) as error:
            self.view.show_error(f"Не удалось экспортировать CSV: {error}")
            return
        self.view.show_info("CSV экспортирован.")

    def export_html(self) -> None:
        if self.state.current_input is None or self.state.current_result is None:
            self.view.show_error("Сначала выполните расчёт.")
            return
        path = self.view.ask_save_html_path()
        if not path:
            return
        try:
            self.report_service.export_html(path, self.state)
        except OSError as error:
            self.view.show_error(f"Не удалось сохранить HTML-отчёт: {error}")
            return
        self.view.show_info("HTML-отчёт сохранён.")

    def _build_current_input(self, *, label: str):
        form_data = self.view.get_form_data()
        return build_input_from_raw(
            label=label,
            retrospective=form_data["retrospective"],
            statistics=form_data["statistics"],
            expert=form_data["expert"],
            weight_r=form_data["weight_r"],
            weight_s=form_data["weight_s"],
            weight_e=form_data["weight_e"],
        )

    def _resolve_preset_name(self, indicator_input) -> str:
        weights = indicator_input.weights.as_tuple()
        for name, preset in WEIGHT_PRESETS.items():
            if all(abs(left - right) < 0.000001 for left, right in zip(weights, preset)):
                return name
        return "Ручной"

    def _refresh_view(self) -> None:
        self.view.set_result(self.state.current_result)
        self.view.refresh_tables(self.state)
        self.view.render_charts(self.state.current_result, self.state.periods, self.state.scenarios)
