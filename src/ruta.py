"""Solución reproducible para la primera entrega del proyecto ADAG 3."""

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Stage:
    name: str
    duration: int
    cost: int
    reduction: int


@dataclass(frozen=True)
class Interaction:
    name: str
    risks: frozenset[str]
    cost: int = 1


@dataclass(frozen=True)
class DagStage:
    name: str
    duration: int
    cost: int
    reduction: int


def _validate_stage(stage: Stage) -> None:
    if stage.duration < 0 or stage.cost < 0 or stage.reduction < 0:
        raise ValueError(f"Valores negativos en la etapa {stage.name}.")
    if stage.reduction > stage.duration:
        raise ValueError(f"La reducción excede la duración en {stage.name}.")


def accelerate_exact(
    stages: Iterable[Stage], budget: int
) -> dict[str, object]:
    """Maximiza la reducción total con Mochila 0/1 y devuelve traza completa."""
    if budget < 0:
        raise ValueError("El presupuesto no puede ser negativo.")
    items = list(stages)
    for stage in items:
        _validate_stage(stage)

    dp = [[0] * (budget + 1) for _ in range(len(items) + 1)]
    decisions: list[dict[str, int | str | bool]] = []
    for i, stage in enumerate(items, start=1):
        for used in range(budget + 1):
            without = dp[i - 1][used]
            with_item = -1
            if stage.cost <= used:
                with_item = dp[i - 1][used - stage.cost] + stage.reduction
            dp[i][used] = max(without, with_item)
            decisions.append(
                {
                    "stage": stage.name,
                    "budget": used,
                    "without": without,
                    "with": with_item,
                    "selected": with_item >= 0 and with_item >= without,
                    "best": dp[i][used],
                }
            )

    selected: list[Stage] = []
    remaining = budget
    for i in range(len(items), 0, -1):
        if dp[i][remaining] != dp[i - 1][remaining]:
            stage = items[i - 1]
            selected.append(stage)
            remaining -= stage.cost
    selected.reverse()
    reduction = dp[-1][-1]
    return {
        "selected": selected,
        "total_cost": sum(stage.cost for stage in selected),
        "reduction": reduction,
        "duration": sum(stage.duration for stage in items) - reduction,
        "trace": decisions,
        "complexity": f"O({len(items)}*{budget})",
    }


def audit_greedy(
    interactions: Iterable[Interaction], risks: Iterable[str]
) -> dict[str, object]:
    """Set Cover voraz: elige la interacción con mayor cobertura marginal."""
    candidates = list(interactions)
    universe = set(risks)
    max_risk_count = max((len(item.risks) for item in candidates), default=0)
    if any(interaction.cost < 0 for interaction in candidates):
        raise ValueError("El costo de una interacción no puede ser negativo.")
    if not universe:
        return {"selected": [], "covered": set(), "trace": [], "feasible": True}
    if set().union(*(item.risks for item in candidates)) < universe:
        return {
            "selected": [],
            "covered": set(),
            "trace": [],
            "feasible": False,
            "reason": "La unión de interacciones no cubre todos los riesgos.",
        }

    covered: set[str] = set()
    selected: list[Interaction] = []
    trace: list[dict[str, object]] = []
    while covered != universe:
        remaining = universe - covered
        best = max(
            candidates,
            key=lambda item: (len(item.risks & remaining), -item.cost, item.name),
            default=None,
        )
        if best is None or not (best.risks & remaining):
            return {
                "selected": selected,
                "covered": covered,
                "trace": trace,
                "feasible": False,
            }
        marginal = best.risks & remaining
        covered.update(marginal)
        selected.append(best)
        candidates.remove(best)
        trace.append(
            {
                "interaction": best.name,
                "marginal_risks": sorted(marginal),
                "covered_after": sorted(covered),
            }
        )
    return {
        "selected": selected,
        "covered": covered,
        "trace": trace,
        "feasible": True,
        "approximation_bound": (
            f"H_{max_risk_count} "
            f"<= 1 + ln({len(universe)})"
        ),
    }


