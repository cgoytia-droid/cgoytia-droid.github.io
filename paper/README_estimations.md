# LVC Climate Adaptation Paper — Revised estimations (real data)

This note documents how the revenue estimations in **Section 7** of
`LVC_Climate_Adaptation_Paper_revised_estimations.docx` were rebuilt from the
real Luján de Cuyo project data held in Google Drive, replacing the original
qualitative "Low / Moderate / High" placeholders.

## What changed in the paper

- **Section 7** fully rewritten (7.1 Methodology & data sources, 7.2 Realized
  revenue, 7.3 Ex-ante value-capture potential, 7.4 Financing gap & leverage).
- **Table 3** replaced: was a qualitative trajectory; now the *realized* revenue
  series (FX-adjusted USD).
- **Table 4** added: ex-ante value-capture potential by instrument and scenario,
  plus combined annual total.
- **Population corrected** throughout: ~140,000 → **~175,000** (2022 census,
  +46% inter-censal), consistent with the project's instrument report.
- **Abstract & §3.3 methodology**: now state honestly that two instruments are
  *operational with realized revenue* while the value-capture instruments are
  *designed and estimated ex ante* from real works-programme and land-value data.
- **§6.1**: notes the index is operationalised as the *Índice de Ciudad Deseada*.

## Data sources (Google Drive)

| Source | What it provided |
| --- | --- |
| `LdC_LBF_Revenue_Model` (Sheet) | Realized water/sewer series; FX/CPI; vacant-land padrón aggregates; ex-ante formula engine; UT 2026 |
| `LdC_LBF_Instrument_Report` / `LdC_Analisis_Normativa_Instrumentos_ES` (Docs) | Legal framework, instrument status (operational vs designed), ordinance formulas |
| `Recaudación por Año - Factibilidad de Agua y Cloaca.xlsx` | Water & sewer collections 2021–2025 (nominal ARS) |
| `Recaudado inmueble ocioso.xlsx` (padrón) | Vacant-land surcharge: 5,315 lots; 2026 emission |
| `Obras y Espacios Públicos - Proyectos a ejecutar 2026.pdf` (Plan de Obras) | 2026 public-works programme → betterment-levy cost base |
| `Valor de suelo.png` / `Avalúo Fiscal.png` (Mapas) | Undeveloped land prices (USD/m²) and fiscal assessment (UT) → CEODEC/PVA unit-price calibration |

Drive path: `ECONOMÍA URBANA / ORDENANZA DE ECONOMÍA URBANA / 4. Registros fiscales y administrativos` (and project root for the LdC_LBF_* model/report).

## Key figures used

**Macro (real):** UT 2026 = ARS 235 (Tarifaria 2026, Art. 54); 2025 avg FX = ARS 1,244.17/USD; INDEC CPI for real-terms deflation.

**Realized — water & sewer feasibility contribution (USD, FX-adjusted):**
2021 = 60,699 · 2022 = 97,212 · 2023 = 168,756 · 2024 = 246,004 · 2025 = 690,497.
Real CAGR 2021–2025 = **83.7%** (≈11× real growth).

**Realized — vacant-land surcharge (2026 padrón):** 5,315 lots
(4,996 @ +100%, 319 @ +200%); surcharge ≈ ARS 493 M of the 2026 emission;
estimated annual collection ≈ ARS 345 M = **USD 277,539** (≈ARS 93,000/lot).

**Combined realized operational revenue ≈ USD 0.97 M/yr.**

**2026 public-works programme (Plan de Obras) — betterment-levy cost base:**
10 funded projects, total **ARS 6,853,882,500** (~USD 5.51 M). Each carries a
planning-priority weight (EA): priority-1 = 80%, priority-2 = 20%.

| Priority | Projects | Budget (ARS) |
| --- | --- | --- |
| 1 (80%) | Cacique Guaymallén bridge (2,000M); Urban centrality (1,500M); Saenz Peña/Ruta 15 centrality (1,500M); Microplazas (1,200M) | 6,200,000,000 |
| 2 (20%) | Speed reducers (350M); Infra/stops (200M); Bus shelters (33.75M); Sidewalks Zapiola/Pueyrredón (30.56M); Boulevard T. del Fuego (24.57M); Polideportivo sidewalk (15M) | 653,882,500 |
| | **Total funded** | **6,853,882,500** |
| | Priority-weighted (EA 80/20) | 5,090,776,500 |
| | Betterment-eligible, weighted (excl. ID 1274 bridge) | **3,490,776,500** |

12 further projects carry no separate 2026 budget (operating pavement budget or
provincial execution) and are excluded.

**Ex-ante value capture (ordinance formulas × real parameters):**

- *Betterment (CPM)* — base = betterment-eligible, EA-weighted works ≈ **ARS 3.49 B
  (USD 2.81 M)**; cost-recovery 25–50% (legal caps: ≤ value increment; aggregate
  ≤ 50% of assessed value) → **ARS 0.87–1.75 B/yr (USD 0.70–1.40 M)**.
- *Differential rent (PVA)* — land-value map; 5,000–50,000 m²/yr × 30–200 UT/m²
  → **ARS 35–2,350 M/yr (USD 0.03–1.89 M)**.
- *Development rights (Suelo Creado/CEODEC)* — land-value map; 2,000–20,000 m²/yr ×
  50–300 UT/m² → **ARS 24–1,410 M/yr (USD 0.02–1.13 M)**.
- TDR and tax incentives: not separately quantified (untraded market / net cost early on).

| Scenario | Value-capture subtotal | + Realized operational | **Total annual** |
| --- | --- | --- | --- |
| Low | USD 0.75 M | 0.97 M | **1.72 M** |
| Base | USD 1.65 M | 0.97 M | **2.62 M** |
| High | USD 4.42 M | 0.97 M | **5.39 M** |

**Illustrative financing gap:** green-space deficit ≈ 700,000 m²
(≈6 → 10 m²/hab, pop ≈175,000) × ~USD 80/m² ≈ **USD 56 M** one-off capital.
Baseline annual revenue covers ≈4–5%/yr pay-as-you-go; a green bond at 3–4× annual
revenue (~USD 8–10 M) is the leverage mechanism that closes the gap.

## What is real vs. still assumed

- **Real / measured:** all realized-revenue figures; UT, FX, CPI; the 2026 works
  programme cost base; the land-value and fiscal-assessment ranges.
- **Still assumed (pipeline):** the annual volumes of development rights, rezoning
  demand, and the exact cost-recovery share. These remain scenario parameters
  because the value-capture instruments are not yet sanctioned/applied; their
  *unit prices* are now calibrated to real land values, but *transaction volumes*
  await the development pipeline and the ordinance's Anexo Técnico coefficients.

Point estimates for the ex-ante instruments are therefore illustrative; the
contribution is the method plus the realized-revenue evidence.
