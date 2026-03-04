from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WeightSet:
    retrospective: float
    statistics: float
    expert: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.retrospective, self.statistics, self.expert)


@dataclass(slots=True)
class IndicatorInput:
    retrospective: float
    statistics: float
    expert: float
    weights: WeightSet
    label: str = ""


@dataclass(slots=True)
class CalculationResult:
    value: float
    interpretation: str
    contribution_retrospective: float
    contribution_statistics: float
    contribution_expert: float


@dataclass(slots=True)
class PeriodRecord:
    period_name: str
    data: IndicatorInput
    result: CalculationResult


@dataclass(slots=True)
class ScenarioRecord:
    scenario_name: str
    data: IndicatorInput
    result: CalculationResult


@dataclass(slots=True)
class AppState:
    current_input: IndicatorInput | None = None
    current_result: CalculationResult | None = None
    periods: list[PeriodRecord] = field(default_factory=list)
    scenarios: list[ScenarioRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_input": _input_to_dict(self.current_input),
            "current_result": _result_to_dict(self.current_result),
            "periods": [
                {
                    "period_name": item.period_name,
                    "data": _input_to_dict(item.data),
                    "result": _result_to_dict(item.result),
                }
                for item in self.periods
            ],
            "scenarios": [
                {
                    "scenario_name": item.scenario_name,
                    "data": _input_to_dict(item.data),
                    "result": _result_to_dict(item.result),
                }
                for item in self.scenarios
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AppState":
        state = cls()
        if payload.get("current_input"):
            state.current_input = _input_from_dict(payload["current_input"])
        if payload.get("current_result"):
            state.current_result = _result_from_dict(payload["current_result"])

        state.periods = [
            PeriodRecord(
                period_name=item["period_name"],
                data=_input_from_dict(item["data"]),
                result=_result_from_dict(item["result"]),
            )
            for item in payload.get("periods", [])
        ]
        state.scenarios = [
            ScenarioRecord(
                scenario_name=item["scenario_name"],
                data=_input_from_dict(item["data"]),
                result=_result_from_dict(item["result"]),
            )
            for item in payload.get("scenarios", [])
        ]
        return state


def _input_to_dict(data: IndicatorInput | None) -> dict[str, Any] | None:
    if data is None:
        return None
    return {
        "label": data.label,
        "retrospective": data.retrospective,
        "statistics": data.statistics,
        "expert": data.expert,
        "weights": {
            "retrospective": data.weights.retrospective,
            "statistics": data.weights.statistics,
            "expert": data.weights.expert,
        },
    }


def _input_from_dict(payload: dict[str, Any]) -> IndicatorInput:
    weights = payload["weights"]
    return IndicatorInput(
        label=payload.get("label", ""),
        retrospective=float(payload["retrospective"]),
        statistics=float(payload["statistics"]),
        expert=float(payload["expert"]),
        weights=WeightSet(
            retrospective=float(weights["retrospective"]),
            statistics=float(weights["statistics"]),
            expert=float(weights["expert"]),
        ),
    )


def _result_to_dict(result: CalculationResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "value": result.value,
        "interpretation": result.interpretation,
        "contribution_retrospective": result.contribution_retrospective,
        "contribution_statistics": result.contribution_statistics,
        "contribution_expert": result.contribution_expert,
    }


def _result_from_dict(payload: dict[str, Any]) -> CalculationResult:
    return CalculationResult(
        value=float(payload["value"]),
        interpretation=str(payload["interpretation"]),
        contribution_retrospective=float(payload["contribution_retrospective"]),
        contribution_statistics=float(payload["contribution_statistics"]),
        contribution_expert=float(payload["contribution_expert"]),
    )
