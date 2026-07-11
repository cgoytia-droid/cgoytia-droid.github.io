# =============================================================================
# Main.R  --  Modelo de Equilibrio Espacial (QSE) aplicado al WFH en la RMBA
# -----------------------------------------------------------------------------
# Usa el paquete IGC.CSM (International Growth Centre — Cities Spatial Model),
# que operacionaliza el modelo estructural de Ahlfeldt, Redding, Sturm & Wolf
# (2015). Flujo del paquete:
#
#   1. inversionModel() : dado L_i, L_j, Q, K y la matriz de tiempos t_ij,
#      recupera los FUNDAMENTOS de la ciudad: productividad (a/A),
#      amenidades (b/B), salarios (w), densidad de desarrollo (varphi),
#      precios normalizados (Q_norm) y share comercial del floorspace (ttheta).
#
#   2. solveModel()     : dados esos fundamentos, resuelve el EQUILIBRIO.
#      En el baseline reproduce los datos; cambiando un input (acá: los
#      tiempos de viaje t_ij) computa el CONTRAFÁCTICO de política.
#
# Mapeo del WFH -> teletrabajar N días por semana reduce la frecuencia de
# conmutación, es decir baja el COSTO EFECTIVO de viajar. Lo modelamos como
# una reducción de la matriz de tiempos t_ij (ver wfh_scenarios.R). El modelo
# reubica residentes/empleo, y devuelve precios de floorspace, salarios y
# bienestar -> los tres resultados centrales del paper (precios, uso del
# suelo, recaudación local vía valor del floorspace).
#
# Proyecto: Goytia & Sanguinetti — Lincoln Institute of Land Policy.
# Paquete:  https://cran.r-project.org/package=IGC.CSM
# =============================================================================

# --- 0. Entorno --------------------------------------------------------------
rm(list = ls())
if (basename(getwd()) == "R") setwd("..")   # pararse en la carpeta Wfh/
source("R/wfh_scenarios.R")                  # helpers de escenarios e impactos

# --- 1. Paquete IGC.CSM ------------------------------------------------------
# La PRIMERA vez descomentá install.packages(); después alcanza con library().
if (!requireNamespace("IGC.CSM", quietly = TRUE)) {
  install.packages("IGC.CSM", repos = "https://cloud.r-project.org")
}
library(IGC.CSM)

# --- 2. Configuración --------------------------------------------------------
CFG <- list(
  # "demo"  -> corre con las 10 localidades de ejemplo (R/demo/), sin datos propios.
  # "real"  -> usa tus insumos en data/ generados por prepare_data.R.
  source_data = "demo",

  # Escenario WFH: días de teletrabajo por semana (de 5 laborables).
  wfh_days_per_week  = 2,          # p.ej. 2 días WFH -> 3 días de conmutación
  work_days_per_week = 5,

  # Alícuota de referencia para el proxy de recaudación local (ABL / inmobiliario)
  # sobre el valor del floorspace. Solo escala el nivel; los % de cambio no dependen de esto.
  tax_rate = 0.01,

  out_dir = "output"
)

paths <- if (CFG$source_data == "demo") {
  list(chars = "R/demo/Chars.csv", tmat = "R/demo/MatrixTravelTimes_mins.csv")
} else {
  list(chars = "data/Chars.csv",   tmat = "data/MatrixTravelTimes_mins.csv")
}

# --- 3. Carga de datos -------------------------------------------------------
chars <- utils::read.csv(paths$chars, stringsAsFactors = FALSE)
t_ij  <- as.matrix(utils::read.csv(paths$tmat, header = FALSE))
dimnames(t_ij) <- NULL

req <- c("L_i", "L_j", "K", "Q")
if (!all(req %in% names(chars)))
  stop("Chars.csv debe tener columnas: ", paste(req, collapse = ", "))

N   <- nrow(chars)
L_i <- as.matrix(chars$L_i)
L_j <- as.matrix(chars$L_j)
K   <- as.matrix(chars$K)
Q   <- as.matrix(chars$Q)

