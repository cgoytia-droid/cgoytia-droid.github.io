# =============================================================================
# _config.R  --  Configuración central del análisis de spatial models (WFH)
# -----------------------------------------------------------------------------
# Proyecto: Impacto del Work-from-Home post-COVID sobre precios, uso del suelo
#           y recaudación local en la Región Metropolitana de Buenos Aires.
#           (Goytia & Sanguinetti — Lincoln Institute of Land Policy)
#
# Editá SOLO este archivo para apuntar el pipeline a tus datos reales.
# El resto de los scripts (01_, 02_, 03_) leen de acá y no deberían tocarse.
# =============================================================================

CFG <- list(

  # ---------------------------------------------------------------------------
  # 1. FUENTE DE DATOS
  # ---------------------------------------------------------------------------
  # Poné USE_SIMULATED = TRUE para correr el pipeline de punta a punta con datos
  # sintéticos (sirve para testear que todo funciona sin tus datos reales).
  # Poné USE_SIMULATED = FALSE y completá las rutas de abajo para usar tus datos.
  USE_SIMULATED = TRUE,

  # Shapefile / GeoPackage con las unidades espaciales (partidos, radios
  # censales, fracciones, etc.). Debe tener una columna de ID única.
  geom_path = "data/rmba_units.gpkg",   # o "data/rmba.shp"
  id_col    = "id",                     # identificador único de cada unidad

  # Tabla de datos (CSV / RDS). Si los atributos ya vienen dentro del shapefile,
  # dejá attr_path = NULL y se usan las columnas del propio geometry.
  attr_path = NULL,                     # p.ej. "data/wfh_panel.csv" o NULL

  # ---------------------------------------------------------------------------
  # 2. MAPEO DE VARIABLES  (nombres tal cual aparecen en TUS datos)
  # ---------------------------------------------------------------------------
  # Variable dependiente principal del corte transversal.
  # Sugerencia: log del precio del m2, cambio de uso del suelo, o recaudación.
  y = "log_price",

  # Regresor de interés: exposición / potencial de WFH de la unidad.
  # (p.ej. share de empleo teletrabajable, o cambio pre/post-COVID en WFH).
  wfh = "wfh_share",

  # Controles (todos deben existir como columnas numéricas).
  controls = c("dist_cbd", "density", "income", "accessibility"),

  # ---------------------------------------------------------------------------
  # 3. DIMENSIÓN PANEL  (opcional — para el diseño pre/post-COVID)
  # ---------------------------------------------------------------------------
  # Si tenés panel (misma unidad observada en varios años), completá:
  is_panel  = FALSE,
  time_col  = "year",                   # columna de tiempo
  # Los scripts de panel usan efectos fijos de unidad por defecto.

  # ---------------------------------------------------------------------------
  # 4. MATRIZ DE PESOS ESPACIALES  W
  # ---------------------------------------------------------------------------
  # Tipo de vecindad:
  #   "queen"  -> contigüidad reina (comparten borde o vértice)
  #   "rook"   -> contigüidad torre (comparten borde)
  #   "knn"    -> k vecinos más cercanos (robusto a polígonos irregulares)
  #   "dist"   -> vecinos dentro de un radio de distancia
  weights_type = "queen",
  knn_k        = 6,        # usado si weights_type == "knn"
  dist_km      = 5,        # usado si weights_type == "dist" (umbral en km)

  # Estandarización de W: "W" (por fila, lo habitual), "B" (binaria), "C".
  weights_style = "W",

  # ---------------------------------------------------------------------------
  # 5. INFERENCIA / SALIDAS
  # ---------------------------------------------------------------------------
  impacts_sims = 1000,     # simulaciones para IC de efectos directos/indirectos
  seed         = 20240711, # reproducibilidad
  out_dir      = "output"  # tablas y figuras van acá
)

# CRS métrico sugerido para la RMBA (POSGAR 2007 / Argentina 5 = EPSG:5347).
# Solo se usa para vecindad por distancia; ajustá si tu shapefile usa otro.
CFG$target_crs <- 5347
