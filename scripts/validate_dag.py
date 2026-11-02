"""Compara la solución exacta del DAG con la heurística en un contraejemplo."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ruta import DagStage, dag_exact, dag_greedy


def main() -> None:
    stages = [
        DagStage("S0", duration=5, cost=2, reduction=4),
        DagStage("S1", duration=4, cost=4, reduction=1),
        DagStage("S2", duration=7, cost=5, reduction=6),
    ]
    edges = [("S0", "S2"), ("S1", "S2")]
    exact = dag_exact(stages, edges, budget=6)
    greedy = dag_greedy(stages, edges, budget=6)
    print(
        json.dumps(
            {
                "exact": exact,
                "greedy": greedy,
                "heuristic_is_not_optimal": greedy["duration"] > exact["duration"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
