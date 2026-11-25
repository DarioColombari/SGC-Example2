Completa la pipeline dati già implementata in src/, senza duplicare né ricalcolare nelle funzioni di plotting le statistiche esistenti.

Crea uno script nel root del repo che può essere eseguito sia da CLI che da Run di vs code (anche in modalità debug), con le seguenti richieste: 
- lettura dei .csv singolarmete nella dataset_dir 
- dataset_dir di default /experimentalResults esplicitato in intestazione nel parser
- plot unico di efficienza (con deviazione std) al variare del carico per ogni percentuale di idrogeno
- le linee a percentuale di idrogeno fissa seguono la palette di colore standar di python
- riutilizza le funzioni /src il più possibile senza modificarle
- integra nuove funzioni nello script per riutilizzare quelle presenti solo se strettamente necessario

Regole da seguire: 
- non analizzare i .csv 

