from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.models.entities import AppState


class ReportService:
    def export_html(self, path: str, state: AppState) -> None:
        file_path = Path(path)
        html = self._build_html(state)
        file_path.write_text(html, encoding="utf-8")

    def _build_html(self, state: AppState) -> str:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        current_table = ""
        summary = "<p>Текущий расчёт отсутствует.</p>"
        if state.current_input and state.current_result:
            summary = (
                f"<p><strong>ИПУР:</strong> {state.current_result.value:.3f}</p>"
                f"<p><strong>Интерпретация:</strong> {state.current_result.interpretation}</p>"
            )
            current_table = self._table(
                headers=["R", "S", "E", "aR", "aS", "aE"],
                rows=[
                    [
                        state.current_input.retrospective,
                        state.current_input.statistics,
                        state.current_input.expert,
                        state.current_input.weights.retrospective,
                        state.current_input.weights.statistics,
                        state.current_input.weights.expert,
                    ]
                ],
            )

        periods_table = self._table(
            headers=["Период", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация"],
            rows=[
                [
                    item.period_name,
                    item.data.retrospective,
                    item.data.statistics,
                    item.data.expert,
                    item.data.weights.retrospective,
                    item.data.weights.statistics,
                    item.data.weights.expert,
                    item.result.value,
                    item.result.interpretation,
                ]
                for item in state.periods
            ],
        )
        scenarios_table = self._table(
            headers=["Сценарий", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация"],
            rows=[
                [
                    item.scenario_name,
                    item.data.retrospective,
                    item.data.statistics,
                    item.data.expert,
                    item.data.weights.retrospective,
                    item.data.weights.statistics,
                    item.data.weights.expert,
                    item.result.value,
                    item.result.interpretation,
                ]
                for item in state.scenarios
            ],
        )
        return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Отчёт ИПУР</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1, h2 {{ color: #0f172a; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; }}
    th {{ background: #e2e8f0; }}
    .meta {{ color: #475569; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <h1>Отчёт по расчёту ИПУР</h1>
  <div class="meta">Сформировано: {timestamp}</div>
  <h2>Текущий результат</h2>
  {summary}
  {current_table}
  <h2>Периоды</h2>
  {periods_table}
  <h2>Сценарии</h2>
  {scenarios_table}
</body>
</html>
"""

    def _table(self, headers: list[str], rows: list[list[object]]) -> str:
        if not rows:
            return "<p>Нет данных.</p>"
        head_html = "".join(f"<th>{header}</th>" for header in headers)
        row_html = []
        for row in rows:
            cells = "".join(f"<td>{cell}</td>" for cell in row)
            row_html.append(f"<tr>{cells}</tr>")
        return f"<table><thead><tr>{head_html}</tr></thead><tbody>{''.join(row_html)}</tbody></table>"
