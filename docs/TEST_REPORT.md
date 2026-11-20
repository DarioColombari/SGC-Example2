# Report test pipeline

## Verifica

- Comando: `python -m pytest -q`
- Esito: raccolta non avviata: l'interprete non contiene `pytest`
  (`No module named pytest`). Anche `pandas` non è installato.
- Test scritti: 10.
- Test superati: 0.
- Test falliti: 0 (nessun test raccolto).

## Copertura

Parsing dei metadati e del CSV, decimali italiani, colonne con spazi,
delimitatore finale dell'header, passaggio di mezzanotte, H2 da colonna o
nome file, valori mancanti e infiniti, sentinella del sensore, durata minima
dei tratti stazionari, assenza di tratti validi, statistiche, combinazioni
mancanti, grafico Agg/PNG, chiusura delle figure ed errore CLI.

## Difetti da verificare

- `test_load_dataset_cleans_csv_and_unwraps_midnight` documenta che il
  sentinella `-2370,37` dovrebbe essere trattato come valore mancante durante
  la pulizia; l'implementazione attuale lo conserva.
- `test_stationary_period_excludes_nonfinite_and_zero_input` documenta che
  dati non finiti o a ingresso nullo non devono produrre un tratto stazionario.

## Indicazioni

Installare le dipendenze nell'ambiente `.venv` con autorizzazione dell'utente,
poi eseguire nuovamente `python -m pytest -q`. Passare al `programmer` per
valutare la normalizzazione dei valori sentinella e rieseguire la suite.
