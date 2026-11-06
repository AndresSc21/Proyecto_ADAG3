# Proyecto_ADAG3 — Ruta

Primera entrega de **Análisis y Diseño de Algoritmos 2026-B**.

Integrantes:

- Andres Felipe Salazar
- Manuel Alejandro Hurtado

## Alcance

La solución implementa:

1. Aceleración óptima de una cadena de etapas mediante Mochila 0/1 y programación dinámica.
2. Cobertura de auditoría mediante el algoritmo voraz de Set Cover.
3. Variante de auditoría ponderada por costo.
4. Optimización conjunta de auditoría y aceleración bajo un presupuesto único.
5. Flujo DAG: ruta crítica, solución exacta por enumeración y heurística.
6. Comparación del voraz contra el óptimo en instancias pequeñas.
7. Trazas reproducibles de decisiones, costos, reducciones y cobertura.
8. Generación de instancias sintéticas y medición de tiempos.

Los casos privados de la profesora todavía no han sido entregados. Cuando estén disponibles, deben guardarse como JSON en `data/casos_profesora/` y ejecutarse con el mismo comando, sin modificar la lógica.

## Requisitos

- Python 3.10 o superior.
- No se requieren dependencias externas para ejecutar la solución.

## Ejecución

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
python scripts/run_demo.py
python scripts/benchmark.py --output resultados/benchmark.csv
```

Para ejecutar un caso JSON:

```powershell
python scripts/run_case.py data/casos_profesora/caso_01.json
```

La salida incluye el resultado y la traza exigida por la guía: estados de programación dinámica, etapas aceleradas, costos, ganancias marginales y cobertura de auditoría.

Para ejecutar todos los casos y guardar una evidencia consolidada:

```powershell
python scripts/run_cases.py data/casos_profesora --output resultados/casos_profesora.json
```

La salida de cada caso incluye tiempo, verificación de restricciones y trazas
de programación dinámica y auditoría.

Para validar empíricamente el voraz frente al óptimo por fuerza bruta:

```powershell
python scripts/validate_greedy.py
```

Para comparar el DAG exacto con una instancia donde la heurística no es óptima:

```powershell
python scripts/validate_dag.py
```

El archivo `entrada_G3_mochila_20_nodos.json` es un caso de ejemplo
suministrado para probar el algoritmo. Acepta el formato específico de la
entrada y se puede reproducir con:

```powershell
python scripts/run_case.py entrada_G3_mochila_20_nodos.json > resultados/entrada_G3_mochila_20_nodos.json
```

La evidencia generada está en `resultados/entrada_G3_mochila_20_nodos.json`.
Para verla en forma de tabla, ejecutar:

```powershell
python scripts/generate_summary.py entrada_G3_mochila_20_nodos.json `
  --csv resultados/entrada_G3_mochila_20_nodos_resumen.csv `
  --markdown resultados/entrada_G3_mochila_20_nodos_resumen.md
```

## Formato de caso

```json
{
  "name": "caso_01",
  "budget": 10,
  "stages": [
    {"name": "S1", "duration": 12, "cost": 4, "reduction": 5}
  ],
  "risks": ["sesgo", "datos", "formato"],
  "interactions": [
    {"name": "I1", "risks": ["sesgo", "datos"], "cost": 3}
  ],
  "risk_weights": {"sesgo": 2, "datos": 5, "formato": 1}
}
```

`cost` en las interacciones se usa para la variante ponderada. La primera parte usa `budget`, `stages[].cost` y `stages[].reduction`.

## Estructura

- `informe_tecnico.md`: formalización, reducciones y complejidad.
- `manual_tecnico.md`: arquitectura, formatos, ejecución y limitaciones.
- `src/ruta.py`: algoritmos y validaciones.
- `scripts/run_demo.py`: demostración con una instancia conocida.
- `scripts/run_case.py`: ejecución de casos externos.
- `scripts/run_cases.py`: ejecución consolidada de todos los casos JSON.
- `scripts/validate_greedy.py`: comparación experimental voraz/óptimo.
- `scripts/validate_dag.py`: comparación exacta/heurística del DAG.
- `scripts/benchmark.py`: experimentación con tamaños crecientes.
- `tests/`: pruebas automatizadas.
- `data/casos_profesora/`: ubicación reservada para los casos oficiales.
- `entrada_G3_mochila_20_nodos.json`: entrada de ejemplo suministrada.
- `resultados/entrada_G3_mochila_20_nodos.json`: evidencia reproducible del ejemplo.
