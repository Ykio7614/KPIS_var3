from __future__ import annotations

from app.models.entities import CalculationResult, IndicatorInput

HIGH_TEXT = "Высокий уровень защищённости (можно сохранять текущую стратегию)"
MEDIUM_TEXT = "Удовлетворительный уровень (требуется внимание, мониторинг)"
LOW_TEXT = "Повышенный риск (требуется немедленное вмешательство)"


def calculate_ipur(data: IndicatorInput) -> CalculationResult:
    contribution_retrospective = data.weights.retrospective * data.retrospective
    contribution_statistics = data.weights.statistics * data.statistics
    contribution_expert = data.weights.expert * data.expert
    total = contribution_retrospective + contribution_statistics + contribution_expert
    return CalculationResult(
        value=round(total, 3),
        interpretation=interpret_ipur(total),
        contribution_retrospective=round(contribution_retrospective, 3),
        contribution_statistics=round(contribution_statistics, 3),
        contribution_expert=round(contribution_expert, 3),
    )


def interpret_ipur(value: float) -> str:
    if value >= 0.6:
        return HIGH_TEXT
    if value >= 0.4:
        return MEDIUM_TEXT
    return LOW_TEXT
