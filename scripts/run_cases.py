"""Ejecuta todos los casos JSON de una carpeta y conserva evidencia reproducible."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_case import build_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default="data/casos_profesora")
    parser.add_argument("--output", default="resultados/casos_profesora.json")
    args = parser.parse_args()

    directory = Path(args.directory)
    cases = sorted(directory.glob("*.json"))
    if not cases:
        raise SystemExit(
            f"No hay casos JSON en {directory}. Guarde allí los archivos de la profesora."
        )

    results = [build_result(str(path)) for path in cases]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(results)} casos ejecutados. Evidencia guardada en {output}")


if __name__ == "__main__":
    main()
