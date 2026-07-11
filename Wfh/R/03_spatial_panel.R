# =============================================================================
# 03_spatial_panel.R  --  Panel espacial pre/post-COVID (opcional)
# =============================================================================
# Explota el diseño natural del paper: la misma unidad observada antes (2019)
# y después (2022) del shock de WFH. Con efectos fijos de unidad, el WFH
# identifica el cambio dentro de cada unidad.
#
# Requiere el paquete 'splm'. Si no está instalado, este script avisa y sale.
# Requiere: CFG$is_panel == TRUE y datos con CFG$time_col.

stopifnot(exists("sdf"), exists("listw"))

if (!requireNamespace("splm", quietly = TRUE)) {
  message(">> 'splm' no está instalado; salteo el panel espacial. ",
          "Instalá con install.packages('splm') si querés correrlo.")
} else if (!isTRUE(CFG$is_panel)) {
  message(">> CFG$is_panel es FALSE; no hay dimensión temporal. Salteo panel.")
} else {

  library(splm)

  # splm espera un data.frame ordenado por (unidad, tiempo) SIN geometría,
  # y una listw cuyas unidades coincidan con las del panel.
  pdat <- sf::st_drop_geometry(sdf)
  pdat <- pdat[order(pdat[[CFG$id_col]], pdat[[CFG$time_col]]), ]

  rhs  <- paste(c(CFG$wfh, CFG$controls), collapse = " + ")
  form <- as.formula(paste(CFG$y, "~", rhs))

  # SAR panel con efectos fijos de unidad (within).
  sar_fe <- splm::spml(form, data = pdat, listw = listw,
                       model = "within", effect = "individual",
                       lag = TRUE, spatial.error = "none")

  # SEM panel con efectos fijos de unidad.
  sem_fe <- splm::spml(form, data = pdat, listw = listw,
                       model = "within", effect = "individual",
                       lag = FALSE, spatial.error = "b")

  # Test de Hausman espacial: efectos fijos vs. aleatorios.
  re_lag <- tryCatch(
    splm::spml(form, data = pdat, listw = listw,
               model = "random", lag = TRUE, spatial.error = "none"),
    error = function(e) NULL)
  hausman <- if (!is.null(re_lag)) {
    tryCatch(splm::sphtest(sar_fe, re_lag), error = function(e) NULL)
  } else NULL

  dir.create(CFG$out_dir, showWarnings = FALSE, recursive = TRUE)
  saveRDS(list(sar_fe = sar_fe, sem_fe = sem_fe, hausman = hausman),
          file.path(CFG$out_dir, "panel_models.rds"))

  cat("\n=========================================================\n")
  cat("  RESUMEN — Panel espacial (efectos fijos de unidad)\n")
  cat("=========================================================\n\n")
  cat("--- SAR panel (lag) ---\n");   print(summary(sar_fe))
  cat("\n--- SEM panel (error) ---\n"); print(summary(sem_fe))
  if (!is.null(hausman)) { cat("\n--- Hausman espacial (FE vs RE) ---\n"); print(hausman) }
  cat("\nObjetos guardados en:", normalizePath(CFG$out_dir), "\n")
}
