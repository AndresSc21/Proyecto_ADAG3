import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ruta import (
    DagStage,
    Interaction,
    Stage,
    accelerate_exact,
    audit_greedy,
    audit_weighted_cost,
    combined_budget,
    dag_exact,
    dag_greedy,
)


def _load_case(path: str) -> dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    required = ("budget", "stages", "risks", "interactions")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")
    if not isinstance(data["stages"], list) or not isinstance(data["interactions"], list):
        raise ValueError("'stages' e 'interactions' deben ser listas.")
    if not isinstance(data["risks"], list):
        raise ValueError("'risks' debe ser una lista.")
    return data


def _jsonable(value: object) -> object:
    if isinstance(value, set | frozenset):
        return sorted(value)
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if hasattr(value, "name") and hasattr(value, "__dataclass_fields__"):
        return value.name
    return value


def build_result(path: str) -> dict[str, object]:
    data = _load_case(path)
    stages = [Stage(**item) for item in data["stages"]]
    interactions = [
        Interaction(item["name"], frozenset(item["risks"]), item.get("cost", 1))
        for item in data["interactions"]
    ]
    risks = set(data["risks"])
    start = time.perf_counter()
    acceleration = accelerate_exact(stages, data["budget"])
    audit = audit_greedy(interactions, risks)
    weighted_audit = audit_weighted_cost(interactions, risks)
    elapsed = time.perf_counter() - start
    result = {
        "name": data.get("name", Path(path).stem),
        "source": str(Path(path)),
        "elapsed_seconds": elapsed,
        "acceleration": acceleration,
        "audit": audit,
        "weighted_audit": weighted_audit,
        "combined_budget": combined_budget(stages, interactions, risks, data["budget"]),
        "verification": {
            "acceleration_budget_respected": acceleration["total_cost"] <= data["budget"],
            "audit_covers_all_risks": audit["feasible"] and audit["covered"] == risks,
            "weighted_audit_covers_all_risks": (
                weighted_audit["feasible"] and weighted_audit["covered"] == risks
            ),
        },
    }
    if "edges" in data:
        dag_stages = [DagStage(**item) for item in data["stages"]]
        edges = [tuple(edge) for edge in data["edges"]]
        result["dag"] = {
            "exact": dag_exact(dag_stages, edges, data["budget"]),
            "greedy": dag_greedy(dag_stages, edges, data["budget"]),
        }
    return _jsonable(result)


def main(path: str) -> None:
    print(json.dumps(build_result(path), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/run_case.py ruta/al/caso.json")
    main(sys.argv[1])
