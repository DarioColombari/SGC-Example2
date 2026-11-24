Consulta le istruzioni del repository e le specifiche presenti in docs/.

Implementa nel package src/ la pipeline di elaborazione dati, senza realizzare ancora grafici o test automatici.

Utilizza il file in /sampleResults per identificare la struttura del csv da analizzare

La pipeline deve:

- individuare e leggere i CSV presenti nella directory indicata;
- gestire correttamente metadati, separatori, formato decimale, spazi e delimitatori finali;
- estrarre la percentuale di H2 dal nome del file;
- identificare i periodi stazionari usando WT01, applicando esclusivamente i criteri definiti nella documentazione;
- associare i campioni stazionari ai livelli di carico;
- aggregare n_el per percentuale di H2 e livello di carico;
- calcolare media, deviazione standard e numerosità dei campioni;
- restituire i risultati come DataFrame ordinato e pronto per il plotting.

Se i criteri scientifici necessari non sono definiti chiaramente, non inventare soglie: segnala l’ambiguità prima di procedere.

Mantieni separate le responsabilità di caricamento, pulizia, identificazione dei periodi stazionari e aggregazione. Verifica manualmente il risultato esclusivamente su sampleResults/, senza accedere a experimentalResults/ e senza modificare i dataset.

Non scrivere test e non implementare ancora la parte grafica. Al termine, indica i file modificati, le verifiche eseguite e la struttura del DataFrame aggregato.