# Chequeos que exige el modelo (nada nulo/faltante; matriz cuadrada; diagonal 0).
stopifnot(nrow(t_ij) == N, ncol(t_ij) == N)
if (any(is.na(chars[req])) || any(sapply(chars[req], function(x) any(x == 0))))
  stop("L_i, L_j, K, Q no pueden tener NA ni ceros. Revisá tus datos.")
if (any(diag(t_ij) != 0)) warning("La diagonal de t_ij deberia ser 0 (viaje a si mismo).")

message(sprintf(">> %d localidades | fuente: %s | WFH: %d/%d dias",
                N, CFG$source_data, CFG$wfh_days_per_week, CFG$work_days_per_week))

# --- 4. Inversión del modelo (baseline) --------------------------------------
# Recupera los fundamentos de la ciudad a partir de los datos observados.
inv <- IGC.CSM::inversionModel(N = N, L_i = L_i, L_j = L_j, Q = Q, K = K, t_ij = t_ij)

# --- 5. Equilibrio baseline (debe reproducir los datos) ----------------------
bl <- IGC.CSM::solveModel(
  N = N, L_i = L_i, L_j = L_j, K = K, t_ij = t_ij,
  a = inv$a, b = inv$b, varphi = inv$varphi,
  w_eq = inv$w, u_eq = inv$u, Q_eq = inv$Q_norm, ttheta_eq = inv$ttheta
)

# --- 6. Contrafáctico WFH ----------------------------------------------------
# Menos días de conmutación -> menor costo efectivo de viaje -> t_ij escalada.
t_ij_wfh <- wfh_commuting_matrix(
  t_ij,
  wfh_days  = CFG$wfh_days_per_week,
  week_days = CFG$work_days_per_week
  # telework_share = chars$wfh_share   # (opcional) share teletrabajable por destino
)

cf <- IGC.CSM::solveModel(
  N = N, L_i = L_i, L_j = L_j, K = K, t_ij = t_ij_wfh,
  a = inv$a, b = inv$b, varphi = inv$varphi,
  w_eq = inv$w, u_eq = inv$u, Q_eq = inv$Q_norm, ttheta_eq = inv$ttheta
)

# --- 7. Impactos (baseline vs WFH) -------------------------------------------
impact <- summarise_impacts(bl, cf, K = K, varphi = inv$varphi,
                            tax_rate = CFG$tax_rate)

dir.create(CFG$out_dir, showWarnings = FALSE, recursive = TRUE)
utils::write.csv(impact$by_location,
                 file.path(CFG$out_dir, "wfh_impacts_by_location.csv"),
                 row.names = FALSE)
saveRDS(list(inversion = inv, baseline = bl, counterfactual = cf, impact = impact),
        file.path(CFG$out_dir, "wfh_model_objects.rds"))

# --- 8. Reporte a consola ----------------------------------------------------
cat("\n=========================================================\n")
cat("  WFH en la RMBA — Modelo de Equilibrio Espacial (IGC.CSM)\n")
cat("  Escenario:", CFG$wfh_days_per_week, "de", CFG$work_days_per_week,
    "dias de teletrabajo\n")
cat("=========================================================\n\n")
agg <- impact$aggregate
agg[sapply(agg, is.numeric)] <- lapply(agg[sapply(agg, is.numeric)], round, 4)
print(agg, row.names = FALSE)
cat("\nCambio de bienestar agregado (%):     ", round(impact$welfare_pct, 3), "%\n")
cat("Cambio en base imponible local (%):    ", round(impact$tax_pct, 3), "%\n")
cat("\nTop 5 zonas por suba de precios (Q):\n")
print(utils::head(
  impact$by_location[order(-impact$by_location$Q_pct),
                     c("location", "Q_pct", "Li_pct", "Lj_pct", "tax_pct")], 5))
cat("\nResultados guardados en:", normalizePath(CFG$out_dir), "\n")
