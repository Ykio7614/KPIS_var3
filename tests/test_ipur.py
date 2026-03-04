import unittest

from app.controllers.validation import ValidationError, build_input_from_raw
from app.domain.formulas.ipur import HIGH_TEXT, LOW_TEXT, MEDIUM_TEXT, calculate_ipur


class IpurFormulaTests(unittest.TestCase):
    def test_scenario_i_matches_spec(self) -> None:
        data = build_input_from_raw(
            label="Сценарий I",
            retrospective="0.7",
            statistics="0.733",
            expert="0.35",
            weight_r="0.3",
            weight_s="0.4",
            weight_e="0.3",
        )
        result = calculate_ipur(data)

        self.assertEqual(result.value, 0.608)
        self.assertEqual(result.interpretation, HIGH_TEXT)

    def test_scenario_ii_matches_spec(self) -> None:
        data = build_input_from_raw(
            label="Сценарий II",
            retrospective="0.8",
            statistics="0.0",
            expert="0.4",
            weight_r="0.2",
            weight_s="0.6",
            weight_e="0.2",
        )
        result = calculate_ipur(data)

        self.assertEqual(result.value, 0.24)
        self.assertEqual(result.interpretation, LOW_TEXT)

    def test_scenario_iii_matches_spec(self) -> None:
        data = build_input_from_raw(
            label="Сценарий III",
            retrospective="0.3",
            statistics="0.5",
            expert="0.8",
            weight_r="0.4",
            weight_s="0.3",
            weight_e="0.3",
        )
        result = calculate_ipur(data)

        self.assertEqual(result.value, 0.51)
        self.assertEqual(result.interpretation, MEDIUM_TEXT)

    def test_validation_requires_weight_sum_one(self) -> None:
        with self.assertRaises(ValidationError) as context:
            build_input_from_raw(
                label="Ошибка",
                retrospective="0.5",
                statistics="0.5",
                expert="0.5",
                weight_r="0.2",
                weight_s="0.2",
                weight_e="0.2",
            )
        self.assertIn("Сумма весов", str(context.exception))


if __name__ == "__main__":
    unittest.main()
