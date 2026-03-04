from __future__ import annotations

from app.models.entities import IndicatorInput, WeightSet


class ValidationError(ValueError):
    """Ошибка пользовательского ввода."""


def build_input_from_raw(
    *,
    label: str,
    retrospective: str | float,
    statistics: str | float,
    expert: str | float,
    weight_r: str | float,
    weight_s: str | float,
    weight_e: str | float,
) -> IndicatorInput:
    parsed_retrospective = _parse_unit_interval("R", retrospective)
    parsed_statistics = _parse_unit_interval("S", statistics)
    parsed_expert = _parse_unit_interval("E", expert)
    weights = WeightSet(
        retrospective=_parse_unit_interval("aR", weight_r),
        statistics=_parse_unit_interval("aS", weight_s),
        expert=_parse_unit_interval("aE", weight_e),
    )
    weight_sum = round(sum(weights.as_tuple()), 6)
    if abs(weight_sum - 1.0) > 0.000001:
        raise ValidationError(
            f"Сумма весов должна быть равна 1. Сейчас: {weight_sum:.3f}. "
            "Скорректируйте aR, aS и aE."
        )
    return IndicatorInput(
        label=label.strip(),
        retrospective=parsed_retrospective,
        statistics=parsed_statistics,
        expert=parsed_expert,
        weights=weights,
    )


def _parse_unit_interval(name: str, value: str | float) -> float:
    raw = str(value).replace(",", ".").strip()
    try:
        parsed = float(raw)
    except ValueError as error:
        raise ValidationError(f"Поле {name} должно быть числом от 0 до 1.") from error
    if parsed < 0 or parsed > 1:
        raise ValidationError(f"Поле {name} должно находиться в диапазоне от 0 до 1.")
    return round(parsed, 3)
