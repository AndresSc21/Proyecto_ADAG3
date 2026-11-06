# Informe técnico — Primera entrega

## 1. Identificación

**Proyecto:** Proyecto_ADAG3 — Ruta: aceleración bajo presupuesto y cobertura de auditoría
**Grupo:** G3
**Integrantes:** Andres Felipe Salazar y Manuel Alejandro Hurtado
**Implementación:** Python 3.10+

## 2. Formalización del problema

### 2.1 Aceleración de la cadena

La entrada contiene `n` etapas en serie, un presupuesto entero `B` y, para cada
etapa `i`, una duración normal `t_i`, un costo `c_i` y una reducción `d_i`.
Se exige `0 <= d_i <= t_i` y `c_i >= 0`.

La salida es un subconjunto `S` de etapas tal que

`sum(c_i, i en S) <= B`

y que minimiza la duración final:

`T_final = sum(t_i) - sum(d_i, i en S)`.

Como `sum(t_i)` es constante, esto equivale a maximizar
`sum(d_i, i en S)` sujeto al presupuesto. Por tanto, es exactamente Mochila
0/1, con peso `c_i` y valor `d_i`.

### 2.2 Cobertura de auditoría

La entrada contiene `n` interacciones candidatas, un universo de `r` categorías
de riesgo y un subconjunto `R_j` para cada interacción `j`. La salida es el
menor conjunto de interacciones cuya unión cubra el universo:

`union(R_j, j en S) = U`.

La implementación base usa el algoritmo voraz que elige, en cada iteración, la
interacción que cubre más riesgos aún no cubiertos. Si no existe una cobertura,
lo informa explícitamente.

## 3. Prueba de NP-dureza

### 3.1 Aceleración: reducción desde Mochila 0/1

Sea una instancia de Mochila 0/1 con objetos `(w_i, v_i)`, capacidad `B` y
objetivo maximizar el valor. Construimos una instancia de aceleración con una
etapa por objeto:

`c_i = w_i`, `d_i = v_i`, y `t_i = v_i` (o cualquier duración al menos `v_i`).

La transformación es polinomial y conserva exactamente la restricción de peso y
la función objetivo. Un subconjunto de objetos de valor al menos `V` corresponde
a un subconjunto de etapas con reducción al menos `V`, y viceversa. Como
Mochila 0/1 es NP-difícil, la decisión de aceleración también lo es.

La programación dinámica entregada es exacta, pero pseudo-polinomial: depende
del valor numérico `B`, no solo de la cantidad de bits usada para representarlo.

### 3.2 Auditoría: reducción desde Cobertura de Vértices

Para cumplir la reducción específica de G3, tomamos una instancia de
Cobertura de Vértices: un grafo `G=(V,E)` y un entero `k`. Construimos una
instancia de auditoría así:

1. Creamos una categoría de riesgo `e` por cada arista `e` de `G`.
2. Creamos una interacción `I_v` por cada vértice `v` de `G`.
3. La interacción `I_v` cubre exactamente las categorías correspondientes a
   las aristas incidentes en `v`.
4. Conservamos el mismo límite `k` sobre el número de interacciones.

Si `C` es una cobertura de vértices de tamaño a lo sumo `k`, entonces las
interacciones `{I_v : v en C}` cubren todas las categorías, porque cada arista
tiene al menos uno de sus extremos en `C`. En sentido contrario, si un conjunto
de a lo sumo `k` interacciones cubre todas las categorías, los vértices
correspondientes forman una cobertura de vértices: cada arista fue cubierta por
al menos uno de sus extremos. La transformación solo enumera vértices, aristas
y adyacencias, así que es polinomial. Por lo tanto, la versión de decisión de
auditoría es NP-difícil; además pertenece a NP porque una selección se verifica
recorriendo las categorías.

La formulación también es una instancia de Set Cover, por lo que se puede
aplicar la garantía del voraz: si `OPT` es el número mínimo de interacciones,
la solución tiene tamaño a lo sumo `H_d OPT`, donde `d` es la máxima cantidad
de riesgos cubierta por una interacción y `H_d <= H_r`.

## 4. Complejidad

### 4.1 Programación dinámica

Definimos `DP[i][b]` como la máxima reducción usando las primeras `i` etapas y
presupuesto disponible `b`.

```
DP[i][b] = DP[i-1][b]                                      si c_i > b
DP[i][b] = max(DP[i-1][b], DP[i-1][b-c_i] + d_i)            si c_i <= b
```

Hay `(n+1)(B+1)` celdas y cada una se calcula en tiempo constante. Por tanto:

- Tiempo: `T(n,B) = O(nB)`.
- Memoria de la tabla y traza: `O(nB)`.
- Reconstrucción de la solución: `O(n)`.

Si `B` se representa en `L` bits, puede ser tan grande como `2^L`; por eso
`O(nB)` no es polinomial en el tamaño binario de la entrada.

### 4.2 Voraz de auditoría

En cada iteración se revisan las interacciones restantes y se calcula su
cobertura marginal. Como puede haber hasta `r` iteraciones, y una comparación
puede inspeccionar hasta `r` categorías:

- Tiempo: `O(n r^2)` en el peor caso.
- Memoria: `O(nr)` si se cuenta la representación explícita de los conjuntos.

