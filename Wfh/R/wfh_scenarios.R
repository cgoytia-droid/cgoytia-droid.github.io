# =============================================================================
# wfh_scenarios.R  --  Construcción del escenario WFH y cálculo de impactos
# =============================================================================
# Funciones auxiliares para Main.R. No dependen de IGC.CSM; solo manipulan
# la matriz de tiempos y los resultados de solveModel().

# -----------------------------------------------------------------------------
# wfh_commuting_matrix()
# -----------------------------------------------------------------------------
# Traduce el teletrabajo a una reducción del costo efectivo de conmutación.
# Intuición: si se trabaja `week_days` por semana y se teletrabaja `wfh_days`,
# la frecuencia de viaje cae y el tiempo de conmutación EFECTIVO por período
# se escala por (week_days - wfh_days)/week_days.
#
#   t_ij         : matriz NxN de tiempos de viaje (diagonal 0)
#   wfh_days     : días de teletrabajo por semana (0..week_days)
#   week_days    : días laborables por semana (default 5)
#   telework_share : (opcional) vector Nx1 con el share de empleo teletrabajable
#                    en cada DESTINO j. Si se provee, el ahorro de conmutación
#                    es heterogéneo: los destinos con más empleo teletrabajable
#                    reducen más su tiempo efectivo (escala por columna j).
#
# Devuelve una matriz NxN con la diagonal en 0.
wfh_commuting_matrix <- function(t_ij, wfh_days, week_days = 5,
                                 telework_share = NULL) {
  stopifnot(wfh_days >= 0, wfh_days <= week_days)
  N <- nrow(t_ij)

  if (is.null(telework_share)) {
    frac  <- (week_days - wfh_days) / week_days      # escalar uniforme
    t_new <- t_ij * frac
  } else {
    stopifnot(length(telework_share) == N,
              all(telework_share >= 0), all(telework_share <= 1))
    # Factor por destino j: 1 - share_j * (wfh_days/week_days)
    col_factor <- 1 - as.numeric(telework_share) * (wfh_days / week_days)
    t_new <- sweep(t_ij, 2, col_factor, `*`)          # escala cada columna j
  }
  diag(t_new) <- 0
  t_new
}

# -----------------------------------------------------------------------------
# summarise_impacts()
# -----------------------------------------------------------------------------
# Compara el equilibrio baseline (bl) con el contrafáctico WFH (cf), ambos
# salidas de IGC.CSM::solveModel(). Devuelve cambios por localidad y agregados.
#
# Proxy de recaudación local (ABL / impuesto inmobiliario): asume que la base
# imponible es proporcional al VALOR del floorspace construido en cada zona,
# base_i = Q_i * (varphi_i * K_i)  [precio x floorspace desarrollado].
# `varphi` (densidad de desarrollo) es un fundamento recuperado en la inversión
# y se mantiene fijo; el contrafáctico cambia los precios Q. Es un proxy de
# primer orden, transparente, para el resultado de "recaudación local" del paper.
summarise_impacts <- function(bl, cf, K, varphi, tax_rate = 0.01) {
  pct <- function(new, old) 100 * (as.numeric(new) / as.numeric(old) - 1)

  K      <- as.numeric(K)
  varphi <- as.numeric(varphi)
  base_bl <- tax_rate * as.numeric(bl$Q) * varphi * K
  base_cf <- tax_rate * as.numeric(cf$Q) * varphi * K

  by_location <- data.frame(
    location = seq_along(as.numeric(bl$Q)),
    Q_pct    = pct(cf$Q,   bl$Q),      # precio de floorspace
    Li_pct   = pct(cf$L_i, bl$L_i),    # residentes
    Lj_pct   = pct(cf$L_j, bl$L_j),    # trabajadores
    u_pct    = pct(cf$u,   bl$u),      # bienestar por zona
    tax_base_bl = base_bl,
    tax_base_cf = base_cf,
    tax_pct  = pct(base_cf, base_bl)   # base imponible local
  )

  # Bienestar agregado: U puede venir como escalar (agregado) o vector.
  U_bl <- sum(as.numeric(bl$U)); U_cf <- sum(as.numeric(cf$U))
  welfare_pct <- 100 * (U_cf / U_bl - 1)
  tax_pct_agg <- 100 * (sum(base_cf) / sum(base_bl) - 1)

  aggregate <- data.frame(
    variable = c("Precio floorspace (Q)", "Residentes (L_i)",
                 "Trabajadores (L_j)", "Base imponible local"),
    cambio_medio_pct = c(mean(by_location$Q_pct),  mean(by_location$Li_pct),
                         mean(by_location$Lj_pct), mean(by_location$tax_pct)),
    cambio_abs_pct   = c(mean(abs(by_location$Q_pct)),  mean(abs(by_location$Li_pct)),
                         mean(abs(by_location$Lj_pct)), mean(abs(by_location$tax_pct)))
  )

  # Valoración monetaria aproximada del cambio de bienestar (equivalente en
  # ingreso), usando el ingreso medio ybar del baseline si está disponible.
  ybar <- if (!is.null(bl$ybar)) mean(as.numeric(bl$ybar)) else NA_real_
  welfare_money <- if (!is.na(ybar)) ybar * welfare_pct / 100 else NA_real_

  list(
    by_location   = by_location,
    aggregate     = aggregate,
    welfare_pct   = welfare_pct,
    welfare_money = welfare_money,   # ingreso equivalente por residente (aprox.)
    tax_pct       = tax_pct_agg
  )
}