def audit_weighted_cost(
    interactions: Iterable[Interaction], risks: Iterable[str]
) -> dict[str, object]:
    """Variante: minimiza costo usando costo por riesgo nuevo cubierto."""
    candidates = list(interactions)
    universe = set(risks)
    if any(item.cost < 0 for item in candidates):
        raise ValueError("El costo de una interacción no puede ser negativo.")
    covered: set[str] = set()
    selected: list[Interaction] = []
    trace: list[dict[str, object]] = []
    max_risk_count = max((len(item.risks) for item in candidates), default=0)
    if not universe:
        return {
            "selected": [],
            "covered": set(),
            "total_cost": 0,
            "trace": [],
            "feasible": True,
        }
    if set().union(*(item.risks for item in candidates)) < universe:
        return {
            "selected": [],
            "covered": set(),
            "total_cost": 0,
            "trace": [],
            "feasible": False,
            "reason": "La unión de interacciones no cubre todos los riesgos.",
        }
    while covered != universe:
        remaining = universe - covered
        feasible = [item for item in candidates if item.risks & remaining]
        if not feasible:
            return {
                "selected": selected,
                "covered": covered,
                "total_cost": sum(item.cost for item in selected),
                "trace": trace,
                "feasible": False,
            }
        best = min(
            feasible,
            key=lambda item: (
                item.cost / len(item.risks & remaining),
                item.cost,
                item.name,
            ),
        )
        marginal = best.risks & remaining
        covered.update(marginal)
        selected.append(best)
        candidates.remove(best)
        trace.append(
            {
                "interaction": best.name,
                "marginal_risks": sorted(marginal),
                "cost": best.cost,
                "cost_per_new_risk": best.cost / len(marginal),
                "covered_after": sorted(covered),
            }
        )
    return {
        "selected": selected,
        "covered": covered,
        "total_cost": sum(item.cost for item in selected),
        "trace": trace,
        "feasible": True,
        "approximation_bound": (
            f"H_{max_risk_count} "
            f"<= 1 + ln({len(universe)})"
        ),
    }


def audit_weighted_exact(
    interactions: Iterable[Interaction], risks: Iterable[str]
) -> dict[str, object]:
    """Encuentra la cobertura de costo mínimo con DP sobre máscaras de riesgos."""
    candidates = list(interactions)
    universe = set(risks)
    if not universe:
        return {"selected": [], "covered": set(), "total_cost": 0, "feasible": True}
    if set().union(*(item.risks for item in candidates)) < universe:
        return {"selected": [], "covered": set(), "total_cost": 0, "feasible": False}
    ordered_risks = sorted(universe)
    positions = {risk: index for index, risk in enumerate(ordered_risks)}
    full_mask = (1 << len(ordered_risks)) - 1
    states: dict[int, tuple[int, tuple[int, ...]]] = {0: (0, ())}
    for index, item in enumerate(candidates):
        item_mask = sum(1 << positions[risk] for risk in item.risks if risk in positions)
        for mask, (cost, selected_indexes) in list(states.items()):
            new_mask = mask | item_mask
            new_value = (cost + item.cost, selected_indexes + (index,))
            if new_mask not in states or new_value < states[new_mask]:
                states[new_mask] = new_value
    if full_mask not in states:
        return {"selected": [], "covered": set(), "total_cost": 0, "feasible": False}
    best_cost, indexes = states[full_mask]
    selected = [candidates[i] for i in indexes]
    return {
        "selected": selected,
        "covered": set().union(*(item.risks for item in selected)),
        "total_cost": best_cost,
        "feasible": True,
        "complexity": f"O({len(candidates)}*2^{len(universe)})",
    }


def audit_optimal_cardinality(
    interactions: Iterable[Interaction], risks: Iterable[str]
) -> dict[str, object]:
    """Calcula el óptimo de Set Cover por fuerza bruta para instancias pequeñas."""
    candidates = list(interactions)
    universe = set(risks)
    if not universe:
        return {"selected": [], "covered": set(), "feasible": True}
    for size in range(1, len(candidates) + 1):
        for indexes in combinations(range(len(candidates)), size):
            covered = set().union(*(candidates[i].risks for i in indexes))
            if covered >= universe:
                selected = [candidates[i] for i in indexes]
                return {
                    "selected": selected,
                    "covered": covered,
                    "feasible": True,
                    "complexity": f"O(2^{len(candidates)}*{len(universe)})",
                }
    return {"selected": [], "covered": set(), "feasible": False}


def combined_budget(
    stages: Iterable[Stage],
    interactions: Iterable[Interaction],
    risks: Iterable[str],
    budget: int,
) -> dict[str, object]:
    """Resuelve auditoría ponderada exacta y acelera con el presupuesto restante."""
    audit = audit_weighted_exact(interactions, risks)
    if not audit["feasible"] or audit["total_cost"] > budget:
        return {
            "feasible": False,
            "audit": audit,
            "reason": "No hay presupuesto suficiente para una cobertura completa.",
        }
    acceleration = accelerate_exact(stages, budget - audit["total_cost"])
    return {
        "feasible": True,
        "audit": audit,
        "acceleration": acceleration,
        "total_cost": audit["total_cost"] + acceleration["total_cost"],
        "remaining_budget": budget - audit["total_cost"],
    }


def _validate_dag(stages: Sequence[DagStage], edges: Sequence[tuple[str, str]]) -> None:
    names = {stage.name for stage in stages}
    if len(names) != len(stages):
        raise ValueError("Los nombres de las etapas DAG deben ser únicos.")
    if any(source not in names or target not in names for source, target in edges):
        raise ValueError("Las aristas DAG deben referenciar etapas existentes.")
    for stage in stages:
        if stage.duration < 0 or stage.cost < 0 or stage.reduction < 0:
            raise ValueError(f"Valores negativos en la etapa DAG {stage.name}.")
        if stage.reduction > stage.duration:
            raise ValueError(f"La reducción excede la duración en {stage.name}.")


