import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ruta import Interaction, Stage, accelerate_exact, audit_greedy, audit_weighted_cost


stages = [
    Stage("S1", 12, 4, 5),
    Stage("S2", 10, 6, 8),
    Stage("S3", 7, 3, 2),
    Stage("S4", 15, 5, 6),
]
interactions = [
    Interaction("I1", frozenset({"sesgo", "datos"}), 3),
    Interaction("I2", frozenset({"formato", "sesgo"}), 2),
    Interaction("I3", frozenset({"datos", "acceso"}), 4),
]
risks = {"sesgo", "datos", "formato", "acceso"}

result = {
    "acceleration": accelerate_exact(stages, 9),
    "audit": audit_greedy(interactions, risks),
    "weighted_audit": audit_weighted_cost(interactions, risks),
}
for key, value in result.items():
    if "selected" in value:
        value["selected"] = [item.name for item in value["selected"]]
    value["covered"] = sorted(value["covered"]) if "covered" in value else None
print(json.dumps(result, indent=2, ensure_ascii=False))
