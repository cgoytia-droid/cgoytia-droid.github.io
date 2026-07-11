# =============================================================================
# prepare_data.R  --  De los datos crudos de la RMBA a los insumos del modelo
# =============================================================================
# Convierte:
#   - greater_buenos_aires_ar.geojson  (radios censales INDEC, geometría)
#   - ingreso.csv                      (ipcf 2016 por radio)
#   - dolar_blue.xlsx                  (tipo de cambio, para pasar $AR -> USD)
# en los DOS archivos que pide IGC.CSM:
#   - data/Chars.csv                   (L_i, L_j, K, Q por localidad)
#   - data/MatrixTravelTimes_mins.csv  (matriz NxN de tiempos)
#
# La matriz de tiempos de 14.954 radios sería inviable (~2.2e8 celdas), así que
# AGREGAMOS a los ~59 partidos/comunas (primeros 5 dígitos del código INDEC).
# Cambiá AGG_DIGITS si querés otra granularidad (7 = fracción censal).
#
# IMPORTANTE — lo que estos archivos NO contienen y tenés que sumar vos:
#   * L_i (residentes)  -> Censo 2010/2022 por radio.
#   * L_j (trabajadores)-> Censo económico / registros de empleo por zona.
#   * Q  (precio del m2 de floorspace) -> listings inmobiliarios / registro.
#   * t_ij real -> tiempos de viaje puerta a puerta (Google/OSRM/GTFS-AMBA).
# Acá K (área) y la matriz placeholder por distancia SÍ se calculan de verdad;
# L_i, L_j y Q se dejan como columnas a completar (NA) con instrucciones.
# =============================================================================

# --- Configuración -----------------------------------------------------------
IN <- list(
  geojson = "data/greater_buenos_aires_ar.geojson",
  ingreso = "data/ingreso.csv",
  dolar   = "data/dolar_blue.xlsx"
)
AGG_DIGITS  <- 5        # 5 = partido/comuna ; 7 = fracción censal
TARGET_CRS  <- 5347     # POSGAR 2007 / Arg 5 (métrico) para calcular áreas
SPEED_KMH   <- 25       # velocidad supuesta para la matriz placeholder de tiempos
OUT_DIR     <- "data"

for (p in c("sf", "dplyr")) if (!requireNamespace(p, quietly = TRUE))
  stop("Falta el paquete '", p, "'. Instalá con install.packages('", p, "').")
library(sf); library(dplyr)

# --- 1. Geometría + área (K) -------------------------------------------------
message(">> Leyendo geojson…")
g <- sf::st_read(IN$geojson, quiet = TRUE)

# El código INDEC del radio está en 'name'. Descartamos filas malformadas.
g$code <- sprintf("%09s", trimws(as.character(g$name)))
g <- g[grepl("^[0-9]{9}$", g$code), ]
g$zone <- substr(g$code, 1, AGG_DIGITS)

g <- sf::st_transform(g, TARGET_CRS)
g$area_km2 <- as.numeric(sf::st_area(g)) / 1e6

# --- 2. Ingreso por radio -> por zona ---------------------------------------
message(">> Leyendo ingreso.csv…")
inc <- utils::read.csv(IN$ingreso, stringsAsFactors = FALSE)
inc$code <- sprintf("%09d", as.integer(inc$codigo))   # completa el 0 inicial
inc$zone <- substr(inc$code, 1, AGG_DIGITS)
inc_zone <- inc %>%
  dplyr::group_by(zone) %>%
  dplyr::summarise(ipcf_mean = mean(ipcf_0_2016, na.rm = TRUE), .groups = "drop")

# --- 3. Tipo de cambio (para reportar en USD, opcional) ---------------------
usd_rate <- NA_real_
if (file.exists(IN$dolar) && requireNamespace("readxl", quietly = TRUE)) {
  dx <- tryCatch(readxl::read_excel(IN$dolar), error = function(e) NULL)
  if (!is.null(dx)) {
    num <- suppressWarnings(as.numeric(unlist(dx)))
    usd_rate <- stats::median(num[is.finite(num) & num > 1], na.rm = TRUE)
    message(sprintf(">> Tipo de cambio (mediana dolar_blue): %.1f $/USD", usd_rate))
  }
}

# --- 4. Agregación a zonas ---------------------------------------------------
zones <- g %>%
  dplyr::group_by(zone) %>%
  dplyr::summarise(K = sum(area_km2, na.rm = TRUE),
                   geometry = sf::st_union(geometry), .groups = "drop") %>%
  dplyr::left_join(inc_zone, by = "zone") %>%
  dplyr::arrange(zone)

N <- nrow(zones)
message(sprintf(">> %d zonas de agregación (AGG_DIGITS=%d).", N, AGG_DIGITS))

# --- 5. Chars.csv (template) -------------------------------------------------
# K e ingreso calculados; L_i, L_j, Q a completar con datos reales.
chars <- data.frame(
  location = seq_len(N),
  zone     = zones$zone,
  K        = round(zones$K, 4),
  ipcf     = round(zones$ipcf_mean, 1),  # ingreso per cápita (proxy / amenidad)
  L_i      = NA_real_,                   # <-- residentes (Censo)
  L_j      = NA_real_,                   # <-- trabajadores (empleo)
  Q        = NA_real_                    # <-- precio del m2 (listings/registro)
)

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
utils::write.csv(chars, file.path(OUT_DIR, "Chars_template.csv"), row.names = FALSE)

# --- 6. Matriz de tiempos placeholder (por distancia entre centroides) -------
# Stand-in hasta tener tiempos reales. Distancia geodésica / velocidad supuesta.
cent   <- sf::st_transform(sf::st_centroid(zones), 4326)
coords <- sf::st_coordinates(cent)
dmat   <- as.matrix(sf::st_distance(cent)) / 1000        # km
tmat   <- round(dmat / SPEED_KMH * 60, 2)                 # minutos
diag(tmat) <- 0                                           # el modelo pide diag 0

# Sin encabezado ni nombres de fila: matriz "cruda" como espera Main.R / el manual.
utils::write.table(tmat,
                   file.path(OUT_DIR, "MatrixTravelTimes_mins_placeholder.csv"),
                   sep = ",", row.names = FALSE, col.names = FALSE)

# --- 7. Instrucciones finales ------------------------------------------------
cat("\n=========================================================\n")
cat("  Insumos RMBA generados en '", OUT_DIR, "/'\n", sep = "")
cat("=========================================================\n")
cat("  - Chars_template.csv                     (K e ingreso listos; faltan L_i, L_j, Q)\n")
cat("  - MatrixTravelTimes_mins_placeholder.csv (tiempos aprox. por distancia)\n\n")
cat("PASOS PARA CORRER EL MODELO CON DATOS REALES:\n")
cat("  1. Completá L_i, L_j y Q en Chars_template.csv y renombralo Chars.csv\n")
cat("     (sin NA ni ceros; mismo orden de filas que la matriz).\n")
cat("  2. Reemplazá la matriz placeholder por tiempos reales (OSRM/Google/GTFS)\n")
cat("     y guardala como MatrixTravelTimes_mins.csv (sin encabezado).\n")
cat("  3. En Main.R poné CFG$source_data <- 'real' y corré source('R/Main.R').\n")
if (!is.na(usd_rate))
  cat(sprintf("\n  (Tipo de cambio disponible para reportes en USD: %.1f $/USD)\n", usd_rate))
