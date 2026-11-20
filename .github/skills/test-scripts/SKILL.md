---
name: test-scripts
description: Scrive ed esegue i test automatici della pipeline
disable-model-invocation: true
---
Analizza il package `analysis/`, elenca sinteticamente i casi di test
e implementa in `tests/` i test pytest per:

- lettura e pulizia dei CSV;
- valori mancanti, infiniti e sentinella;
- passaggio della mezzanotte;
- identificazione dei periodi stazionari;
- statistiche e combinazioni mancanti;
- CLI e generazione del grafico.

Usa esclusivamente dati sintetici creati con `tmp_path`.

Esegui:

  python -m pytest -q

Non modificare `analysis/`. Se trovi un difetto, descrivilo e proponi
il passaggio al `programmer`.