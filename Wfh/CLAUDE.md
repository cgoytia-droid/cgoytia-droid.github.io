# Contexto del proyecto WFH — handoff para Claude Code

> Este archivo resume una sesión previa de Claude Code (jul 2026). Leelo entero
> antes de tocar nada: acá está todo lo decidido, lo hecho y lo pendiente.

## Qué es este proyecto

Estimar el impacto del **Work-from-Home post-COVID** sobre precios de
floorspace, uso del suelo y **recaudación local** en la Región Metropolitana de
Buenos Aires (RMBA). Paper de **Cynthia Goytia & Pablo Sanguinetti** para el
*Lincoln Institute of Land Policy*.

Herramienta: **"el R de IGC"** = paquete CRAN [`IGC.CSM`](https://cran.r-project.org/package=IGC.CSM)
(IGC *Cities Spatial Model*), un modelo estructural de **Quantitative Spatial
Equilibrium** (Ahlfeldt, Redding, Sturm & Wolf 2015, *Econometrica*). Fuente:
<https://github.com/davidzarruk/IGCities>.
**OJO:** no es econometría espacial (SAR/SEM) — es inversión de modelo +
contrafáctico de equilibrio general. Un primer intento con `spdep`/`spatialreg`
se descartó por esa razón.

## Cómo funciona el pipeline (ya escrito y testeado)

1. `R/Main.R` — flujo completo:
   `inversionModel(N, L_i, L_j, Q, K, t_ij)` recupera fundamentos
   (productividad `a`, amenidades `b`, salarios `w`, densidad `varphi`,
   `Q_norm`, `ttheta`) → `solveModel(...)` reproduce el baseline →
   se escala `t_ij` por el escenario WFH → `solveModel(...)` da el
   contrafáctico → `summarise_impacts()` arma la tabla de impactos.
   Corre out-of-the-box con `CFG$source_data = "demo"` (10 localidades en
   `R/demo/`). Para datos reales: `CFG$source_data <- "real"`.
2. `R/wfh_scenarios.R` — mapeo WFH: teletrabajar *k* de 5 días escala la matriz
   de tiempos por `(5-k)/5` (`wfh_commuting_matrix()`), uniforme o heterogéneo
   por destino vía `telework_share`. `summarise_impacts()` compara equilibrios;
   proxy de recaudación local: base imponible `∝ Q · varphi · K`.
3. `R/build_chars.R` — ensambla el `Chars.csv` REAL por radio censal (9 dígitos)
   o fracción (7): población→`L_i`, Argenprop point-in-polygon→`Q` (mediana del
   m² en USD, fallback fracción→partido si hay <5 listings, conversión ARS→USD
   con dólar blue), empleo→`L_j` (métodos `file`/`residents`/`proxy`),
   WFH→`wfh_share`. Todo parametrizado por nombres de columna en su `CFG`.
4. `R/prepare_data.R` — del geojson de radios: área `K` (POSGAR 2007, EPSG:5347)
   y matriz de tiempos placeholder por distancia entre centroides (25 km/h).
   Agrega radios a partidos con `AGG_DIGITS`.

Verificado: los 4 scripts parsean; la lógica de `wfh_scenarios.R` pasó tests
unitarios (escalado y cálculo de impactos). **El modelo completo aún no se
ejecutó** — la sesión remota tenía CRAN bloqueado. Primer paso acá:
`install.packages("IGC.CSM")` y `source("R/Main.R")` con el demo.

## Datos: qué hay y qué falta

Ya disponibles (la usuaria los tiene; en la sesión previa se subieron al chat):
- `greater_buenos_aires_ar.geojson` — 14.954 radios censales INDEC (CABA=prov 02,
  PBA=06; campo `name` = código de 9 dígitos; 2 filas malformadas se filtran).
  59 partidos/comunas. CRS84.
- `ingreso.csv` — 13.523 radios, `codigo` (8 dígitos, falta el 0 inicial:
  usar `sprintf("%09d", ...)`), `ipcf_0_2016`.
- `dolar_blue.xlsx` — tipo de cambio para ARS→USD.

Pendientes (la usuaria confirmó que EXISTEN, en Dropbox — "proyecto UBER"):
- **Tiempos de viaje** del proyecto UBER (¿Uber Movement?) → `t_ij` real.
  PREGUNTA ABIERTA: ¿a qué zonificación están (radio/fracción/zonas Uber)?
  Todas las fuentes deben compartir el mismo sistema de zonas.
- **Población por radio** (Censo 2010/2022) → `L_i`.
- **Precios Argenprop** (listings con lat/lon, precio, superficie, moneda,
  operación) → `Q`.
- **Datos de WFH** (share teletrabajable por zona) → `wfh_share`.
- **Empleo por lugar de trabajo** → `L_j`. No existe directo; plan: construirlo
  con EPH macheada a censo u otro proxy (ver métodos en `build_chars.R`).

Decisiones tomadas: nivel de análisis **lo más desagregado posible** (radio;
si no, fracción). La matriz radio×radio de 14.954² es inviable → la
granularidad efectiva la limita el `t_ij` disponible.

## Próximos pasos (en orden)

1. Copiar los archivos de datos de Dropbox a `data/` de esta carpeta.
2. Inspeccionar el archivo de tiempos del proyecto UBER; decidir zonificación.
3. Ajustar los nombres de columna en el `CFG` de `build_chars.R` y correrlo.
4. Construir `L_j` (EPH×censo) — diseñar el matcheo con la usuaria.
5. Armar `MatrixTravelTimes_mins.csv` real (mismo orden de filas que Chars.csv).
6. `Main.R` con `source_data="real"`; calibrar escenario WFH
   (`wfh_days_per_week`, `telework_share` con los datos de WFH).
7. Escenarios alternativos (1–3 días), figuras y tablas para el paper.

## Contexto administrativo

- Repo original: `cgoytia-droid/cgoytia-droid.github.io` (sitio web personal),
  rama `claude/spatial-models-igc-r-dl3q5s`, **PR #4** (draft) con todo esto.
  Si este proyecto ahora vive en Dropbox, esa PR puede mergearse o cerrarse.
- La usuaria es Cynthia Goytia (UTDT, cgoytia@utdt.edu); economía urbana,
  responde en español.
- Parámetros estructurales: defaults del paquete (`alpha=0.7, beta=0.7,
  theta=7, mu=0.3, delta=0.3585, rho=0.9094, lambda=0.01, eta=0.1548,
  epsilon=0.01`). Si hay estimaciones propias para Buenos Aires, pasarlas como
  argumentos a `inversionModel`/`solveModel`.
