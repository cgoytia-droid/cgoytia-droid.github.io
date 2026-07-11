# =============================================================================
# build_chars.R  --  Ensambla Chars.csv (L_i, L_j, Q, K, wfh_share) por
#                    radio censal (o fracción) desde las fuentes reales de la RMBA
# -----------------------------------------------------------------------------
# Fuentes (cada una en data/; mapeá tus nombres de columna en el bloque CFG):
#   * geojson de radios INDEC        -> geometría, área K, código de zona
#   * población por radio (Censo)    -> L_i (residentes)
#   * precios Argenprop              -> Q  (precio del m2 de floorspace)
#   * empleo (EPH/censo/proxy)       -> L_j (trabajadores por lugar de trabajo)
#   * WFH                            -> wfh_share (share teletrabajable por zona)
#
# NIVEL: siempre lo más desagregado posible. level="radio" (9 dígitos) usa el
# radio censal; level="fraccion" (7 dígitos) agrega a fracción. Las celdas con
# pocos datos (típico en precios) hacen fallback a fracción y luego a partido.
#
# Salida: data/Chars.csv  (+ usar prepare_data.R para la matriz de tiempos).
# =============================================================================

# --- Config: EDITÁ esto con tus archivos y nombres de columna ---------------
CFG <- list(
  level = "radio",                 # "radio" (9 díg.) o "fraccion" (7 díg.)
  out_dir = "data",

  geojson = list(path = "data/greater_buenos_aires_ar.geojson",
                 code = "name"),    # propiedad con el código INDEC del radio

  # Población (Censo por radio). Debe tener el código de radio y la población.
  poblacion = list(path = "data/poblacion_radio.csv",
                   code = "link",   # p.ej. "link" / "cod_2010" (9 díg.)
                   pop  = "personas"),

  # Precios Argenprop. Puntos (lon/lat) con precio, superficie, moneda, operación.
  precios = list(path = "data/argenprop.csv",
                 lon = "lon", lat = "lat",
                 price = "precio", surface = "sup_m2",
                 currency = "moneda",         # valores "USD"/"ARS" (o similar)
                 usd_token = "USD",
                 operation = "operacion", operation_keep = "venta",
                 min_obs = 5),                # mín. listings por celda; sino fallback

  # Empleo (L_j). method:
  #   "file"     -> ya tenés L_j por zona en un archivo (code + workers)
  #   "residents"-> proxy: ocupados por RESIDENCIA (Censo/EPH) [ojo: no es lugar de trabajo]
  #   "proxy"    -> reparte el empleo total del AMBA según un indicador de lugar de trabajo
  empleo = list(method = "file",
                path = "data/empleo_radio.csv",
                code = "link", workers = "L_j",
                proxy_col = NULL),            # columna indicador si method="proxy"

  # WFH: share teletrabajable por zona (destino/lugar de trabajo).
  wfh = list(path = "data/wfh_radio.csv",
             code = "link", share = "wfh_share"),

  dolar_rate = NA_real_,           # $/USD para pasar precios ARS->USD; NA=leer de xlsx
  dolar_xlsx = "data/dolar_blue.xlsx",
  target_crs = 5347                # métrico (POSGAR 2007/Arg 5) para áreas y joins
)

for (p in c("sf", "dplyr")) if (!requireNamespace(p, quietly = TRUE))
  stop("Falta el paquete '", p, "'. install.packages('", p, "').")
suppressMessages({library(sf); library(dplyr)})

n_digits <- if (CFG$level == "fraccion") 7 else 9
zkey <- function(x) substr(sprintf("%09s", trimws(as.character(x))), 1, n_digits)

# --- 1. Geometría + área (K) por zona ---------------------------------------
message(">> Geometría…")
g <- sf::st_read(CFG$geojson$path, quiet = TRUE)
g$code9 <- sprintf("%09s", trimws(as.character(g[[CFG$geojson$code]])))
g <- g[grepl("^[0-9]{9}$", g$code9), ]
g$zone <- substr(g$code9, 1, n_digits)
g <- sf::st_transform(g, CFG$target_crs)
g$area_km2 <- as.numeric(sf::st_area(g)) / 1e6

zones <- g %>% group_by(zone) %>%
  summarise(K = sum(area_km2, na.rm = TRUE),
            geometry = sf::st_union(geometry), .groups = "drop")
N <- nrow(zones)
message(sprintf("   %d zonas (nivel=%s).", N, CFG$level))

# helper: lee csv y agrega una métrica por zona (suma) según código
load_by_zone <- function(cfg, valuecol, fun = sum) {
  d <- utils::read.csv(cfg$path, stringsAsFactors = FALSE)
  d$zone <- zkey(d[[cfg$code]])
  d %>% group_by(zone) %>%
    summarise(val = fun(.data[[valuecol]], na.rm = TRUE), .groups = "drop")
}

# --- 2. Población -> L_i -----------------------------------------------------
message(">> Población (L_i)…")
pop <- load_by_zone(list(path = CFG$poblacion$path, code = CFG$poblacion$code),
                    CFG$poblacion$pop, sum)
names(pop)[2] <- "L_i"

# --- 3. Precios Argenprop -> Q (con fallback fracción/partido) ---------------
message(">> Precios (Q)…")
rate <- CFG$dolar_rate
if (is.na(rate) && file.exists(CFG$dolar_xlsx) && requireNamespace("readxl", quietly = TRUE)) {
  dx <- tryCatch(readxl::read_excel(CFG$dolar_xlsx), error = function(e) NULL)
  if (!is.null(dx)) {
    num <- suppressWarnings(as.numeric(unlist(dx)))
    rate <- stats::median(num[is.finite(num) & num > 1], na.rm = TRUE)
  }
}
pr <- utils::read.csv(CFG$precios$path, stringsAsFactors = FALSE)
if (!is.null(CFG$precios$operation))
  pr <- pr[pr[[CFG$precios$operation]] == CFG$precios$operation_keep, ]
