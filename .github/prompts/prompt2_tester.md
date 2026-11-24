Analizza le funzionalità di plotting e CLI aggiunte in src/ e completa la suite pytest esistente senza modificare o indebolire i test della pipeline dati.

Aggiungi test per verificare:

- ricezione da parte del plotting di dati già aggregati;
- generazione del grafico senza ricalcolare le statistiche;
- presenza di assi, etichette, unità, legenda e serie attese;
- rappresentazione della deviazione standard;
- salvataggio di un PNG valido e non vuoto a 300 dpi;
- utilizzo del backend Matplotlib Agg;
- chiusura delle figure dopo il salvataggio;
- rispetto della directory di output richiesta;
- funzionamento della CLI con argomenti validi;
- gestione degli argomenti mancanti o non validi;
- esecuzione end-to-end su un piccolo dataset sintetico;
- assenza di regressioni nella pipeline dati.

Usa esclusivamente dati sintetici creati con tmp_path. Non confrontare le immagini pixel per pixel e non accedere a experimentalResults/, exampleScript/ o ai dataset del repository.

Puoi modificare soltanto tests/ e docs/TEST_REPORT.md. Non modificare src/.

Esegui l’intera suite:

python -m pytest -q

Aggiorna docs/TEST_REPORT.md con il comando eseguito, i test superati e falliti, i casi coperti e gli eventuali difetti. Se il problema è nel codice di produzione, non correggerlo e proponi il passaggio al programmer.