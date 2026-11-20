---
name: generate-scripts
description: Implementa la pipeline di analisi e genera il grafico finale
disable-model-invocation: true
---
Analizza i file sintetici in `sampleResults/` e implementa nel package
`analysis/` una pipeline che:

- legga e pulisca i CSV;
- individui i periodi stazionari rispetto a WT01;
- calcoli media, deviazione standard e numerosità di `n_el`
  per percentuale di H2 e livello di carico;
- generi un grafico PNG a 300 dpi;
- sia eseguibile con:

  python -m analysis --dataset-dir <dir> --output-dir <dir>

Verifica l'implementazione esclusivamente su `sampleResults/`.

Non scrivere test. Al termine, proponi il passaggio al `tester`.