# Piano di test per `Main_Analysis.py`

## Happy path

- Una directory contiene uno o più CSV validi con header, colonne `WT01` e `n_el`.
- Il nome di ogni file contiene una percentuale H2 numerica.
- I CSV contengono almeno un periodo stazionario.
- Lo script elabora ogni file separatamente.
- Per ogni file vengono creati:
  - un riepilogo CSV con media, deviazione standard e numerosità;
  - un PNG con l'efficienza in funzione del carico del generatore.
- L'asse X usa `WT01 / 30 * 100` e l'etichetta `Load level [%]`.
- Il titolo del subplot riporta la percentuale H2.
- I limiti X e Y restano comuni a tutti i subplot.
- L'esecuzione con i parametri CLI predefiniti e con parametri espliciti produce gli stessi risultati.

## Edge cases

- CSV con righe di metadati, spazi nei nomi delle colonne e decimali con virgola.
- Valori mancanti, infiniti e sentinella `-999`.
- Timestamp che attraversano la mezzanotte.
- CSV senza periodi stazionari: riepilogo vuoto e grafico salvato senza errori.
- Combinazioni H2/carico presenti solo parzialmente.
- Un solo punto per gruppo: deviazione standard impostata a zero.
- Più CSV con percentuali H2 differenti: un output distinto per file.
- Dataset vuoto o directory senza CSV.
- Nome file privo di percentuale H2.
- `Pnom` non positivo, finestra pari o parametri di stazionarietà non validi.
- Directory di output inesistente: deve essere creata automaticamente.
- Verifica della chiusura delle figure Matplotlib dopo il salvataggio.
