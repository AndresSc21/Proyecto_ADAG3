import unittest

from src.ruta import (
    DagStage,
    Interaction,
    Stage,
    accelerate_exact,
    audit_greedy,
    audit_optimal_cardinality,
    audit_weighted_cost,
    combined_budget,
    dag_exact,
    dag_greedy,
)


class RutaTests(unittest.TestCase):
    def test_acceleration_respects_budget_and_finds_optimum(self):
        stages = [
            Stage("A", 10, 3, 5),
            Stage("B", 10, 4, 6),
            Stage("C", 10, 5, 10),
        ]
        result = accelerate_exact(stages, 7)
        self.assertEqual(result["reduction"], 11)
        self.assertEqual(result["total_cost"], 7)
        self.assertEqual([stage.name for stage in result["selected"]], ["A", "B"])

    def test_greedy_covers_all_risks(self):
        interactions = [
            Interaction("I1", frozenset({"a", "b"})),
            Interaction("I2", frozenset({"c"})),
            Interaction("I3", frozenset({"a"})),
        ]
        result = audit_greedy(interactions, {"a", "b", "c"})
        self.assertTrue(result["feasible"])
        self.assertEqual(result["covered"], {"a", "b", "c"})
        self.assertEqual([item.name for item in result["selected"]], ["I1", "I2"])

    def test_reports_infeasible_cover(self):
        result = audit_greedy([Interaction("I1", frozenset({"a"}))], {"a", "b"})
        self.assertFalse(result["feasible"])

    def test_weighted_variant_minimizes_cost_per_marginal_risk(self):
        interactions = [
            Interaction("cheap", frozenset({"a"}), 1),
            Interaction("bundle", frozenset({"b", "c"}), 2),
            Interaction("expensive", frozenset({"a", "b", "c"}), 10),
        ]
        result = audit_weighted_cost(interactions, {"a", "b", "c"})
        self.assertTrue(result["feasible"])
        self.assertEqual(result["total_cost"], 3)

    def test_combined_budget_uses_exact_audit_cost_before_acceleration(self):
        result = combined_budget(
            [Stage("S1", 10, 3, 5)],
            [Interaction("I1", frozenset({"a"}), 2)],
            {"a"},
            5,
        )
        self.assertTrue(result["feasible"])
        self.assertEqual(result["audit"]["total_cost"], 2)
        self.assertEqual(result["acceleration"]["total_cost"], 3)

    def test_dag_exact_and_greedy_return_valid_solutions(self):
        stages = [
            DagStage("A", 5, 2, 2),
            DagStage("B", 8, 3, 4),
            DagStage("C", 4, 2, 3),
        ]
        edges = [("A", "B"), ("A", "C")]
        exact = dag_exact(stages, edges, 3)
        greedy = dag_greedy(stages, edges, 3)
        self.assertEqual(exact["duration"], 9)
        self.assertLessEqual(exact["total_cost"], 3)
        self.assertLessEqual(greedy["total_cost"], 3)

    def test_dag_heuristic_counterexample_is_not_optimal(self):
        stages = [
            DagStage("S0", 5, 2, 4),
            DagStage("S1", 4, 4, 1),
            DagStage("S2", 7, 5, 6),
        ]
        edges = [("S0", "S2"), ("S1", "S2")]
        exact = dag_exact(stages, edges, 6)
        greedy = dag_greedy(stages, edges, 6)
        self.assertGreater(greedy["duration"], exact["duration"])

    def test_greedy_is_compared_with_small_instance_optimum(self):
        interactions = [
            Interaction("I1", frozenset({"a", "b"})),
            Interaction("I2", frozenset({"c"})),
            Interaction("I3", frozenset({"a", "c"})),
        ]
        greedy = audit_greedy(interactions, {"a", "b", "c"})
        optimal = audit_optimal_cardinality(interactions, {"a", "b", "c"})
        self.assertGreaterEqual(len(greedy["selected"]), len(optimal["selected"]))


if __name__ == "__main__":
    unittest.main()
