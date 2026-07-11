# =============================================================================
# 01_data_and_weights.R  --  Carga de datos y matriz de pesos espaciales W
# =============================================================================
# Deja en el entorno:
#   sdf     : objeto sf con geometría + atributos (una fila por unidad-tiempo)
#   nb      : lista de vecindades (neighbours list)
#   listw   : objeto listw (W estandarizada) para los modelos
#   Wc      : matriz rala CsparseMatrix (para trazas de impacts())
#
# Requiere: haber corrido 00_setup.R y tener CFG (de _config.R).

stopifnot(exists("CFG"))
set.seed(CFG$seed)

# -----------------------------------------------------------------------------
# 1. DATOS
# -----------------------------------------------------------------------------
if (isTRUE(CFG$USE_SIMULATED)) {

  message(">> Usando DATOS SIMULADOS (grilla 15x15). Poné CFG$USE_SIMULATED=FALSE ",
          "en _config.R para usar tus datos.")

  # Grilla regular como proxy de unidades espaciales de la RMBA.
  n_side <- 15
  grd <- sf::st_make_grid(
    sf::st_as_sfc(sf::st_bbox(c(xmin = 0, ymin = 0, xmax = n_side, ymax = n_side))),
    n = c(n_side, n_side)
  )
  sdf <- sf::st_sf(id = seq_along(grd), geometry = grd)

  # Vecindad para generar dependencia espacial real en el DGP.
  nb0    <- spdep::poly2nb(sdf, queen = TRUE)
  listw0 <- spdep::nb2listw(nb0, style = "W")

  N <- nrow(sdf)
  # Regresores
  centroids <- sf::st_coordinates(sf::st_centroid(sf::st_geometry(sdf)))
  dist_cbd  <- as.numeric(sqrt((centroids[,1] - n_side/2)^2 +
                               (centroids[,2] - n_side/2)^2))
  wfh_share     <- pmin(pmax(0.15 + 0.03 * dist_cbd + rnorm(N, 0, 0.05), 0), 1)
  density       <- exp(-0.15 * dist_cbd) + rnorm(N, 0, 0.05)
  income        <- 10 - 0.2 * dist_cbd + rnorm(N, 0, 0.5)
  accessibility <- exp(-0.10 * dist_cbd) + rnorm(N, 0, 0.03)

  # DGP tipo SAR:  y = rho*W*y + X*beta + eps
  X <- cbind(1, wfh_share, dist_cbd, density, income, accessibility)
  beta <- c(3.0, 1.2, -0.05, 0.4, 0.15, 0.6)   # efecto WFH positivo (+1.2)
  rho  <- 0.45
  eps  <- rnorm(N, 0, 0.3)
  Wmat <- as(listw0, "CsparseMatrix")
  A    <- Matrix::Diagonal(N) - rho * Wmat
  log_price <- as.numeric(Matrix::solve(A, X %*% beta + eps))

  sdf$log_price     <- log_price
  sdf$wfh_share     <- wfh_share
  sdf$dist_cbd      <- dist_cbd
  sdf$density       <- density
  sdf$income        <- income
  sdf$accessibility <- accessibility

  # Panel sintético opcional (pre/post-COVID) si CFG$is_panel == TRUE.
  if (isTRUE(CFG$is_panel)) {
    pre  <- sdf; pre$year  <- 2019; pre$wfh_share  <- 0.05 + 0.005 * dist_cbd
    post <- sdf; post$year <- 2022
    # El shock de WFH sube más lejos del CBD y empuja precios en esos lugares.
    post$log_price <- post$log_price + 0.8 * (post$wfh_share - pre$wfh_share)
    sdf <- rbind(pre, post)
  }

} else {

  message(">> Cargando datos reales desde: ", CFG$geom_path)
  sdf <- sf::st_read(CFG$geom_path, quiet = TRUE)

  if (!is.null(CFG$attr_path)) {
    attr_tbl <- if (grepl("\\.rds$", CFG$attr_path, ignore.case = TRUE)) {
      readRDS(CFG$attr_path)
    } else {
      utils::read.csv(CFG$attr_path, stringsAsFactors = FALSE)
    }
    sdf <- dplyr::left_join(sdf, attr_tbl, by = CFG$id_col)
  }

  # Reproyección a CRS métrico (necesario para vecindad por distancia).
  if (!is.na(sf::st_crs(sdf)$epsg) || !is.null(CFG$target_crs)) {
    sdf <- sf::st_transform(sdf, CFG$target_crs)
  }
}

# -----------------------------------------------------------------------------
# 2. CHEQUEO DE COLUMNAS REQUERIDAS
# -----------------------------------------------------------------------------
needed <- c(CFG$y, CFG$wfh, CFG$controls, if (CFG$is_panel) CFG$time_col)
missing_cols <- setdiff(needed, names(sdf))
if (length(missing_cols)) {
  stop("Faltan columnas en los datos (revisá _config.R): ",
       paste(missing_cols, collapse = ", "))
}

# -----------------------------------------------------------------------------
# 3. MATRIZ DE PESOS ESPACIALES  W
# -----------------------------------------------------------------------------
# Para panel, la W se construye sobre las unidades de UN período (la geometría
# no cambia en el tiempo). Tomamos el primer período como referencia.
if (isTRUE(CFG$is_panel)) {
  t0        <- sort(unique(sdf[[CFG$time_col]]))[1]
  geom_ref  <- sdf[sdf[[CFG$time_col]] == t0, ]
} else {
  geom_ref  <- sdf
}

build_nb <- function(g, type, k, dist_km) {
  switch(type,
    queen = spdep::poly2nb(g, queen = TRUE),
    rook  = spdep::poly2nb(g, queen = FALSE),
    knn   = {
      coords <- sf::st_coordinates(sf::st_centroid(sf::st_geometry(g)))
      spdep::knn2nb(spdep::knearneigh(coords, k = k))
    },
    dist  = {
      coords <- sf::st_coordinates(sf::st_centroid(sf::st_geometry(g)))
      spdep::dnearneigh(coords, 0, dist_km * 1000)  # metros
    },
    stop("weights_type inválido: ", type)
  )
}

nb <- build_nb(geom_ref, CFG$weights_type, CFG$knn_k, CFG$dist_km)

# Aviso si hay unidades sin vecinos (islas): rompen algunos estimadores.
n_islas <- sum(spdep::card(nb) == 0)
if (n_islas > 0) {
  warning(n_islas, " unidad(es) sin vecinos. Considerá 'knn' o subir dist_km. ",
          "Se permite zero.policy=TRUE, pero revisá el diseño.")
}

listw <- spdep::nb2listw(nb, style = CFG$weights_style, zero.policy = TRUE)

# Matriz rala para impacts() (trazas de potencias de W).
Wc <- as(listw, "CsparseMatrix")

message(sprintf("Datos: %d observaciones | W: tipo '%s', %d unidades, %.1f vecinos prom.",
                nrow(sdf), CFG$weights_type, length(nb),
                mean(spdep::card(nb))))
