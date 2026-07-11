# data/ — insumos de la RMBA (no versionado)

Poné acá los archivos crudos para `R/prepare_data.R`:

- `greater_buenos_aires_ar.geojson` — radios censales (geometría INDEC).
- `ingreso.csv` — ipcf 2016 por radio (`codigo`, `ipcf_0_2016`, …).
- `dolar_blue.xlsx` — tipo de cambio (para reportar en USD).

`prepare_data.R` genera acá `Chars_template.csv` y
`MatrixTravelTimes_mins_placeholder.csv`. Completá `L_i`, `L_j`, `Q` y los
tiempos de viaje reales, renombralos a `Chars.csv` y
`MatrixTravelTimes_mins.csv`, y poné `CFG$source_data <- "real"` en `Main.R`.

El contenido de esta carpeta no se versiona (ver `.gitignore`), salvo este README.
