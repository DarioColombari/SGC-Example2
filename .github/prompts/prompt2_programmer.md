Completa la pipeline dati già implementata in src/, senza duplicare né ricalcolare nelle funzioni di plotting le statistiche esistenti.

Implementa:

-un grafico riepilogativo di n_el per percentuale di H2 e livello di carico;
-assi, unità, legenda e titoli leggibili;
-rappresentazione della variabilità mediante la deviazione standard;
-salvataggio in formato PNG a 300 dpi;
-funzionamento senza interfaccia grafica mediante backend Agg;
-chiusura esplicita delle figure dopo il salvataggio;
-interfaccia CLI con directory del dataset e directory di output configurabili;
-un punto di ingresso utilizzabile sia da CLI sia tramite il tasto Run di VS Code.

Il plotting deve ricevere il DataFrame già aggregato prodotto dalla pipeline dati.

Esegui una verifica end-to-end esclusivamente con sampleResults/ e controlla che gli output siano creati nella directory richiesta. Non scrivere test e non installare pacchetti senza autorizzazione.

Al termine, riporta file modificati, comando eseguito e output generati, quindi proponi il passaggio al tester.