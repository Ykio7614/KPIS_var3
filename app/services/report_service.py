from __future__ import annotations

import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path

from app.domain.formulas.ipur import HIGH_TEXT, LOW_TEXT, MEDIUM_TEXT
from app.models.entities import AppState


class ReportService:
    def export_html(self, path: str, state: AppState) -> None:
        file_path = Path(path)
        html = self._build_html(state)
        file_path.write_text(html, encoding="utf-8")

    def export_pdf(self, path: str, state: AppState) -> None:
        from matplotlib.backends.backend_pdf import PdfPages

        file_path = Path(path)
        with PdfPages(file_path) as pdf:
            pdf.savefig(self._build_summary_page(state))
            pdf.savefig(
                self._build_table_figure(
                    title="Периоды",
                    headers=["Период", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация"],
                    rows=self._period_rows(state),
                )
            )
            pdf.savefig(
                self._build_table_figure(
                    title="Сценарии",
                    headers=["Сценарий", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация"],
                    rows=self._scenario_rows(state),
                )
            )
            pdf.savefig(self._build_current_chart_figure(state))
            pdf.savefig(self._build_periods_chart_figure(state))
            pdf.savefig(self._build_scenarios_chart_figure(state))

    def _build_html(self, state: AppState) -> str:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        charts_html = self._charts_block(state)
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
            rows=self._period_rows(state),
        )
        scenarios_table = self._table(
            headers=["Сценарий", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация"],
            rows=self._scenario_rows(state),
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
    .chart {{ margin-bottom: 24px; }}
    .chart img {{ max-width: 100%; border: 1px solid #cbd5e1; }}
  </style>
</head>
<body>
  <h1>Отчёт по расчёту ИПУР</h1>
  <div class="meta">Сформировано: {timestamp}</div>
  <h2>Текущий результат</h2>
  {summary}
  {current_table}
  <h2>Графики</h2>
  {charts_html}
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

    def _charts_block(self, state: AppState) -> str:
        charts = [
            ("Вклад компонентов и итоговый ИПУР", self._build_current_chart(state)),
            ("Динамика ИПУР по периодам", self._build_periods_chart(state)),
            ("Сравнение сценариев", self._build_scenarios_chart(state)),
        ]
        return "".join(
            f'<div class="chart"><h3>{title}</h3><img alt="{title}" src="data:image/png;base64,{image}"></div>'
            for title, image in charts
        )

    def _build_current_chart(self, state: AppState) -> str:
        figure = self._build_current_chart_figure(state)
        return self._figure_to_base64(figure)

    def _build_periods_chart(self, state: AppState) -> str:
        figure = self._build_periods_chart_figure(state)
        return self._figure_to_base64(figure)

    def _build_scenarios_chart(self, state: AppState) -> str:
        figure = self._build_scenarios_chart_figure(state)
        return self._figure_to_base64(figure)

    def _build_current_chart_figure(self, state: AppState):
        figure = self._create_figure()
        axis = figure.subplots()
        axis.set_title("Вклад компонентов и итоговый ИПУР")
        self._style_axis(axis)

        if state.current_result is None:
            self._empty_axis(axis, "Выполните расчёт, чтобы увидеть вклад компонентов.")
            figure.tight_layout()
            return figure

        bars = [
            state.current_result.contribution_retrospective,
            state.current_result.contribution_statistics,
            state.current_result.contribution_expert,
            state.current_result.value,
        ]
        labels = ["R", "S", "E", "I"]
        colors = ["#3b82f6", "#0ea5e9", "#8b5cf6", self._result_color(state.current_result.interpretation)]
        axis.bar(labels, bars, color=colors)
        axis.grid(axis="y", alpha=0.3)
        for index, value in enumerate(bars):
            axis.text(index, value + 0.02, f"{value:.2f}", ha="center", va="bottom", fontsize=9)
        figure.tight_layout()
        return figure

    def _build_periods_chart_figure(self, state: AppState):
        figure = self._create_figure()
        axis = figure.subplots()
        axis.set_title("Динамика ИПУР по периодам")
        self._style_axis(axis)

        if not state.periods:
            self._empty_axis(axis, "Добавьте хотя бы один период.")
            figure.tight_layout()
            return figure

        axis.plot(
            [item.period_name for item in state.periods],
            [item.result.value for item in state.periods],
            marker="o",
            color="#2563eb",
        )
        axis.grid(alpha=0.3)
        axis.tick_params(axis="x", rotation=25)
        figure.tight_layout()
        return figure

    def _build_scenarios_chart_figure(self, state: AppState):
        figure = self._create_figure()
        axis = figure.subplots()
        axis.set_title("Сравнение сценариев")
        self._style_axis(axis)

        if not state.scenarios:
            self._empty_axis(axis, "Добавьте 2-3 сценария для сравнения.")
            figure.tight_layout()
            return figure

        axis.bar(
            [item.scenario_name for item in state.scenarios],
            [item.result.value for item in state.scenarios],
            color=[self._result_color(item.result.interpretation) for item in state.scenarios],
        )
        axis.grid(axis="y", alpha=0.3)
        axis.tick_params(axis="x", rotation=15)
        figure.tight_layout()
        return figure

    def _build_summary_page(self, state: AppState):
        figure = self._create_document_figure()
        axis = figure.subplots()
        axis.axis("off")

        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        y = 0.95
        axis.text(0.02, y, "Отчёт по расчёту ИПУР", fontsize=18, weight="bold", va="top")
        y -= 0.07
        axis.text(0.02, y, f"Сформировано: {timestamp}", fontsize=10, color="#475569", va="top")
        y -= 0.08

        if state.current_input and state.current_result:
            axis.text(0.02, y, f"ИПУР: {state.current_result.value:.3f}", fontsize=13, weight="bold", va="top")
            y -= 0.05
            axis.text(0.02, y, state.current_result.interpretation, fontsize=11, va="top", wrap=True)
            y -= 0.08
            current_table = axis.table(
                cellText=[
                    [
                        f"{state.current_input.retrospective:.3f}",
                        f"{state.current_input.statistics:.3f}",
                        f"{state.current_input.expert:.3f}",
                        f"{state.current_input.weights.retrospective:.3f}",
                        f"{state.current_input.weights.statistics:.3f}",
                        f"{state.current_input.weights.expert:.3f}",
                    ]
                ],
                colLabels=["R", "S", "E", "aR", "aS", "aE"],
                bbox=[0.02, 0.48, 0.96, 0.16],
                cellLoc="center",
            )
            current_table.auto_set_font_size(False)
            current_table.set_fontsize(10)
        else:
            axis.text(0.02, y, "Текущий расчёт отсутствует.", fontsize=11, va="top")

        axis.text(
            0.02,
            0.36,
            "Следующие страницы содержат таблицы по периодам и сценариям, а также три графика из интерфейса.",
            fontsize=10,
            color="#334155",
            va="top",
            wrap=True,
        )
        figure.tight_layout()
        return figure

    def _build_table_figure(self, *, title: str, headers: list[str], rows: list[list[object]]):
        figure = self._create_document_figure()
        axis = figure.subplots()
        axis.axis("off")
        axis.set_title(title, fontsize=16, pad=16)

        if not rows:
            axis.text(0.5, 0.5, "Нет данных.", ha="center", va="center", fontsize=12)
            figure.tight_layout()
            return figure

        table = axis.table(
            cellText=[[str(cell) for cell in row] for row in rows],
            colLabels=headers,
            bbox=[0.02, 0.02, 0.96, 0.9],
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.35)
        figure.tight_layout()
        return figure

    def _period_rows(self, state: AppState) -> list[list[object]]:
        return [
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
        ]

    def _scenario_rows(self, state: AppState) -> list[list[object]]:
        return [
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
        ]

    def _style_axis(self, axis) -> None:
        axis.set_ylim(0, 1)
        axis.axhspan(0.6, 1.0, alpha=0.1, color="green")
        axis.axhspan(0.4, 0.6, alpha=0.1, color="yellow")
        axis.axhspan(0.0, 0.4, alpha=0.1, color="red")
        axis.axhline(y=0.6, color="green", linestyle="--", alpha=0.5, linewidth=1)
        axis.axhline(y=0.4, color="orange", linestyle="--", alpha=0.5, linewidth=1)

    def _empty_axis(self, axis, text: str) -> None:
        axis.set_xticks([])
        axis.set_yticks([0, 0.5, 1.0])
        axis.grid(axis="y", alpha=0.2)
        axis.text(0.5, 0.5, text, transform=axis.transAxes, ha="center", va="center")

    def _create_figure(self):
        from matplotlib.figure import Figure

        return Figure(figsize=(8, 3), dpi=120)

    def _create_document_figure(self):
        from matplotlib.figure import Figure

        return Figure(figsize=(11.69, 8.27), dpi=120)

    def _figure_to_base64(self, figure) -> str:
        buffer = BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("ascii")

    def _result_color(self, interpretation: str) -> str:
        if interpretation == HIGH_TEXT:
            return "#16a34a"
        if interpretation == MEDIUM_TEXT:
            return "#eab308"
        if interpretation == LOW_TEXT:
            return "#dc2626"
        return "#64748b"
