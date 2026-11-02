import argparse
import csv
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ruta import Stage, accelerate_exact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="resultados/benchmark.csv")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in (10, 20, 40, 80, 120, 160):
        budget = n * 4
        rng = random.Random(2026 + n)
        stages = [
            Stage(f"S{i}", rng.randint(10, 100), rng.randint(1, 8), rng.randint(1, 10))
            for i in range(n)
        ]
        start = time.perf_counter()
        result = accelerate_exact(stages, budget)
        elapsed = time.perf_counter() - start
        rows.append({"n": n, "budget": budget, "seconds": elapsed, "duration": result["duration"]})
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Resultados guardados en {output}")


if __name__ == "__main__":
    main()
