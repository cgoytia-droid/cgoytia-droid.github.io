# WFH en la RMBA — Modelo de Equilibrio Espacial (IGC.CSM)

Estima el impacto del **Work-from-Home (WFH) post-COVID** sobre precios de
floorspace, uso del suelo (residentes/trabajadores) y **recaudación local** en
la Región Metropolitana de Buenos Aires, usando **"el R de IGC"**: el paquete
[`IGC.CSM`](https://cran.r-project.org/package=IGC.CSM) (International Growth
Centre — *Cities Spatial Model*), que operacionaliza el modelo estructural de
**Quantitative Spatial Equilibrium** de Ahlfeldt, Redding, Sturm & Wolf (2015).

Proyecto: Goytia & Sanguinetti — *Lincoln Institute of Land Policy*.

> **Nota:** este es un modelo **estructural de equilibrio general** (inversión +
> contrafáctico), **no** econometría espacial (SAR/SEM). El scaffold anterior de
> `spdep`/`spatialreg` fue reemplazado por este, que es el que usa el IGC.

---

## Cómo funciona el modelo

1. **`inversionModel()`** — a partir de datos observados por localidad
   (residentes `L_i`, trabajadores `L_j`, precio del floorspace `Q`, área `K`) y
   la matriz de tiempos de viaje `t_ij`, **recupera los fundamentos** de la
   ciudad: productividad (`a`/`A`), amenidades (`b`/`B`), salarios (`w`),
   densidad de desarrollo (`varphi`), precios normalizados (`Q_norm`) y share
   comercial del floorspace (`ttheta`).

2. **`solveModel()`** — con esos fundamentos resuelve el **equilibrio**. En el
   baseline reproduce los datos; cambiando un input computa el **contrafáctico**.

**Mapeo del WFH:** teletrabajar *k* días por semana reduce la frecuencia de
conmutación y por lo tanto el **costo efectivo de viajar** → escalamos la matriz
`t_ij` por `(semana − k)/semana` (ver `R/wfh_scenarios.R`). El modelo reubica
residentes y empleo, y devuelve nuevos precios, salarios y bienestar.

## Estructura

```
Wfh/
├── R/
│   ├── Main.R            <- corre el modelo (inversión + baseline + WFH + impactos)
│   ├── wfh_scenarios.R   <- escenario WFH (matriz de conmutación) + cálculo de impactos
│   ├── prepare_data.R    <- geojson + ingreso + dólar  ->  Chars.csv + matriz de tiempos
│   └── demo/             <- 10 localidades de ejemplo para correr sin datos propios
│       ├── Chars.csv
│       └── MatrixTravelTimes_mins.csv
├── data/                <- tus insumos reales (no se versiona)
└── output/              <- resultados (no se versiona)
```

## Uso

### 1. Probar con el demo (out-of-the-box)
```r
setwd("Wfh")
source("R/Main.R")      # instala IGC.CSM la 1ra vez y corre las 10 localidades demo
```
Imprime el cambio de precios, residentes, trabajadores, bienestar agregado y la
base imponible local bajo el escenario WFH, y guarda todo en `output/`.

### 2. Con los datos reales de la RMBA
```r
setwd("Wfh")
# 2a. Poné los 3 archivos crudos en data/:
#     greater_buenos_aires_ar.geojson, ingreso.csv, dolar_blue.xlsx
source("R/prepare_data.R")   # genera Chars_template.csv + matriz placeholder (agrega a 59 partidos)
# 2b. Completá L_i, L_j, Q en Chars_template.csv -> renombralo Chars.csv
#     Reemplazá la matriz placeholder por tiempos reales -> MatrixTravelTimes_mins.csv
# 2c. En Main.R poné CFG$source_data <- "real"
source("R/Main.R")
```

## Datos: qué hay y qué falta

`prepare_data.R` agrega los **14.954 radios censales** a **~59 partidos/comunas**
(la matriz de tiempos radio×radio sería inviable) y calcula lo que **sí** es
derivable de los archivos subidos:

| Insumo del modelo | Estado | Fuente |
|---|---|---|
| `K` (área) | ✅ calculado | geometría del geojson (`st_area`) |
| `ipcf` (ingreso) | ✅ calculado | `ingreso.csv` (proxy / amenidad) |
| `t_ij` | ⚠️ placeholder por distancia | reemplazar por OSRM/Google/GTFS-AMBA |
| `L_i` (residentes) | ❌ a completar | Censo 2010/2022 por radio |
| `L_j` (trabajadores) | ❌ a completar | empleo / censo económico |
| `Q` (precio del m²) | ❌ a completar | listings inmobiliarios / registro |

El manual del IGC aclara que la limpieza y armado de datos queda del lado del
usuario; `L_i`, `L_j` y `Q` requieren tus fuentes de población, empleo y precios.

## Escenario WFH y resultados

- **Precios (`Q`)** y **uso del suelo (`L_i`, `L_j`)**: salida directa del contrafáctico.
- **Recaudación local**: proxy de base imponible `∝ Q · varphi · K` (valor del
  floorspace desarrollado), comparando baseline vs WFH — el resultado de
  "*local tax revenues*" del paper. La alícuota (`CFG$tax_rate`) solo escala el
  nivel; los % de cambio no dependen de ella.
- **Bienestar**: `%ΔU` agregado, con valoración monetaria aproximada en ingreso
  equivalente (usando `ybar`).

Ajustá el escenario en `Main.R`: `CFG$wfh_days_per_week` (días de teletrabajo).
Para un WFH **heterogéneo por zona**, pasá `telework_share` (share de empleo
teletrabajable por destino) a `wfh_commuting_matrix()`.

## Requisitos y estado de verificación

- R (≥ 4.2) con `IGC.CSM`; para `prepare_data.R`: `sf`, `dplyr`, `readxl`.
- Parámetros estructurales por defecto del paquete (`alpha`, `beta=0.7`,
  `theta=7`, etc.); si tenés estimaciones propias para Buenos Aires, pasalas
  como argumentos a `inversionModel`/`solveModel`.
- **Verificado en este entorno:** los scripts parsean y la lógica de
  `wfh_scenarios.R` pasa sus tests. **No** se pudo ejecutar el modelo completo
  acá porque CRAN está bloqueado por la política de red de la sesión remota;
  corré `source("R/Main.R")` en tu máquina (donde CRAN es accesible) para la
  ejecución end-to-end.

## Referencias
- Paquete: <https://cran.r-project.org/package=IGC.CSM> · Fuente:
  <https://github.com/davidzarruk/IGCities>
- Ahlfeldt, Redding, Sturm & Wolf (2015), *The Economics of Density: Evidence
  from the Berlin Wall*, Econometrica 83(6).
- Delbridge, Gomez Ortis, Tsivanidis & Zarate (2024), *Cities Spatial Model*, IGC.
