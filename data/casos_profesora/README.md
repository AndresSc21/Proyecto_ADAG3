# Casos oficiales

Guardar aquí los archivos JSON entregados por la profesora. No cambiar el código
para adaptarlo a un caso; cada caso debe ejecutarse con:

```powershell
python scripts/run_case.py data/casos_profesora/nombre.json
```

También se pueden ejecutar todos juntos y guardar la evidencia:

```powershell
python scripts/run_cases.py data/casos_profesora --output resultados/casos_profesora.json
```

La carpeta no contiene datos privados. La evidencia reproducible del proyecto
se genera con el caso de ejemplo ubicado en la raíz.

El archivo `entrada_G3_mochila_20_nodos.json` que está en la raíz es un caso de
ejemplo suministrado para probar el algoritmo; no representa datos privados de
la profesora.

Para la evidencia final registrar por caso: salida, tiempo, trazas de DP,
etapas aceleradas, costos, selección de auditoría y verificación de cobertura.
