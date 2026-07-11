# WFH — Spatial models (Goytia & Sanguinetti)

Código en **R** para estimar modelos de econometría espacial sobre los datos del
proyecto *"The Impact of Post-COVID Trends in Work from Home on Land Use,
Property Prices, and Local Tax Revenues in the Buenos Aires Metropolitan
Region"* (Lincoln Institute of Land Policy).

El pipeline sigue el flujo estándar (Anselin; LeSage & Pace): OLS → tests de
autocorrelación → elección de especificación → estimación de SAR / SEM / SDM /
SLX / SAC → **efectos directos, indirectos y totales** → comparación de modelos.

---

## Estructura

```
Wfh/
├── R/
│   ├── _config.R              <- EDITÁ SOLO ESTO (rutas y nombres de columnas)
│   ├── 00_setup.R             <- instala/carga paquetes
│   ├── 01_data_and_weights.R  <- carga datos y construye la matriz W
│   ├── 02_cross_section_models.R  <- OLS, Moran, LM tests, SAR/SEM/SDM/SLX/SAC, impactos
│   ├── 03_spatial_panel.R     <- panel espacial pre/post-COVID (opcional, splm)
│   └── run_all.R              <- corre todo de punta a punta
├── data/                      <- poné acá tu shapefile/CSV (no se versiona)
└── output/                    <- tablas y objetos estimados (no se versiona)
```

## Cómo correrlo

### 1. Prueba sin datos (out-of-the-box)
Con `CFG$USE_SIMULATED = TRUE` (valor por defecto) el pipeline genera una grilla
sintética con dependencia espacial real y corre todos los modelos. Sirve para
verificar que R y los paquetes están OK:

```r
setwd("Wfh")          # o abrí el proyecto en RStudio
source("R/run_all.R")
```

### 2. Con tus datos reales
Abrí `R/_config.R` y:

1. Poné `USE_SIMULATED = FALSE`.
2. Apuntá `geom_path` a tu shapefile / GeoPackage de unidades (partidos, radios
   censales, fracciones…) con una columna de ID única (`id_col`).
3. Si los atributos están en una tabla aparte, completá `attr_path`; si ya vienen
   dentro del shapefile, dejalo en `NULL`.
4. Mapeá tus nombres de columnas en `y`, `wfh` y `controls`.
5. Elegí el tipo de matriz de pesos (`weights_type`: `queen`, `rook`, `knn`, `dist`).
6. Volvé a correr `source("R/run_all.R")`.

Para el diseño **panel pre/post-COVID**, poné `is_panel = TRUE` y completá
`time_col`; se activa `03_spatial_panel.R` (efectos fijos de unidad con `splm`).

## Qué modelos estima

| Modelo | Estructura | Cuándo |
|--------|-----------|--------|
| OLS    | `y = Xβ + e`                         | referencia |
| SLX    | `y = Xβ + WXθ + e`                   | spillovers solo en covariables |
| SAR    | `y = ρWy + Xβ + e`                   | rezago de la dependiente (difusión de precios) |
| SEM    | `y = Xβ + u, u = λWu + e`            | shocks no observados espacialmente correlacionados |
| SDM    | `y = ρWy + Xβ + WXθ + e`             | anida SAR y SLX; suele ser el más general recomendado |
| SAC    | `y = ρWy + Xβ + u, u = λWu + e`      | rezago **y** error espacial |

La elección se guía por los tests LM/RS y por AIC + LR tests (todo se imprime en
consola y se guarda en `output/`).

> **Impactos (clave para interpretar el WFH):** en los modelos con `ρWy` el
> coeficiente del WFH **no** es el efecto marginal. `02_cross_section_models.R`
> reporta el efecto **directo** (sobre la propia unidad), **indirecto**
> (spillover a las vecinas) y **total**.

## Requisitos

R (≥ 4.1) con: `sf`, `spdep`, `spatialreg`, `Matrix`, `dplyr`, `ggplot2`,
`modelsummary` y —para panel— `splm`. `00_setup.R` los instala si faltan.

## Nota sobre "el R de IGC"

Si "el R de IGC" es un script/plantilla existente de tu centro con la
construcción de la matriz `W` o una especificación particular, pasámelo y lo
integro reemplazando `01_data_and_weights.R` o la fórmula de `_config.R`, en vez
de este scaffold genérico.
