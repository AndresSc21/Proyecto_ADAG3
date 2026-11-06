"""Genera tablas legibles a partir de la evidencia JSON de un caso."""

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    acceleration = data["acceleration"]
    combined = data["combined_budget"]
    rows = [
        {
            "seccion": "Aceleracion",
            "seleccionados": ", ".join(acceleration["selected"]),
            "costo": acceleration["total_cost"],
            "reduccion": acceleration["reduction"],
            "duracion": acceleration["duration"],
            "factible": data["verification"]["acceleration_budget_respected"],
        },
        {
            "seccion": "Auditoria voraz",
            "seleccionados": ", ".join(data["audit"]["selected"]),
            "costo": data["audit"]["total_cost"],
            "reduccion": "N/A",
            "duracion": "N/A",
            "factible": data["verification"]["audit_covers_all_risks"],
        },
        {
            "seccion": "Auditoria ponderada",
            "seleccionados": ", ".join(data["weighted_audit"]["selected"]),
            "costo": data["weighted_audit"]["total_cost"],
            "reduccion": "N/A",
            "duracion": "N/A",
            "factible": data["verification"]["weighted_audit_covers_all_risks"],
        },
        {
            "seccion": "Presupuesto conjunto",
            "seleccionados": (
                "Auditoria: "
                + ", ".join(combined["audit"]["selected"])
                + " | Aceleracion: "
                + ", ".join(combined["acceleration"]["selected"])
            ),
            "costo": combined["total_cost"],
            "reduccion": combined["acceleration"]["reduction"],
            "duracion": combined["acceleration"]["duration"],
            "factible": data["verification"]["combined_budget_respected"],
        },
    ]
    output_csv = Path(args.csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    output_md = Path(args.markdown)
    lines = [
        "# Resumen del caso G3",
        "",
        f"- Tiempo de ejecución: `{data['elapsed_seconds']:.6f}` segundos",
        f"- Estados DP registrados: `{len(acceleration['trace'])}`",
        "",
        "| Sección | Seleccionados | Costo | Reducción | Duración | Factible |",
        "|---|---|---:|---:|---:|:---:|",
    ]
    for row in rows:
        selected = row["seleccionados"].replace("|", "\\|")
        lines.append(
            f"| {row['seccion']} | {selected} | {row['costo']} | "
            f"{row['reduccion']} | {row['duracion']} | {row['factible']} |"
        )
    lines.extend(
        [
            "",
            "La tabla resume el resultado; la traza completa de cada estado DP "
            "está en el archivo JSON original.",
        ]
    )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