def critical_path_duration(
    stages: Sequence[DagStage], edges: Sequence[tuple[str, str]], accelerated: set[str]
) -> int:
    """Calcula la duración de un DAG mediante orden topológico."""
    _validate_dag(stages, edges)
    names = {stage.name for stage in stages}
    outgoing = {name: [] for name in names}
    indegree = {name: 0 for name in names}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    queue = [name for name, degree in indegree.items() if degree == 0]
    distance = {name: 0 for name in names}
    by_name = {stage.name: stage for stage in stages}
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        duration = by_name[current].duration - (
            by_name[current].reduction if current in accelerated else 0
        )
        distance[current] += duration
        for target in outgoing[current]:
            distance[target] = max(distance[target], distance[current])
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(stages):
        raise ValueError("El grafo de etapas contiene un ciclo.")
    return max(distance.values(), default=0)


def _critical_path_nodes(
    stages: Sequence[DagStage], edges: Sequence[tuple[str, str]], accelerated: set[str]
) -> set[str]:
    _validate_dag(stages, edges)
    names = {stage.name for stage in stages}
    outgoing = {name: [] for name in names}
    incoming = {name: [] for name in names}
    indegree = {name: 0 for name in names}
    for source, target in edges:
        outgoing[source].append(target)
        incoming[target].append(source)
        indegree[target] += 1
    order: list[str] = []
    queue = [name for name, degree in indegree.items() if degree == 0]
    while queue:
        current = queue.pop(0)
        order.append(current)
        for target in outgoing[current]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(stages):
        raise ValueError("El grafo de etapas contiene un ciclo.")
    by_name = {stage.name: stage for stage in stages}
    duration = {
        name: by_name[name].duration
        - (by_name[name].reduction if name in accelerated else 0)
        for name in names
    }
    forward = {name: 0 for name in names}
    for name in order:
        forward[name] += duration[name]
        for target in outgoing[name]:
            forward[target] = max(forward[target], forward[name])
    backward = {name: 0 for name in names}
    for name in reversed(order):
        for target in outgoing[name]:
            backward[name] = max(backward[name], backward[target] + duration[target])
    longest = max(forward.values(), default=0)
    return {
        name for name in names if forward[name] + backward[name] == longest
    }


def dag_exact(
    stages: Sequence[DagStage], edges: Sequence[tuple[str, str]], budget: int
) -> dict[str, object]:
    """Solución exacta del DAG por enumeración de subconjuntos."""
    if budget < 0:
        raise ValueError("El presupuesto no puede ser negativo.")
    _validate_dag(stages, edges)
    best: tuple[int, int, tuple[str, ...]] | None = None
    for mask in range(1 << len(stages)):
        selected = tuple(
            stage.name for i, stage in enumerate(stages) if mask & (1 << i)
        )
        cost = sum(stage.cost for stage in stages if stage.name in selected)
        if cost > budget:
            continue
        duration = critical_path_duration(stages, edges, set(selected))
        candidate = (duration, cost, selected)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return {
        "selected": list(best[2]),
        "total_cost": best[1],
        "duration": best[0],
        "feasible": True,
        "complexity": f"O(2^{len(stages)}*({len(stages)}+{len(edges)}))",
    }


def dag_greedy(
    stages: Sequence[DagStage], edges: Sequence[tuple[str, str]], budget: int
) -> dict[str, object]:
    """Heurística: recalcula ruta crítica y elige d_i/c_i en ella."""
    if budget < 0:
        raise ValueError("El presupuesto no puede ser negativo.")
    _validate_dag(stages, edges)
    selected: set[str] = set()
    remaining = budget
    trace = []
    while True:
        current_duration = critical_path_duration(stages, edges, selected)
        critical = _critical_path_nodes(stages, edges, selected)
        candidates = [
            stage
            for stage in stages
            if stage.name in critical and stage.name not in selected
        ]
        candidates = [stage for stage in candidates if stage.cost <= remaining]
        if not candidates:
            break
        best = max(
            candidates,
            key=lambda stage: (
                stage.reduction / stage.cost if stage.cost else float("inf"),
                -stage.cost,
                stage.name,
            ),
        )
        selected.add(best.name)
        remaining -= best.cost
        new_duration = critical_path_duration(stages, edges, selected)
        trace.append(
            {
                "stage": best.name,
                "cost": best.cost,
                "duration_before": current_duration,
                "duration_after": new_duration,
            }
        )
    return {
        "selected": sorted(selected),
        "total_cost": budget - remaining,
        "duration": critical_path_duration(stages, edges, selected),
        "trace": trace,
        "complexity": f"O({len(stages)}*({len(stages)}+{len(edges)}))",
    }
