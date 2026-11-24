# Test report

## Esecuzione

Comando: `python -m pytest -q`

Risultato: **10 passati, 3 falliti**.

## Copertura

I test in [tests/test_pipeline.py](../tests/test_pipeline.py) coprono:

- parsing di CSV con metadati, spazi, decimali con virgola e H2 nel nome;
- valori mancanti e infiniti;
- passaggio della mezzanotte;
- periodi stazionari, assenza di periodi e parametri non validi;
- statistiche, deviazione standard e combinazioni H2/carico presenti;
- errore per dataset assente;
- CLI, CSV di riepilogo, PNG e chiusura delle figure Matplotlib.

## Difetti rilevati

1. `test_stationary_period_is_not_split_into_single_sample_load_groups`: un
   tratto stazionario di 3 punti (`WT01` 14.49, 14.51, 14.49) viene aggregato
   in due livelli di carico con numerosità 2 e 1. Atteso: assegnare al periodo
   un unico livello basato sul carico medio, ottenendo `n_samples=3`.
2. `test_invalid_efficiencies_do_not_leave_one_negative_sample`: dopo aver
   rimosso `Inf` e `-999`, rimane un'efficienza negativa con `n_samples=1`.
   Atteso: escludere efficienze fisicamente non valide e non produrre gruppi
   con meno del numero minimo di campioni validi.
3. `test_missing_wt01_separates_two_valid_stationary_periods`: un solo `WT01`
   mancante impedisce l'identificazione di tutti i periodi. Atteso: il valore
   mancante separa i segmenti, preservando i due tratti stabili validi.

`min_points=3` si applica attualmente ai campioni `WT01` prima della pulizia di
`n_el` e prima dell'arrotondamento per livello di carico; pertanto non garantisce
che `n_samples` aggregato sia almeno 3.

Si raccomanda il passaggio al **programmer** per correggere segmentazione e
aggregazione mantenendo questi test come regressione.
