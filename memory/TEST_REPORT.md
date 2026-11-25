# Test report

## Esecuzione

Comando: `python -m pytest -q`

Risultato: **13 superati, 0 falliti**.

## Copertura

La suite verifica:

- parsing CSV con metadati, separatore `;`, virgola decimale, spazi e valori
  mancanti/`Inf`/`-Inf`;
- estrazione H2, rollover della mezzanotte e delimitatori finali;
- periodi stazionari validi, durata insufficiente e combinazioni H2/carico;
- media, deviazione standard e numerosità prodotte dall’aggregazione;
- plotting di DataFrame già aggregati, senza ricalcolo delle statistiche;
- assi, etichette, unità, legenda, serie, barre di deviazione standard;
- backend `Agg`, chiusura delle figure e PNG valido a 300 dpi;
- directory di output, grafico vuoto esplicito ed errori dei dati di plotting;
- CLI con argomenti validi/non validi e analisi end-to-end su CSV sintetici.

## Difetti rilevati

### Rollover della mezzanotte — aperto

- Test: `test_loads_metadata_decimal_values_and_midnight_rollover`.
- Atteso: per `23:59:50`, `00:00:00`, `00:00:10`, elapsed time `0, 10, 20`
  secondi.
- Osservato: `0, 0, 10` secondi.
- Indicazione al programmer: correggere `_parse_elapsed_time` in
  `src/data_loading.py`, trattando il cambio di giorno come intervallo di
  10 secondi.

### Delimitatori finali non uniformi — aperto

- Test: `test_preserves_rows_with_nonuniform_trailing_delimiters`.
- Atteso: il delimitatore finale vuoto viene ignorato e entrambe le righe sono
  caricate.
- Osservato: le colonne vengono disallineate e il parsing di `Time` fallisce.
- Indicazione al programmer: ignorare le colonne vuote extra o normalizzare i
  delimitatori finali prima del parsing.

Nessun difetto aggiuntivo è stato rilevato nelle funzionalità di plotting e CLI.
