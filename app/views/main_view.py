from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.domain.formulas.ipur import HIGH_TEXT, LOW_TEXT, MEDIUM_TEXT
from app.models.entities import AppState, CalculationResult, IndicatorInput
from app.utils.constants import WEIGHT_PRESETS


class MainView:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("ИПУР: расчёт управленческого решения")
        self.root.geometry("1450x920")
        self.root.minsize(1200, 800)

        self.preset_var = tk.StringVar(value="Стандартный")
        self.r_var = tk.StringVar(value="0.70")
        self.s_var = tk.StringVar(value="0.73")
        self.e_var = tk.StringVar(value="0.35")
        self.ar_var = tk.StringVar(value="0.30")
        self.as_var = tk.StringVar(value="0.50")
        self.ae_var = tk.StringVar(value="0.20")
        self.period_name_var = tk.StringVar(value="2026-03")
        self.scenario_name_var = tk.StringVar(value="Без изменений")
        self.result_var = tk.StringVar(value="I = -")
        self.interpretation_var = tk.StringVar(value="Интерпретация появится после расчёта.")

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(self.root, padding=12)
        control_frame.grid(row=0, column=0, sticky="nsw")

        content_frame = ttk.Frame(self.root, padding=(0, 12, 12, 12))
        content_frame.grid(row=0, column=1, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        self._build_controls(control_frame)
        self._build_tables(content_frame)
        self._build_charts(content_frame)

    def _build_controls(self, parent: ttk.Frame) -> None:
        input_frame = ttk.LabelFrame(parent, text="Ввод данных", padding=10)
        input_frame.grid(row=0, column=0, sticky="new")

        ttk.Label(input_frame, text="Режим весов").grid(row=0, column=0, sticky="w", pady=4)
        self.preset_combo = ttk.Combobox(
            input_frame,
            textvariable=self.preset_var,
            values=list(WEIGHT_PRESETS.keys()),
            state="readonly",
            width=18,
        )
        self.preset_combo.grid(row=0, column=1, sticky="ew", pady=4)
        self.apply_preset_button = ttk.Button(input_frame, text="Применить")
        self.apply_preset_button.grid(row=0, column=2, padx=(6, 0), pady=4)

        rows = [
            ("R", self.r_var),
            ("S", self.s_var),
            ("E", self.e_var),
            ("aR", self.ar_var),
            ("aS", self.as_var),
            ("aE", self.ae_var),
        ]
        for index, (label, variable) in enumerate(rows, start=1):
            ttk.Label(input_frame, text=f"{label} (0..1)").grid(row=index, column=0, sticky="w", pady=4)
            spin = tk.Spinbox(
                input_frame,
                from_=0.0,
                to=1.0,
                increment=0.01,
                textvariable=variable,
                width=8,
                justify="right",
                format="%.2f",
            )
            spin.grid(row=index, column=1, sticky="w", pady=4)

        ttk.Label(input_frame, text="Период").grid(row=7, column=0, sticky="w", pady=(10, 4))
        ttk.Entry(input_frame, textvariable=self.period_name_var, width=20).grid(
            row=7, column=1, columnspan=2, sticky="ew", pady=(10, 4)
        )
        ttk.Label(input_frame, text="Сценарий").grid(row=8, column=0, sticky="w", pady=4)
        ttk.Entry(input_frame, textvariable=self.scenario_name_var, width=20).grid(
            row=8, column=1, columnspan=2, sticky="ew", pady=4
        )

        action_frame = ttk.LabelFrame(parent, text="Действия", padding=10)
        action_frame.grid(row=1, column=0, sticky="new", pady=(10, 0))

        self.calculate_button = ttk.Button(action_frame, text="Рассчитать")
        self.calculate_button.grid(row=0, column=0, sticky="ew", pady=3)
        self.add_period_button = ttk.Button(action_frame, text="Добавить период")
        self.add_period_button.grid(row=1, column=0, sticky="ew", pady=3)
        self.add_scenario_button = ttk.Button(action_frame, text="Добавить сценарий")
        self.add_scenario_button.grid(row=2, column=0, sticky="ew", pady=3)
        self.clear_button = ttk.Button(action_frame, text="Очистить периоды/сценарии")
        self.clear_button.grid(row=3, column=0, sticky="ew", pady=3)

        storage_frame = ttk.LabelFrame(parent, text="Файлы", padding=10)
        storage_frame.grid(row=2, column=0, sticky="new", pady=(10, 0))

        self.load_button = ttk.Button(storage_frame, text="Загрузить JSON/CSV")
        self.load_button.grid(row=0, column=0, sticky="ew", pady=3)
        self.save_json_button = ttk.Button(storage_frame, text="Сохранить JSON")
        self.save_json_button.grid(row=1, column=0, sticky="ew", pady=3)
        self.export_csv_button = ttk.Button(storage_frame, text="Экспорт CSV")
        self.export_csv_button.grid(row=2, column=0, sticky="ew", pady=3)
        self.export_html_button = ttk.Button(storage_frame, text="Экспорт HTML")
        self.export_html_button.grid(row=3, column=0, sticky="ew", pady=3)

        result_frame = ttk.LabelFrame(parent, text="Результат", padding=10)
        result_frame.grid(row=3, column=0, sticky="new", pady=(10, 0))
        ttk.Label(result_frame, textvariable=self.result_var, font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            result_frame,
            textvariable=self.interpretation_var,
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _build_tables(self, parent: ttk.Frame) -> None:
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        current_tab = ttk.Frame(notebook, padding=8)
        periods_tab = ttk.Frame(notebook, padding=8)
        scenarios_tab = ttk.Frame(notebook, padding=8)
        for tab in (current_tab, periods_tab, scenarios_tab):
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)

        notebook.add(current_tab, text="Текущий ввод")
        notebook.add(periods_tab, text="Периоды")
        notebook.add(scenarios_tab, text="Сценарии")

        current_columns = ("R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация")
        self.current_tree = self._make_tree(current_tab, current_columns, heights=4)

        period_columns = ("Период", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация")
        self.period_tree = self._make_tree(periods_tab, period_columns, heights=8)

        scenario_columns = ("Сценарий", "R", "S", "E", "aR", "aS", "aE", "I", "Интерпретация")
        self.scenario_tree = self._make_tree(scenarios_tab, scenario_columns, heights=8)

    def _build_charts(self, parent: ttk.Frame) -> None:
        chart_frame = ttk.LabelFrame(parent, text="Графики", padding=8)
        chart_frame.grid(row=1, column=0, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.figure = Figure(figsize=(10, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.render_charts(None, [], [])

    def _make_tree(self, parent: ttk.Frame, columns: tuple[str, ...], heights: int) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=heights)
        for column in columns:
            tree.heading(column, text=column)
            width = 115 if column in {"Интерпретация"} else 85
            if column in {"Период", "Сценарий"}:
                width = 140
            tree.column(column, width=width, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def set_callbacks(self, callbacks: dict[str, object]) -> None:
        self.apply_preset_button.configure(command=callbacks["apply_preset"])
        self.calculate_button.configure(command=callbacks["calculate"])
        self.add_period_button.configure(command=callbacks["add_period"])
        self.add_scenario_button.configure(command=callbacks["add_scenario"])
        self.clear_button.configure(command=callbacks["clear"])
        self.load_button.configure(command=callbacks["load"])
        self.save_json_button.configure(command=callbacks["save_json"])
        self.export_csv_button.configure(command=callbacks["export_csv"])
        self.export_html_button.configure(command=callbacks["export_html"])

    def get_form_data(self) -> dict[str, str]:
        return {
            "preset": self.preset_var.get(),
            "retrospective": self.r_var.get(),
            "statistics": self.s_var.get(),
            "expert": self.e_var.get(),
            "weight_r": self.ar_var.get(),
            "weight_s": self.as_var.get(),
            "weight_e": self.ae_var.get(),
            "period_name": self.period_name_var.get(),
            "scenario_name": self.scenario_name_var.get(),
        }

    def set_weights(self, retrospective: float, statistics: float, expert: float) -> None:
        self.ar_var.set(f"{retrospective:.2f}")
        self.as_var.set(f"{statistics:.2f}")
        self.ae_var.set(f"{expert:.2f}")

    def set_input_values(self, data: IndicatorInput) -> None:
        self.r_var.set(f"{data.retrospective:.2f}")
        self.s_var.set(f"{data.statistics:.2f}")
        self.e_var.set(f"{data.expert:.2f}")
        self.set_weights(
            data.weights.retrospective,
            data.weights.statistics,
            data.weights.expert,
        )

    def set_result(self, result: CalculationResult | None) -> None:
        if result is None:
            self.result_var.set("I = -")
            self.interpretation_var.set("Интерпретация появится после расчёта.")
            return
        self.result_var.set(f"I = {result.value:.3f}")
        self.interpretation_var.set(result.interpretation)

    def refresh_tables(self, state: AppState) -> None:
        self._replace_tree_rows(self.current_tree, [])
        if state.current_input and state.current_result:
            self._replace_tree_rows(
                self.current_tree,
                [
                    (
                        f"{state.current_input.retrospective:.3f}",
                        f"{state.current_input.statistics:.3f}",
                        f"{state.current_input.expert:.3f}",
                        f"{state.current_input.weights.retrospective:.3f}",
                        f"{state.current_input.weights.statistics:.3f}",
                        f"{state.current_input.weights.expert:.3f}",
                        f"{state.current_result.value:.3f}",
                        state.current_result.interpretation,
                    )
                ],
            )
        self._replace_tree_rows(
            self.period_tree,
            [
                (
                    item.period_name,
                    f"{item.data.retrospective:.3f}",
                    f"{item.data.statistics:.3f}",
                    f"{item.data.expert:.3f}",
                    f"{item.data.weights.retrospective:.3f}",
                    f"{item.data.weights.statistics:.3f}",
                    f"{item.data.weights.expert:.3f}",
                    f"{item.result.value:.3f}",
                    item.result.interpretation,
                )
                for item in state.periods
            ],
        )
        self._replace_tree_rows(
            self.scenario_tree,
            [
                (
                    item.scenario_name,
                    f"{item.data.retrospective:.3f}",
                    f"{item.data.statistics:.3f}",
                    f"{item.data.expert:.3f}",
                    f"{item.data.weights.retrospective:.3f}",
                    f"{item.data.weights.statistics:.3f}",
                    f"{item.data.weights.expert:.3f}",
                    f"{item.result.value:.3f}",
                    item.result.interpretation,
                )
                for item in state.scenarios
            ],
        )

    def render_charts(self, current_result: CalculationResult | None, periods, scenarios) -> None:
        self.figure.clear()
        axes = self.figure.subplots(3, 1)
        self.figure.subplots_adjust(hspace=0.6, left=0.08, right=0.98, top=0.96, bottom=0.06)

        current_axis, periods_axis, scenarios_axis = axes
        current_axis.set_title("Вклад компонентов и итоговый ИПУР")
        current_axis.set_ylim(0, 1)

        if current_result is None:
            self._empty_axis(current_axis, "Выполните расчёт, чтобы увидеть вклад компонентов.")
        else:
            bars = [
                current_result.contribution_retrospective,
                current_result.contribution_statistics,
                current_result.contribution_expert,
                current_result.value,
            ]
            labels = ["R", "S", "E", "I"]
            colors = ["#3b82f6", "#0ea5e9", "#8b5cf6", self._result_color(current_result.interpretation)]
            current_axis.bar(labels, bars, color=colors)
            current_axis.grid(axis="y", alpha=0.3)

        periods_axis.set_title("Динамика ИПУР по периодам")
        periods_axis.set_ylim(0, 1)
        if not periods:
            self._empty_axis(periods_axis, "Добавьте хотя бы один период.")
        else:
            periods_axis.plot(
                [item.period_name for item in periods],
                [item.result.value for item in periods],
                marker="o",
                color="#2563eb",
            )
            periods_axis.grid(alpha=0.3)
            periods_axis.tick_params(axis="x", rotation=25)

        scenarios_axis.set_title("Сравнение сценариев")
        scenarios_axis.set_ylim(0, 1)
        if not scenarios:
            self._empty_axis(scenarios_axis, "Добавьте 2-3 сценария для сравнения.")
        else:
            scenario_values = [item.result.value for item in scenarios]
            scenario_colors = [self._result_color(item.result.interpretation) for item in scenarios]
            scenarios_axis.bar(
                [item.scenario_name for item in scenarios],
                scenario_values,
                color=scenario_colors,
            )
            scenarios_axis.grid(axis="y", alpha=0.3)
            scenarios_axis.tick_params(axis="x", rotation=15)

        self.canvas.draw_idle()

    def _empty_axis(self, axis, text: str) -> None:
        axis.set_xticks([])
        axis.set_yticks([0, 0.5, 1.0])
        axis.grid(axis="y", alpha=0.2)
        axis.text(0.5, 0.5, text, transform=axis.transAxes, ha="center", va="center")

    def _replace_tree_rows(self, tree: ttk.Treeview, rows: list[tuple[object, ...]]) -> None:
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=row)

    def _result_color(self, interpretation: str) -> str:
        if interpretation == HIGH_TEXT:
            return "#16a34a"
        if interpretation == MEDIUM_TEXT:
            return "#eab308"
        if interpretation == LOW_TEXT:
            return "#dc2626"
        return "#64748b"

    def ask_open_path(self) -> str:
        return filedialog.askopenfilename(
            title="Загрузка данных",
            filetypes=[("JSON и CSV", "*.json *.csv"), ("JSON", "*.json"), ("CSV", "*.csv")],
        )

    def ask_save_json_path(self) -> str:
        return filedialog.asksaveasfilename(
            title="Сохранить состояние в JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )

    def ask_save_csv_path(self) -> str:
        return filedialog.asksaveasfilename(
            title="Экспорт в CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )

    def ask_save_html_path(self) -> str:
        return filedialog.asksaveasfilename(
            title="Экспорт отчёта в HTML",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
        )

    def show_error(self, message: str) -> None:
        messagebox.showerror("Ошибка", message)

    def show_info(self, message: str) -> None:
        messagebox.showinfo("ИПУР", message)

    def start(self) -> None:
        self.root.mainloop()
