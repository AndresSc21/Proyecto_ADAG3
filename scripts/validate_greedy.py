"""Compara el Set Cover voraz con el óptimo por fuerza bruta en casos pequeños."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ruta import Interaction, audit_greedy, audit_optimal_cardinality


CASES = [
    (
        {"a", "b", "c", "d"},
        [
            Interaction("I1", frozenset({"a", "b"})),
            Interaction("I2", frozenset({"c"})),
            Interaction("I3", frozenset({"d"})),
            Interaction("I4", frozenset({"a", "c", "d"})),
        ],
    ),
    (
        {"r1", "r2", "r3", "r4", "r5"},
        [
            Interaction("I1", frozenset({"r1", "r2", "r3"})),
            Interaction("I2", frozenset({"r4"})),
            Interaction("I3", frozenset({"r5"})),
            Interaction("I4", frozenset({"r1", "r4", "r5"})),
        ],
    ),
]


def main() -> None:
    results = []
    for index, (risks, interactions) in enumerate(CASES, start=1):
        greedy = audit_greedy(interactions, risks)
        optimal = audit_optimal_cardinality(interactions, risks)
        results.append(
            {
                "case": index,
                "greedy_count": len(greedy["selected"]),
                "optimal_count": len(optimal["selected"]),
                "within_bound": len(greedy["selected"]) >= len(optimal["selected"]),
            }
        )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
