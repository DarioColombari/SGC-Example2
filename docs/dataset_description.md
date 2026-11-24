## Informazioni impianto e sperimentazione
Le prove sperimentali sono effettuate su un motore al variare della percentuale di idrogeno in miscela di combustibile. 

La percentuale di idrogeno è identificata da un numero nel nome del file. 
Es. nome: "prova_auto_x*.csv", x indica la percentuale di idrogeno. 

Il motore ha una potenza nominale (massima) di 30 kW


## Formato dei files
I file CSV possono contenere:

- righe di metadati prima dell'header;
- separatore `;`;
- virgola come separatore decimale;
- delimitatori finali non uniformi;
- spazi iniziali

Le grandezze rilevanti nelle colonne del .csv da utilizzare nell'analisi sono:
- Time, timestamp di acquisizione
- WT01, potenza elettrica generata;
- P_in, potenza termica in ingresso da combustibile;
- n_th, efficienza termica; 
- n_el, efficienza elettrica. 

La colonna WT01 deve essere utilizzata per identificare i punti stazionari