Para Set Cover, el algoritmo voraz tiene garantía `H_d`, donde
`H_d = 1 + 1/2 + ... + 1/d <= 1 + ln(d)`. Como `d <= r`, también
`H_d <= H_r`. Por tanto, si `OPT` es el número mínimo de interacciones, la
solución voraz tiene tamaño a lo sumo `H_d OPT`.
La variante ponderada usa la razón costo/cobertura marginal y mantiene la
garantía clásica de Set Cover ponderado bajo los mismos supuestos.

### 4.3 Comparación empírica

Para instancias pequeñas, `audit_optimal_cardinality` enumera todos los
subconjuntos y permite comparar el tamaño del resultado voraz con el óptimo.
El script `scripts/validate_greedy.py` reproduce esta comparación con casos
fijos, sin usar la enumeración como algoritmo para casos grandes.

## 5. Variantes implementadas

La variante ponderada por costo elige la interacción que minimiza:

`costo(interacción) / cantidad de riesgos nuevos cubiertos`.

La combinación simultánea de aceleración y auditoría usa un presupuesto único:
primero calcula la cobertura ponderada de costo mínimo mediante programación
dinámica sobre máscaras de riesgos y luego ejecuta la mochila con el
presupuesto restante. Si `m` es el número de interacciones y `r` el número de
riesgos, la cobertura exacta usa `O(m 2^r)` tiempo y `O(2^r)` memoria. La
mochila restante usa `O(nB')`, donde `B'` es el presupuesto después de auditar.
Esto produce la solución exacta cuando el número de riesgos permite manejar las
máscaras.

Para un DAG, `critical_path_duration` calcula la ruta crítica por orden
topológico en `O(n+m)`. `dag_exact` enumera subconjuntos en
`O(2^n(n+m))`, mientras `dag_greedy` recalcula la ruta crítica y selecciona la
mejor razón reducción/costo entre las etapas críticas disponibles. La
heurística tiene costo `O(n(n+m))` y se reporta junto con la solución exacta
para instancias pequeñas.

## 6. Validación inicial

La carpeta `tests/` contiene pruebas automatizadas para:

- optimalidad y respeto del presupuesto;
- cobertura completa;
- detección de cobertura imposible;
- selección de la variante ponderada.
- presupuesto conjunto de auditoría y aceleración;
- solución exacta y heurística para DAG;
- comparación del voraz con el óptimo por fuerza bruta.

El script `scripts/validate_dag.py` también compara ambas estrategias en un
contraejemplo reproducible: con presupuesto 6 y aristas `S0 -> S2` y
`S1 -> S2`, la solución exacta selecciona `S2` y obtiene duración 6, mientras
la heurística selecciona `S0` y `S1` y obtiene duración 10.

`scripts/benchmark.py` genera seis tamaños (`n = 10, 20, 40, 80, 120, 160`)
con semilla fija y guarda tiempos en CSV. La gráfica final debe elaborarse a
partir de esos datos y contrastarse con `nB`, no solo con `n`, porque esa es la
variable teórica de la programación dinámica.

## 7. Evidencia reproducible

El caso de ejemplo suministrado para el grupo está en
`entrada_G3_mochila_20_nodos.json`. Su ejecución produce:

- 20 etapas y 12 categorías de riesgo;
- presupuesto de aceleración `B = 72`;
- presupuesto conjunto `B = 100`;
- aceleración seleccionada: `E02, E03, E04, E06, E08, E12`;
- costo de aceleración `72`, reducción `55` y duración `446`;
- auditoría voraz de costo `24`, cubriendo las 12 categorías;
- auditoría ponderada de costo `25`, cubriendo las 12 categorías;
- solución conjunta de costo total `100`, reducción `58` y duración `443`;
- solución DAG exacta de duración `446` y heurística DAG de duración `447`.

La tabla legible está en
`resultados/entrada_G3_mochila_20_nodos_resumen.md` y la traza completa de
1.460 estados DP en `resultados/entrada_G3_mochila_20_nodos.json`.

### 7.1 Tabla resumen para la entrega

| Sección | Seleccionados | Costo | Reducción | Duración | Factible |
|---|---|---:|---:|---:|:---:|
| Aceleración | E02, E03, E04, E06, E08, E12 | 72 | 55 | 446 | Sí |
| Auditoría voraz | E18_completa, E19_completa, E20_completa, E01_parcial | 24 | — | — | Sí |
| Auditoría ponderada | E01_parcial, E12_completa, E13_completa, E18_parcial, E11_completa | 25 | — | — | Sí |
| Presupuesto conjunto | Auditoría: E01_parcial, E18_completa, E19_completa, E20_completa; aceleración: E03, E04, E06, E08, E12, E16 | 100 | 58 | 443 | Sí |

El tiempo medido fue aproximadamente `0.012460` segundos y se registraron
1.460 estados de programación dinámica. La traza completa se entrega en el
repositorio porque ocuparía muchas páginas en el informe PDF.

Los datos privados de la profesora no se incluyen en el repositorio. La
profesora puede probarlos con el mismo adaptador, sin modificar la lógica:

1. salida;
2. tiempo;
3. traza de estados y decisiones DP;
4. etapas aceleradas y costo;
5. selección de auditoría y ganancias marginales;
6. verificación de cobertura;
7. resultado de la variante ponderada.

1. salida;
2. tiempo;
3. traza de estados y decisiones DP;
4. etapas aceleradas y costo;
5. selección de auditoría y ganancias marginales;
6. verificación de cobertura;
7. resultado de la variante ponderada.
