# Istruzioni del repository

## Contesto

Questo repository sviluppa una pipeline Python per analizzare dati
sperimentali relativi a un motore alimentato con miscele di gas naturale
e idrogeno, salvati in files .csv.
Un file d'esempio è presente nella cartella `sampleResults/` ed ha la stessa 
struttura dei files acquisti dal campo. 

L'analisi deve:

- leggere e pulire i file CSV;
- identificare i periodi di funzionamento stazionario;
- aggregare il rendimento elettrico `n_el` per percentuale di H2
  e livello di carico;
- calcolare media, deviazione standard e numerosità dei campioni;
- generare un grafico riepilogativo.

## Struttura del repository

- `sampleResults/`: dataset sintetico per sviluppo e verifica;
- `experimentalResults/`: dati sperimentali di produzione;
- `analysis/`: codice Python della pipeline;
- `tests/`: test automatici;
- `results/`: output e grafici generati;

Il codice della pipeline deve essere scritto in `analysis/`.

I test automatici devono essere scritti in `tests/`.

Gli output devono essere salvati in `results/` o nella directory specificata
tramite l'interfaccia da riga di comando.

## Regole sui dati

Utilizza esclusivamente i file contenuti in `sampleResults/` per:

- comprendere la struttura dei dati;
- sviluppare il codice;
- verificare la pipeline;
- creare test e fixture sintetiche.

Non devi:

- aprire, cercare o elaborare file in `experimentalResults/`;
- modificare i file presenti nei dataset;
- utilizzare i dati di produzione per sviluppo o test;

L'esecuzione sui dati di produzione è riservata all'utente e potrà essere
eseguita tramite CLI su terminal o interfaccia vs code (es. modalità debug)

## Regole sull'ambiente virtuale

L'ambiente virtuale da utilizzare è .venv. 
L'installazione di un pacchetto in .venv deve essere sempre autorizzata dall'utente. 


## Regole Generali
Il codice pulito, sicuro e facilmente mantenibile.

# Regole Obbligatorie
- Utilizza .venv 
- Utilizza NumPy e SciPy per l'analisi dei dati.
- Utilizza MatPlotLib per il plotting.
- Utilizza DataFrame in Pandas per la gestione dei dati.
- Usa nomi descrittivi per variabili, funzioni e classi.
- Prima di scrivere codice, ragiona su come strutturare il workflow.

# Regole di Stile
- Utilizza programmazione ad oggetti.
- Preferisci funzioni pure.
- Evita classi di lunghezza superiore a 120 righe.
- Aggiungi commenti con le motivazioni e spiegazioni.
