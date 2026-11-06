# Resumen del caso G3

- Tiempo de ejecución: `0.012460` segundos
- Estados DP registrados: `1460`

| Sección | Seleccionados | Costo | Reducción | Duración | Factible |
|---|---|---:|---:|---:|:---:|
| Aceleracion | E02, E03, E04, E06, E08, E12 | 72 | 55 | 446 | True |
| Auditoria voraz | E18_completa, E19_completa, E20_completa, E01_parcial | 24 | N/A | N/A | True |
| Auditoria ponderada | E01_parcial, E12_completa, E13_completa, E18_parcial, E11_completa | 25 | N/A | N/A | True |
| Presupuesto conjunto | Auditoria: E01_parcial, E18_completa, E19_completa, E20_completa \| Aceleracion: E03, E04, E06, E08, E12, E16 | 100 | 58 | 443 | True |

La tabla resume el resultado; la traza completa de cada estado DP está en el archivo JSON original.
