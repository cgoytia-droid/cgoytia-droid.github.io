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

**Environmental–adaptation classification of the works** (paper Table 4):
works with high / medium-high environmental impact — aluvional (stormwater)
drainage in the Ciudad de Luján centrality (395), green microplazas (865),
the Tierra del Fuego green boulevard (575), and the canal-bridge + metrotranvía
connection (1274) — total **≈ARS 4.72 B (~69%)** of the funded programme. This
share is the climate-aligned portion that justifies earmarking betterment revenue
to the Trust Fund.

**Provincially-financed works** (paper Table 5; separate, excluded from the
municipal betterment base): new Río Mendoza road bridge + Ciclovía San Martín
(466); pedestrian overpasses on Acceso Sur at Malabia (467) and Castro Barros
(468). No municipal budget line → cannot be levied by the municipality.

A further seven projects (bike-lane network + repaving) sit in the operating
pavement budget and carry no separate line.

**Densification zones** (paper Table 6) — where Suelo Creado / PVA apply:
1. Metrotranvía / Liniers–San Martín **transit corridor** (TOD; E–W integration, ID 1274);
2. **Ciudad de Luján centrality** (compact infill; drainage upgrade, ID 395);
3. **La Carrodilla–Mayor Drummond** (centrality, ID 773; +200% vacant-land priority voids).
These coincide with the heaviest vacant-land surcharge zones, giving one coherent
spatial signal. The value-capture m²/yr pipeline is concentrated here.

**Buildability from the REAL COS 2026 schedule (paper Table 7)** — replaces the
earlier ΔFOT assumption. Source: draft COS 2026 (Tabla 10) and the zoning report
2019–2026. Two-line scheme: **base 10 m** (13 m in ZCM6), permitted without
instruments → **maximum 36 m** (~8.7 extra floors) reachable only via Derechos de
Construcción Adicional (Suelo Creado) and PVA. FOS 75–90%. Seven zones
(ZC, ZCM1, ZCM6, ZR1, ZRM1–3) = **4,491 ha** → **ceiling ≈ 295.15 million m²** of
additional buildable area (theoretical max, full take-up).

| Zone | ha (2022) | FOS | 10→36 m ceiling (m²) |
| --- | --- | --- | --- |
| ZRM2 | 1,356 | 75% | 88,137,947 |
| ZRM3 | 1,256 | 75% | 81,668,328 |
| ZRM1 | 901 | 75% | 58,596,637 |
| ZR1 | 714 | 75% | 46,410,451 |
| ZCM1 | 232 | 89% | 17,924,965 |
| ZC | 31 | 90% | 2,413,938 |
| **Total** | **4,491** | — | **295,152,266** |

Revenue is **demand-constrained**, not ceiling-constrained: modelled annual
take-up = **20,000 / 50,000 / 80,000 m²/yr** (Low/Base/High, <0.03%/yr of the
ceiling), split ~50/50. Built space sells at USD 300–1,200/m² (built-value map);
instruments capture a fraction (Suelo Creado 50–250 UT/m²; PVA 30–180 UT/m²; UT = ARS 235).

**Ex-ante value capture (ordinance formulas × real parameters):**

- *Betterment (CPM)* — EA-weighted eligible works ≈ **ARS 3.49 B (USD 2.81 M)**;
  recovery 25–50% (caps: ≤ value increment; aggregate ≤ 50% of assessed value)
  → **USD 0.70 / 1.12 / 1.40 M/yr**.
- *Development rights (Suelo Creado/DCA)* — COS 2026 take-up × 50–250 UT/m²
  → **USD 0.09 / 0.57 / 1.89 M/yr**.
- *Differential rent (PVA)* — COS 2026 take-up × 30–180 UT/m²
  → **USD 0.06 / 0.38 / 1.36 M/yr**.
- TDR and tax incentives: not separately quantified (untraded market / net cost early on).

| Scenario | Value-capture subtotal | + Realized operational | **Total annual** |
| --- | --- | --- | --- |
| Low | USD 0.85 M | 0.97 M | **1.82 M** |
| Base | USD 2.07 M | 0.97 M | **3.04 M** |
| High | USD 4.65 M | 0.97 M | **5.62 M** |

Long-run: the 295 M m² rights ceiling is a very large capture base that will not
bind for decades.

**Illustrative financing gap:** green-space deficit ≈ 700,000 m²
(≈6 → 10 m²/hab, pop ≈175,000) × ~USD 80/m² ≈ **USD 56 M** one-off capital.
Baseline annual revenue covers ≈5%/yr pay-as-you-go; a green bond at 3–4× annual
revenue (~USD 9–12 M) is the leverage mechanism that closes the gap.

