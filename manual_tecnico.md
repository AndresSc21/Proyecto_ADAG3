# Manual técnico — Proyecto_ADAG3

## Instalación

No hay dependencias externas. Se recomienda Python 3.10 o superior:

```powershell
python --version
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Demostración

```powershell
python scripts/run_demo.py
```

La demostración imprime JSON con los nombres seleccionados, costos, duración,
riesgos cubiertos y trazas.

## Casos externos

Crear un archivo JSON según este esquema:

```json
{
  "name": "caso_01",
  "budget": 10,
  "stages": [
    {"name": "S1", "duration": 12, "cost": 4, "reduction": 5}
  ],
  "risks": ["sesgo", "datos"],
  "interactions": [
    {"name": "I1", "risks": ["sesgo", "datos"], "cost": 3}
  ]
}
```

Ejecutar:

```powershell
python scripts/run_case.py data/casos_profesora/caso_01.json
```

La salida se puede redirigir para conservar evidencia:

```powershell
python scripts/run_case.py data/casos_profesora/caso_01.json > resultados/caso_01.json
```

La salida de `run_case.py` contiene `elapsed_seconds` y `verification`, además
de las trazas. `run_cases.py` ejecuta todos los JSON de la carpeta y genera una
evidencia consolidada. Si la carpeta no contiene casos oficiales, el comando
termina con un mensaje explícito y no fabrica resultados.

El adaptador también acepta `entrada_G3_mochila_20_nodos.json`. Convierte
`etapas` en objetos de aceleración, convierte sus `variaciones_auditoria` en
interacciones y usa los presupuestos declarados en `parametros`. El presupuesto
de aceleración es 72 y el presupuesto conjunto es 100 en este ejemplo.
El resumen legible se genera con `scripts/generate_summary.py` en formatos CSV
y Markdown; el JSON conserva la traza detallada de todos los estados DP.

## Benchmark

```powershell
python scripts/benchmark.py --output resultados/benchmark.csv
```

El benchmark usa una semilla fija para que los resultados sean reproducibles.
La medición debe hacerse en el mismo equipo y sin comparar ejecuciones de
hardware distinto como si fueran una prueba de complejidad formal.

## Estructura del código

- `Stage` e `Interaction`: modelos inmutables de entrada.
- `accelerate_exact`: tabla DP, reconstrucción y traza.
- `audit_greedy`: Set Cover voraz y ganancias marginales.
- `audit_weighted_cost`: variante costo por riesgo nuevo.
- `audit_weighted_exact`: cobertura ponderada exacta por enumeración, usada para
  calcular el costo mínimo de auditoría en el presupuesto conjunto.
- `combined_budget`: auditoría exacta seguida de aceleración con el presupuesto
  restante.
- `critical_path_duration`: ruta crítica de un DAG en orden topológico.
- `dag_exact` y `dag_greedy`: solución exacta y heurística para el DAG.
- `run_case.py`: adaptador JSON, sin alterar los algoritmos.

## Variantes adicionales

Un caso con el campo opcional `edges` se interpreta también como un DAG. Las
aristas se expresan como pares `[origen, destino]`; `run_case.py` reporta la
solución exacta por enumeración y la heurística que recalcula la ruta crítica.
La salida normal incluye además `combined_budget`, que calcula la cobertura
ponderada exacta y usa el presupuesto sobrante para acelerar.

`validate_greedy.py` compara el número de interacciones del voraz con el
óptimo por fuerza bruta en instancias pequeñas. La enumeración es evidencia
experimental, no un algoritmo para casos grandes.
`validate_dag.py` muestra un contraejemplo reproducible donde la heurística DAG
no alcanza la solución exacta.

## Limitaciones conocidas

- La solución base trabaja con etapas en serie; el modo DAG se usa cuando el
  caso incluye `edges`.
- La solución DAG exacta es exponencial y solo es adecuada para instancias
  pequeñas; la heurística no garantiza optimalidad.
- La auditoría reporta inviabilidad cuando algún riesgo no puede cubrirse.
- La cobertura ponderada exacta también es exponencial; el algoritmo operativo
  para casos grandes es el voraz ponderado.
- Los tiempos dependen del equipo; la evidencia debe conservar la configuración
  usada.
- Los casos oficiales deben agregarse sin incluir información privada fuera del
  repositorio autorizado.
