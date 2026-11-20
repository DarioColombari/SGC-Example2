# Istruzioni del repository

## Contesto

Questo repository contiene una pipeline Python per analizzare dati
sperimentali relativi a un motore alimentato con miscele di gas naturale
e idrogeno.

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
- `exampleScript/`: soluzione di riferimento da non consultare.

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
- leggere o utilizzare il contenuto di `exampleScript/`.

L'esecuzione sui dati di produzione è riservata all'utente.

Puoi indicare il seguente comando, ma non devi eseguirlo:

    python -m analysis \
      --dataset-dir experimentalResults \
      --output-dir results/production

Queste istruzioni definiscono il comportamento atteso, ma non costituiscono
una barriera tecnica di accesso ai file.

## Regole sull'ambiente virtuale

L'ambiente virtuale è .venv. 
L'installazione di un pacchetto in .venv deve essere sempre autorizzata dall'utente. 

## Formato dei dati

I file CSV possono contenere:

- righe di metadati prima dell'header;
- separatore `;`;
- virgola come separatore decimale;
- delimitatori finali non uniformi;
- spazi iniziali

## Descrizione della struttura del dataset

Il dati raccolti riguardano una campagna sperimentale per misurare le prestazioni di un motore cogenerativo al variare della percentuale di idrogeno miscelata con il gas naturale in ingresso. Le acquisizioni sperimentali sono salvati in files .csv.

Un file d'esempio è presente nella cartella `sampleResults/` ed ha la stessa struttura dei files acquisti dal campo. 

## Formato dei files

La percentuale di idrogeno è identificata da un numero nel nome del file. 
Es. nome: "prova_auto_x*.csv", x indica la percentuale di idrogeno. 

Alcune grandezze rilevanti nelle colonne del .csv: 
- WT01, potenza elettrica generata;
- P_in, potenza termica in ingresso da combustibile;
- n_th, efficienza termica; 
- n_el, efficienza elettrica. 