**Trust Fund / fideicomiso (paper §5, expanded):** §5.3 broadened and a new §5.5
added on the Fideicomiso as a **matching-funds + repayment vehicle** — Leverage
Account (15%) ≈ USD 0.45 M/yr builds the 10–30% counterpart for GCF/bilateral
grants; the ring-fenced, audited flows give repayment security for a green bond
(~USD 9–12 M); real names woven in (BMTI, FEULDC, Ord. 15081/15093-2025).

## Priority index — rewritten to the real structure (paper §6)

Section 6 and Table 2 were rewritten to match the municipality's actual index
(`Índice de Ciudad Deseada` / `Índice de Priorización de Infraestructura`),
replacing the paper's invented "4 dimensions / 24 indicators / AHP weights
35-25-22-18". The real index has **six dimensions**: (1) green space &
biodiversity, (2) mobility & services, (3) compactness & functionality,
(4) accessibility to community services, (5) equity & community, and
(6) **basic infrastructure — including water demand (demanda hídrica)**,
network connectivity, green/recycling points, and public-space energy
use/self-generation. Scoring uses a **five-level sufficiency scale** (A ≥90%
… E <25%; lower = higher priority), not fixed weights (weights still pending).
Water enters the index through three channels (green infrastructure, the
basic-infrastructure water-demand indicator, and compactness). The abstract was
updated from "24-indicator" to "six-dimension".

## Alignment of investment with the priority index (paper §7.5)

A figure was added (**Figure 1**, `paper/figures/fig_alignment_works_vs_priority.png`):
district green-space need (x, A→E) vs 2026 place-based investment (y, ARS billion),
showing Ciudad/Carrodilla over-served and the D/E districts under-served.


Source: `Índice de Ciudad Deseada` (methodology doc) and `ÍNDICE DE PRIORIZACIÓN
DE INFRAESTRUCTURA.pdf` (district results, Oct 2025) — ICD folder. The index
scores each district A (≥90%) to E (<25%); lower = higher investment priority.
Only the **green-space subindex** is computed so far; the other five
(mobility, compactness, community services, equity, basic/water infrastructure)
are still being assembled.

**Where green investment is needed** (worst → highest priority):
- E (very insufficient): Vistalba, Las Compuertas, Industrial
- D (insufficient): Chacras de Coria, Agrelo, Mayor Drummond, Vertientes del Pedemonte
- A/B (already good): La Puntilla, Ciudad (A); Carrodilla, Potrerillos (B)

**Where it is being made (2026 works) → partial misalignment:**
- Centrality Ciudad (395, ARS 1.5 B) → district scores **A** (not green-priority).
- Centrality Carrodilla (773, ARS 1.5 B) → district scores **B** (not green-priority).
- Sidewalk Mayor Drummond (452) → district **D** → **aligned**.
- Vistalba / Las Compuertas / Industrial (worst) → **no dedicated 2026 green works**.
- **Microplazas (865, ARS 1.2 B, ~20 squares, dept-wide)** = the decisive lever:
  targeting them to D/E districts aligns investment with the index.

**Capture-vs-need logic:** value capture is generated in high-value consolidated
districts (Chacras de Coria, Vistalba, Carrodilla, Ciudad = densification zones),
some of which rank poorly on green space; the equity subindex will likely flag
peripheral low-income districts (Industrial, Las Compuertas). The Trust Fund +
index allocation rule is what redirects capture from high-value to high-need
areas (and guards against investing only where revenue is raised).

## What is real vs. still assumed

- **Real / measured:** all realized-revenue figures; UT, FX, CPI; the 2026 works
  programme cost base; the land-value, built-value and fiscal-assessment ranges;
  the 319 priority urban-void lot count anchoring developable land; the green-space
  subindex district results.
- **Derived bottom-up (no longer a bare assumption):** the buildable-area pipeline
  (developable land × ΔFOT × absorption, Table 7), which now drives the Suelo
  Creado and PVA volumes instead of a guessed m²/yr range.
- **Still parametric:** ΔFOT increment, build-out absorption rate, the 50/50
  split between the two instruments, and the cost-recovery share. These are
  documented scenario parameters; the per-zone COS base coefficients and the
  ordinance's Anexo Técnico unit prices would pin them down further once available.

Point estimates for the ex-ante instruments are therefore illustrative; the
contribution is the method plus the realized-revenue evidence.
