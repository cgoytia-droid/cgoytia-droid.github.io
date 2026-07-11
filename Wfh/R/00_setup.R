# =============================================================================
# 00_setup.R  --  Paquetes y utilidades
# =============================================================================
# Instala (si faltan) y carga los paquetes necesarios. Corré esto una vez.

.pkgs <- c(
  "sf",           # geometrías / lectura de shapefiles
  "spdep",        # vecindades, listw, tests de autocorrelación espacial
  "spatialreg",   # estimación de modelos espaciales (SAR, SEM, SDM, SAC...)
  "Matrix",       # matrices ralas para impacts()
  "dplyr",        # manipulación de datos
  "ggplot2",      # figuras
  "modelsummary"  # tablas de regresión comparativas
)

# splm es opcional (solo para panel espacial). Se intenta cargar aparte.
.pkgs_optional <- c("splm")

install_if_missing <- function(pkgs) {
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing)) {
    message("Instalando: ", paste(missing, collapse = ", "))
    install.packages(missing, repos = "https://cloud.r-project.org")
  }
}

install_if_missing(.pkgs)
invisible(lapply(.pkgs, library, character.only = TRUE))

# Carga opcional de splm (no frena el pipeline si no está)
for (p in .pkgs_optional) {
  if (requireNamespace(p, quietly = TRUE)) library(p, character.only = TRUE)
}

# --- Wrapper compatible: tests de multiplicadores de Lagrange ----------------
# spdep >= 1.3 renombró lm.LMtests() a lm.RStests(). Usamos el que exista.
lm_lm_tests <- function(model, listw) {
  if (exists("lm.RStests", where = asNamespace("spdep"))) {
    spdep::lm.RStests(model, listw,
                      test = c("RSerr", "RSlag", "adjRSerr", "adjRSlag"))
  } else {
    spdep::lm.LMtests(model, listw,
                      test = c("LMerr", "LMlag", "RLMerr", "RLMlag"))
  }
}

message("Setup OK. Paquetes cargados.")
