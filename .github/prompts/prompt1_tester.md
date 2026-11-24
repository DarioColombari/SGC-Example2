Consulta le istruzioni del repository, le specifiche in docs/ e il codice implementato in src/.

Elenca brevemente happy path, edge case ed error case, quindi implementa in tests/ i test pytest della pipeline dati.

Verifica:

- individuazione e lettura dei CSV;
- gestione di metadati, separatore, virgola decimale, spazi e delimitatori finali;
- estrazione della percentuale di H2 dal nome del file;
- gestione di valori mancanti, infiniti e sentinella;
- parsing temporale, incluso il passaggio della mezzanotte;
- identificazione dei periodi stazionari tramite WT01;
- comportamento in assenza di periodi stazionari;
- associazione ai livelli di carico;
- media, deviazione standard e numerosità di n_el;
- combinazioni H2/carico mancanti;
- struttura e ordinamento del DataFrame aggregato.

Crea esclusivamente piccoli CSV sintetici mediante tmp_path. Non usare i dataset del repository e non accedere a experimentalResults/ o exampleScript/.

Basa le aspettative sulla documentazione e sul contratto pubblico della pipeline. Non inventare soglie scientifiche e non rendere i test dipendenti dai dettagli interni dell’implementazione.

Puoi modificare soltanto tests/ e docs/TEST_REPORT.md. Non modificare src/.

Esegui:

python -m pytest -q

Riporta in docs/TEST_REPORT.md i casi coperti, il risultato dell’esecuzione e gli eventuali difetti, indicando comportamento atteso e osservato. Se rilevi un difetto nel codice di produzione, non correggerlo: proponi il passaggio al programmer.