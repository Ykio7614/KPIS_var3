from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.entities import AppState
from app.repositories.base import Repository


class ImportExportService:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def load_state(self, path: str) -> AppState:
        file_path = Path(path)
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            payload = self._repository.load_json(file_path)
            return AppState.from_dict(payload)
        if suffix == ".csv":
            rows = self._repository.load_csv(file_path)
            return self._state_from_csv(rows)
        raise ValueError("Поддерживаются только файлы JSON и CSV.")

    def save_state_json(self, path: str, state: AppState) -> None:
        self._repository.save_json(Path(path), state.to_dict())

    def export_state_csv(self, path: str, state: AppState) -> None:
        self._repository.save_csv(Path(path), self._state_to_csv(state))

    def _state_to_csv(self, state: AppState) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        if state.current_input and state.current_result:
            rows.append(
                self._flat_row(
                    kind="current",
                    name=state.current_input.label or "Текущий расчёт",
                    state=state,
                    input_payload=state.current_input,
                    result=state.current_result,
                )
            )

        for item in state.periods:
            rows.append(
                self._flat_row(
                    kind="period",
                    name=item.period_name,
                    state=state,
                    input_payload=item.data,
                    result=item.result,
                )
            )

        for item in state.scenarios:
            rows.append(
                self._flat_row(
                    kind="scenario",
                    name=item.scenario_name,
                    state=state,
                    input_payload=item.data,
                    result=item.result,
                )
            )
        return rows

    def _flat_row(
        self,
        *,
        kind: str,
        name: str,
        state: AppState,
        input_payload,
        result,
    ) -> dict[str, Any]:
        del state
        return {
            "type": kind,
            "name": name,
            "R": input_payload.retrospective,
            "S": input_payload.statistics,
            "E": input_payload.expert,
            "aR": input_payload.weights.retrospective,
            "aS": input_payload.weights.statistics,
            "aE": input_payload.weights.expert,
            "I": result.value,
            "interpretation": result.interpretation,
        }

    def _state_from_csv(self, rows: list[dict[str, str]]) -> AppState:
        from app.controllers.validation import build_input_from_raw
        from app.domain.formulas.ipur import calculate_ipur
        from app.models.entities import PeriodRecord, ScenarioRecord

        state = AppState()
        for row in rows:
            kind = (row.get("type") or "").strip().lower()
            name = (row.get("name") or "").strip()
            indicator_input = build_input_from_raw(
                label=name,
                retrospective=row.get("R", ""),
                statistics=row.get("S", ""),
                expert=row.get("E", ""),
                weight_r=row.get("aR", ""),
                weight_s=row.get("aS", ""),
                weight_e=row.get("aE", ""),
            )
            result = calculate_ipur(indicator_input)
            if kind == "current":
                state.current_input = indicator_input
                state.current_result = result
            elif kind == "period":
                state.periods.append(PeriodRecord(period_name=name, data=indicator_input, result=result))
            elif kind == "scenario":
                state.scenarios.append(
                    ScenarioRecord(scenario_name=name, data=indicator_input, result=result)
                )
        return state
