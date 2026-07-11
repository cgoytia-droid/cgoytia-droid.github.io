# =============================================================================
# 02_cross_section_models.R  --  Modelos espaciales de corte transversal
# =============================================================================
# Flujo estándar de econometría espacial (Anselin / LeSage-Pace):
#   1. OLS de referencia
#   2. Moran's I sobre los residuos (¿hay autocorrelación?)
#   3. Tests LM/RS (err vs lag) para elegir la especificación
#   4. Estimación: SAR, SEM, SDM, SLX, SAC/SARAR
#   5. Impactos directos / indirectos / totales (SAR y SDM)
#   6. Comparación por AIC + LR tests y tabla exportada
#
# Requiere: 00_setup.R, 01_data_and_weights.R corridos.

stopifnot(exists("sdf"), exists("listw"))
dir.create(CFG$out_dir, showWarnings = FALSE, recursive = TRUE)

# Si los datos son panel, para el corte transversal usamos el ÚLTIMO período
# y alineamos las filas al orden de la geometría de referencia.
if (isTRUE(CFG$is_panel)) {
  t_last <- max(sdf[[CFG$time_col]])
  cs <- sdf[sdf[[CFG$time_col]] == t_last, ]
  cs <- cs[match(geom_ref[[CFG$id_col]], cs[[CFG$id_col]]), ]
  message(">> Corte transversal sobre el período ", t_last)
} else {
  cs <- sdf
}

# --- Fórmula:  y ~ wfh + controles ------------------------------------------
rhs  <- paste(c(CFG$wfh, CFG$controls), collapse = " + ")
form <- as.formula(paste(CFG$y, "~", rhs))
message("Especificación: ", deparse(form))

# -----------------------------------------------------------------------------
# 1. OLS de referencia
# -----------------------------------------------------------------------------
ols <- lm(form, data = cs)

# -----------------------------------------------------------------------------
# 2. Moran's I sobre residuos de OLS
# -----------------------------------------------------------------------------
moran_resid <- spdep::lm.morantest(ols, listw, zero.policy = TRUE)
moran_y     <- spdep::moran.test(cs[[CFG$y]], listw, zero.policy = TRUE)

# -----------------------------------------------------------------------------
# 3. Tests de multiplicadores de Lagrange (elección de modelo)
# -----------------------------------------------------------------------------
#   - Si el robusto de 'lag' domina  -> preferí SAR (rezago de la dependiente)
#   - Si el robusto de 'err' domina  -> preferí SEM (autocorrelación del error)
#   - Si ambos significativos        -> probá SDM / SAC
lm_tests <- lm_lm_tests(ols, listw)

# -----------------------------------------------------------------------------
# 4. Estimación de modelos espaciales
# -----------------------------------------------------------------------------
# SAR  (Spatial Autoregressive / lag):     y = rho W y + X b + e
sar <- spatialreg::lagsarlm(form, data = cs, listw = listw, zero.policy = TRUE)

# SEM  (Spatial Error):                     y = X b + u,  u = lambda W u + e
sem <- spatialreg::errorsarlm(form, data = cs, listw = listw, zero.policy = TRUE)

# SDM  (Spatial Durbin):    y = rho W y + X b + W X theta + e
sdm <- spatialreg::lagsarlm(form, data = cs, listw = listw,
                            Durbin = TRUE, zero.policy = TRUE)

# SLX  (Spatially Lagged X): y = X b + W X theta + e   (OLS con rezagos de X)
slx <- spatialreg::lmSLX(form, data = cs, listw = listw, zero.policy = TRUE)

# SAC/SARAR (lag + error):   y = rho W y + X b + u, u = lambda W u + e
sac <- spatialreg::sacsarlm(form, data = cs, listw = listw, zero.policy = TRUE)

