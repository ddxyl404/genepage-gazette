# AlphaFold URL consistency audit

**generated:** 2026-10-07 08:46 CST (Asia/Shanghai)
**genes checked:** 10
**passed:** 10
**issues:** 0

## Rule

`structure.alphafold_url` must match the AlphaFold entry in `sources[]` when both exist.
If `sources` has no AlphaFold row but `structure` has a URL, that is allowed.

## Results

**All genes passed.**

| symbol | status | structure.alphafold_url | sources AlphaFold url(s) |
|--------|--------|-------------------------|--------------------------|
| TP53 | pass | `https://alphafold.ebi.ac.uk/entry/P04637` | `https://alphafold.ebi.ac.uk/entry/P04637` |
| BRCA1 | pass | `https://alphafold.ebi.ac.uk/entry/P38398` | `https://alphafold.ebi.ac.uk/entry/P38398` |
| BRCA2 | pass | `https://alphafold.ebi.ac.uk/entry/P51587` | `https://alphafold.ebi.ac.uk/entry/P51587` |
| EGFR | pass | `https://alphafold.ebi.ac.uk/entry/P00533` | `https://alphafold.ebi.ac.uk/entry/P00533` |
| KRAS | pass | `https://alphafold.ebi.ac.uk/entry/P01116` | `https://alphafold.ebi.ac.uk/entry/P01116` |
| APOE | pass | `https://alphafold.ebi.ac.uk/entry/P02649` | `https://alphafold.ebi.ac.uk/entry/P02649` |
| CFTR | pass | `https://alphafold.ebi.ac.uk/entry/P13569` | `https://alphafold.ebi.ac.uk/entry/P13569` |
| HBB | pass | `https://alphafold.ebi.ac.uk/entry/P68871` | `https://alphafold.ebi.ac.uk/entry/P68871` |
| APP | pass | `https://alphafold.ebi.ac.uk/entry/P05067` | `https://alphafold.ebi.ac.uk/entry/P05067` |
| MYC | pass | `https://alphafold.ebi.ac.uk/entry/P01106` | `https://alphafold.ebi.ac.uk/entry/P01106` |