# precio del m2 en USD
ppm2_usd <- pr[[CFG$precios$price]] / pr[[CFG$precios$surface]]
is_ars <- pr[[CFG$precios$currency]] != CFG$precios$usd_token
if (!is.na(rate)) ppm2_usd[is_ars] <- ppm2_usd[is_ars] / rate
pr$ppm2 <- ppm2_usd
pr <- pr[is.finite(pr$ppm2) & pr$ppm2 > 0, ]

# point-in-polygon: cada listing cae en un radio
pts <- sf::st_as_sf(pr, coords = c(CFG$precios$lon, CFG$precios$lat), crs = 4326)
pts <- sf::st_transform(pts, CFG$target_crs)
pip <- sf::st_join(pts, g[, c("code9", "zone")], join = sf::st_within)
pip <- sf::st_drop_geometry(pip)
pip$frac <- substr(pip$code9, 1, 7); pip$part <- substr(pip$code9, 1, 5)

agg_med <- function(df, key) df %>% group_by(.data[[key]]) %>%
  summarise(q = stats::median(ppm2, na.rm = TRUE), n = dplyr::n(), .groups = "drop")
q_zone <- agg_med(pip, "zone"); q_frac <- agg_med(pip, "frac"); q_part <- agg_med(pip, "part")

# Q por zona con fallback si hay pocas observaciones
Q_tbl <- zones %>% sf::st_drop_geometry() %>% select(zone)
Q_tbl$frac <- substr(Q_tbl$zone, 1, 7); Q_tbl$part <- substr(Q_tbl$zone, 1, 5)
Q_tbl <- Q_tbl %>%
  left_join(q_zone, by = "zone") %>%
  left_join(q_frac, by = "frac", suffix = c("", "_f")) %>%
  left_join(q_part, by = "part", suffix = c("", "_p"))
Q_tbl$Q <- ifelse(!is.na(Q_tbl$n) & Q_tbl$n >= CFG$precios$min_obs, Q_tbl$q,
            ifelse(!is.na(Q_tbl$q_f), Q_tbl$q_f, Q_tbl$q_p))
message(sprintf("   Q: %d/%d zonas con precio directo; resto por fallback.",
                sum(!is.na(Q_tbl$n) & Q_tbl$n >= CFG$precios$min_obs), N))
Q_tbl <- Q_tbl[, c("zone", "Q")]

# --- 4. Empleo -> L_j --------------------------------------------------------
message(">> Empleo (L_j) — método: ", CFG$empleo$method)
Lj <- switch(CFG$empleo$method,
  file = { d <- load_by_zone(list(path = CFG$empleo$path, code = CFG$empleo$code),
                             CFG$empleo$workers, sum); names(d)[2] <- "L_j"; d },
  residents = { d <- load_by_zone(list(path = CFG$empleo$path, code = CFG$empleo$code),
                             CFG$empleo$workers, sum); names(d)[2] <- "L_j"
                warning("method='residents': L_j es empleo por RESIDENCIA, no por ",
                        "lugar de trabajo. Sesga el equilibrio; usar solo como proxy."); d },
  proxy = { stopifnot(!is.null(CFG$empleo$proxy_col))
            d <- load_by_zone(list(path = CFG$empleo$path, code = CFG$empleo$code),
                              CFG$empleo$proxy_col, sum)
            total_emp <- sum(pop$L_i, na.rm = TRUE) * 0.45   # tasa de empleo aprox.
            d$val <- d$val / sum(d$val, na.rm = TRUE) * total_emp
            names(d)[2] <- "L_j"; d },
  stop("empleo$method inválido"))

# --- 5. WFH -> wfh_share -----------------------------------------------------
message(">> WFH (wfh_share)…")
wfh <- NULL
if (!is.null(CFG$wfh$path) && file.exists(CFG$wfh$path)) {
  wfh <- load_by_zone(list(path = CFG$wfh$path, code = CFG$wfh$code),
                      CFG$wfh$share, mean)
  names(wfh)[2] <- "wfh_share"
} else message("   (sin archivo WFH; queda NA — se puede correr WFH uniforme)")

# --- 6. Ensamble final -------------------------------------------------------
chars <- zones %>% sf::st_drop_geometry() %>%
  left_join(pop, by = "zone") %>%
  left_join(Lj, by = "zone") %>%
  left_join(Q_tbl, by = "zone")
if (!is.null(wfh)) chars <- left_join(chars, wfh, by = "zone")
chars <- chars %>% arrange(zone) %>% mutate(location = row_number()) %>%
  relocate(location, zone, K)

# Diagnóstico de completitud (el modelo NO admite NA ni ceros en L_i,L_j,K,Q)
req <- c("L_i", "L_j", "K", "Q")
inc <- sapply(req, function(v) sum(is.na(chars[[v]]) | chars[[v]] == 0))
message("\n>> Celdas incompletas por variable (deben quedar en 0 para correr):")
print(inc)

dir.create(CFG$out_dir, showWarnings = FALSE, recursive = TRUE)
utils::write.csv(chars, file.path(CFG$out_dir, "Chars.csv"), row.names = FALSE)
message("\n>> Escrito ", file.path(CFG$out_dir, "Chars.csv"),
        " (", nrow(chars), " zonas). ",
        "Corré prepare_data.R para la matriz de tiempos y luego Main.R (source_data='real').")