# -----------------------------------------------------------------------------
# 5. Impactos directos / indirectos / totales
# -----------------------------------------------------------------------------
# En modelos con rezago de la dependiente, el coeficiente NO es el efecto
# marginal: hay que descomponer en directo (propia unidad), indirecto
# (spillover a vecinos) y total. Clave para leer el efecto del WFH.
set.seed(CFG$seed)
trMat <- spatialreg::trW(Wc, type = "mult")   # trazas de W^k

imp_sar <- summary(spatialreg::impacts(sar, tr = trMat, R = CFG$impacts_sims),
                   zstats = TRUE, short = TRUE)
imp_sdm <- summary(spatialreg::impacts(sdm, tr = trMat, R = CFG$impacts_sims),
                   zstats = TRUE, short = TRUE)

# -----------------------------------------------------------------------------
# 6. Comparación de modelos + exportación
# -----------------------------------------------------------------------------
aic_tbl <- data.frame(
  modelo = c("OLS", "SLX", "SAR", "SEM", "SDM", "SAC"),
  AIC    = c(AIC(ols), AIC(slx), AIC(sar), AIC(sem), AIC(sdm), AIC(sac)),
  logLik = c(as.numeric(logLik(ols)), as.numeric(logLik(slx)),
             as.numeric(logLik(sar)), as.numeric(logLik(sem)),
             as.numeric(logLik(sdm)), as.numeric(logLik(sac)))
)
aic_tbl <- aic_tbl[order(aic_tbl$AIC), ]

# LR test: ¿el SDM se reduce a SAR o a SEM? (test de hipótesis anidadas)
lr_sdm_sar <- spatialreg::LR.Sarlm(sdm, sar)
lr_sdm_sem <- tryCatch(spatialreg::LR.Sarlm(sdm, sem), error = function(e) NULL)

# Tabla comparativa de coeficientes (requiere modelsummary)
models <- list(OLS = ols, SLX = slx, SAR = sar, SEM = sem, SDM = sdm, SAC = sac)
tab_path <- file.path(CFG$out_dir, "tabla_modelos_espaciales.txt")
ok <- tryCatch({
  modelsummary::modelsummary(
    models, output = tab_path,
    stars = TRUE, gof_omit = "IC|Log|Adj|F|RMSE",
    title = "Modelos espaciales — WFH y precios (RMBA)"
  ); TRUE
}, error = function(e) { message("modelsummary falló: ", conditionMessage(e)); FALSE })

# También guardamos objetos y resúmenes crudos para el paper.
saveRDS(models,   file.path(CFG$out_dir, "models.rds"))
write.csv(aic_tbl, file.path(CFG$out_dir, "comparacion_AIC.csv"), row.names = FALSE)

# -----------------------------------------------------------------------------
# 7. Reporte a consola
# -----------------------------------------------------------------------------
cat("\n=========================================================\n")
cat("  RESUMEN — Modelos espaciales de corte transversal\n")
cat("=========================================================\n\n")
cat("Moran's I (residuos OLS):  I =", round(moran_resid$estimate[1], 4),
    " p =", format.pval(moran_resid$p.value), "\n")
cat("Moran's I (variable y):    I =", round(moran_y$estimate[1], 4),
    " p =", format.pval(moran_y$p.value), "\n\n")
print(lm_tests)
cat("\n--- Comparación por AIC (menor es mejor) ---\n"); print(aic_tbl, row.names = FALSE)
cat("\n--- LR test SDM vs SAR ---\n"); print(lr_sdm_sar)
if (!is.null(lr_sdm_sem)) { cat("\n--- LR test SDM vs SEM ---\n"); print(lr_sdm_sem) }
cat("\n--- Impactos SAR (efecto del WFH y controles) ---\n"); print(imp_sar)
cat("\n--- Impactos SDM ---\n"); print(imp_sdm)
if (ok) cat("\nTabla comparativa guardada en:", tab_path, "\n")
cat("Objetos guardados en:", normalizePath(CFG$out_dir), "\n")
