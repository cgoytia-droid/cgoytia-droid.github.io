# =============================================================================
# run_all.R  --  Corre todo el pipeline de spatial models de punta a punta
# =============================================================================
# Uso desde la carpeta Wfh/:
#     setwd("Wfh")        # o abrí Wfh.Rproj
#     source("R/run_all.R")
#
# Con CFG$USE_SIMULATED = TRUE corre solo, sin datos reales, para verificar
# que el entorno y los paquetes funcionan.

# Asegura que el working directory sea la carpeta Wfh/ (donde están R/ y output/)
if (basename(getwd()) == "R") setwd("..")

source("R/_config.R")             # 1. configuración (editá este archivo)
source("R/00_setup.R")            # 2. paquetes
source("R/01_data_and_weights.R") # 3. datos + matriz W
source("R/02_cross_section_models.R")  # 4. modelos de corte transversal

# 5. panel espacial (solo si CFG$is_panel == TRUE y splm disponible)
if (isTRUE(CFG$is_panel)) source("R/03_spatial_panel.R")

message("\n>> Pipeline completo. Revisá la carpeta '", CFG$out_dir, "/'.")
