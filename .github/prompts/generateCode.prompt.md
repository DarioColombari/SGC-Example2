---
name: generateCode
description: Genera codice per l'analisi dati per l'analisi di un dataset
model: GPT-5.3-Codex (copilot)
---

# Contesto:
Sono stati svolti dei test sperimentali su un motore a combustione interna da 30 kW elettrici alimentato a gas naturale e idrogeno. Sono stati svolti dei test con una percentule d idrogeno variabile tra 0 e 12% in volume nel flusso di gas in ingresso. Le prove sono state svolte a diversi livelli di potenza elettrica erogata.

# Task:
Genera uno script di analisi dati che estragga, rielabori e faccia il grafico dei dataset forniti in ingresso.

# Vincoli 
- Utilizza solo i punti in cui il motore ha operato in modo stazionario.
- Separa i punti in base alla potenza elettrica erogata.
- Calcola l'efficienza media per ogni concentrazione di idrogeno e per ogni livello di carico.
- Utilizza colori diversi per le diverse concentrazioni di idrogeno.
- Il grafico deve avere un aspetto professionale e curato, ma senza essere troppo complicato.
- Genera un grafico che sia pronto per una pubblicazione scientifica.
- Utilizza label con unità di misura per asse X e Y.
- Inserisci un titolo per tutto il grafico.
- Utilizza Latex per label e testo.
- Salva i risultati come .svg
- Label e titoli devono essere in inglese.
- Il dataset è indicato dall'utente così come la notazione della variabile di efficienza

# Output:
Grafico con 7 riquadri, ognuno corrispondente ad una percentuale di idrogeno.
Sull'asse X deve essere presente il livello di carico (come % della potenza nominale) e sull'asse Y l'efficienza elettrica (in %).
