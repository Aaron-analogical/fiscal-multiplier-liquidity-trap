# Errata in the original thesis

The French thesis is the official version, and the English translation keeps its text as printed. This list records apparent errors found while translating and rerunning the work. None of them changes a conclusion.

Each item needs Aaron's ruling before publication: keep as printed, or correct in the English version with a note.

## Numbers

| Where | Printed | Evidence | Likely value |
|---|---|---|---|
| Table 6.1, impact, normal times, α = 1, 𝕋 = 16 | 0.58 | Rerun gives 0.5916. The model output in `Dette.xlsx` holds 0.5916, and its summary sheet holds 0.58. | 0.59 |
| Section 4.4, lump-sum, normal times, α = 0 | 0.89 | Equation (45) and `Multiplicateur 3.5.xlsx` give 0.8975. | 0.90 |
| Section 4.4, lump-sum break-even | α = 0.176 | Equations (45) and (53) and the workbook give 0.1716. | 0.172 |

## Equations

| Where | As printed | Issue |
|---|---|---|
| Eq. (14), Annex A | MC = θ/(θ−1) at steady state | The code uses (θ−1)/θ, which follows from the firm's problem. |
| Eq. (34) | Term in δ̃Θk has no α | Eq. (42) includes α. |
| Eq. (49) | No Θτ term | Eq. (51) includes Θτ, and the printed trap results need it. |
| Eq. (51) | δ̃Θk has no α | Eq. (52) includes α. |
| Eq. (51) to (53) | Θr in the denominators | Should be Φr. Θr is not defined. |
| Section 4.3 | "substitute in equation (28)" | Should be equation (26). |
| Eq. (13) | β_s inside a product over x | Should be β_x, as in eq. (1). |
| Eq. (18) | B_t/Y_t | The code uses d(−1)/y, so lagged debt. |
| Section 4.4 | Θc expression | The expansion drops γ and ḡ from the inner term, and does not match Θg above it. |
| Annex A | F/C = Y/C = a/(1−g) | Identity (1) gives 1/(1−ḡ). |
| Annex A | N formula | The printed formula has (θ−1)/θ where the code has θ/(θ−1). |
| Annex A | C exponent b/(1−b) | The code uses 1/(1−b). |

## Cross-references and wording

| Where | As printed | Issue |
|---|---|---|
| Section 3 | Bouakez et al. (2017) cited twice for different shocks | The second citation should be 2020. |
| Section 3.1 | "subject to constraint (4)" | Should be constraint (5). |
| Section 3.2 | "production function (11)", "demand function (10)" | Should be (10) and (9). |
| Section 4.4 | γ = 0.29 called "Frisch elasticity of labor" | γ is a preference parameter, as Table 4.1 says. |
| Section 4.4, Table 4.1 | p = 0.8 in text | p is missing from Table 4.1. |
| Tables 5.1, 5.2 | Title says present-value multipliers | They also report impact multipliers. |
| Tables 6.1, 6.2, Figure 6.1 | Numbered 6.x | They sit in section 5. |
| Section 1 | "New Deal de 1930" | The New Deal began in 1933. |
| Bibliography | Calvo (1983), Fischer (1977), and others | These listed references are not cited in the text. |

## Code listing

| Where | As printed | Issue |
|---|---|---|
| Annex B, no-debt case | `k = (1-delta)*k(-1) + gi;` | Table 5.1 and 5.2 values for 𝕋 = 1 need `gi(-1)`, as shown by the rerun. The listing shows one setting of a line that was edited between runs. |
| Annex B, no-debt case | `eps_zeta` shock commented out with size 0.0261 | The 12-quarter trap uses 0.01 when ρζ = 0.95, as in the debt listing. |
| Project folder | `mod/Dernier/Nodebt.mod` has `rho_zeta = 0.85` | Annex B and the text use 0.95, which this repo follows. |

## Figures

The real-rate panels in Figures 5.1 to 5.6 plot the nominal rate minus current inflation. The Euler equation uses expected next-period inflation. This repo follows the thesis, so its panels reproduce the original values (0.19 and −0.31 in Figure 5.1). No multiplier depends on this choice.
