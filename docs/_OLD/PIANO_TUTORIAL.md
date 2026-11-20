# Piano di implementazione – Tutorial "Programmazione agentica con GitHub Copilot"

> **Per GitHub Copilot:** questo documento descrive come **preparare il repository** per il tutorial.
> Il tuo compito è eseguire le attività della **Fase 1**, una per volta, nell'ordine indicato e rispettando i criteri di accettazione.
> **Non** scrivere il codice di analisi dati né i test: verranno generati **dal vivo** durante il tutorial dagli agenti definiti qui.
> Le Fasi 2 e 3 sono svolte manualmente dal relatore e servono solo come contesto.

---

## 1. Obiettivo del tutorial

Mostrare a colleghi, in **15 minuti**, un flusso di programmazione agentica con GitHub Copilot applicato all'analisi dati di prove sperimentali su un motore a combustione interna da 30 kWe alimentato con miscele di gas naturale e idrogeno (0–12 % vol).

Concetti da mostrare:

1. **Separazione tra dati di esempio e dati di produzione**: gli agenti leggono solo la *struttura* dei dati da un campione ridotto (`sampleResults/`). L'analisi sui dati reali (`experimentalResults/`) la esegue **solo l'umano**.
2. **Agenti specializzati con tool limitati**, invocati **manualmente in sequenza** (niente sessione multi-agente):
   - `programmer` → scrive le funzioni di analisi dati;
   - `edge-case-tester` → scrive ed esegue test sui casi limite.
3. **Handoff** tra agenti: un pulsante a fine risposta passa al prossimo agente, ma è l'utente a decidere quando.
4. **Limiti**: le istruzioni agli agenti sono una convenzione, non una barriera di sicurezza.

---

## 2. Stato attuale del repository e problemi noti

| Elemento | Stato | Problema |
|---|---|---|
| `experimentalResults/*.csv` | 7 file, ~4380 righe ciascuno (H2 = 0, 2, 4, 6, 8, 10, 12 %) | Dati di produzione: gli agenti non devono leggerli. |
| `sampleResults/prova_auto_struttura.csv` | Dataset **sintetico** (160 righe): stessa struttura e formato della produzione, valori generati artificialmente | Nessuno: è l'unico file che gli agenti devono leggere. Il nome non contiene la % di H2 (vedi sotto). |
| `copilot-instructions.md` | Nella root | Copilot lo carica automaticamente solo da `.github/copilot-instructions.md`. |
| `.github/agents/programmer.agent.md` | Presente | Refuso nei tool (`ms-python. python`); i passi 4–8 spingono l'agente a elaborare i dati completi. |
| `.github/prompts/generateCode.prompt.md` | Presente | Non indica la cartella del campione né la struttura del codice attesa. |
| `exampleScript/` | Soluzione di riferimento già generata | Se resta nel workspace, gli agenti possono copiarla e la demo perde senso. |
| `requirements.txt`, `tests/` | Assenti | Servono per eseguire pytest durante la demo. |

### Caratteristiche dei dati rilevanti per il tutorial

Il formato CSV di esportazione del banco prova ha queste particolarità, utili come casi limite:

- 3 righe di metadati (`Start Time: | hh:mm:ss`, `Selected mode: | ...`, `Test Duration: | ... hr`) prima dell'header;
- separatore `;` e **virgola decimale**;
- `;` finale **solo nella riga di header** (le righe dati ne sono prive) → colonna vuota `Unnamed` in pandas;
- alcuni nomi di colonna con **spazio iniziale** (`" TE05"`, `" TOTEM-T4"`);
- valori `Inf` / `-Inf` nelle colonne calcolate `n_th`, `n_el`;
- campionamento ~10 s, colonna `Time` in formato `hh:mm:ss` che **riparte da 00:00** a mezzanotte (accade in tutti i file);
- nel file allo 0 % le colonne `AP-02`, `AP-03`, `AP-08` valgono `-2370,37` in **tutte** le righe (sensori guasti); nel file al 6 % sono valide;
- la percentuale di idrogeno è nel nome dei file di produzione (`prova_auto_<H2>-costante-75.csv`) e nella colonna `ZY-FC02` (intero, % vol). Il file di esempio `prova_auto_struttura.csv` **non** la riporta nel nome: il codice deve gestire entrambi i casi (es. leggere `ZY-FC02` se il nome non la contiene);
- colonne principali per l'analisi: `TOTEM-W1` (potenza elettrica, kW), `V_in` (portata combustibile), `P_in` (potenza in ingresso, kW), `n_el` (rendimento elettrico, frazione).

---

## 3. Fase 1 – Preparazione del repository (eseguita da Copilot)

Eseguire le attività in ordine. Dopo ogni attività, verificare i criteri di accettazione prima di passare alla successiva.

### 1.1 Spostare le istruzioni globali di Copilot

- `git mv copilot-instructions.md .github/copilot-instructions.md`.
- Aggiungere in fondo una sezione **"Regole sui dati"**:
  - i dati in `experimentalResults/` sono dati di produzione: non leggerli, non aprirli, non eseguire codice su di essi;
  - per capire la struttura dei dati usare **solo** `sampleResults/`;
  - non leggere e non prendere spunto da `exampleScript/` (se ancora presente);
  - l'esecuzione dell'analisi sui dati di produzione è riservata all'utente.

**Accettazione:** il file esiste solo in `.github/copilot-instructions.md`; le regole originali sono invariate; la nuova sezione è presente.

### 1.2 Dataset di esempio – GIÀ COMPLETATO, non modificare

`sampleResults/prova_auto_struttura.csv` è un dataset **sintetico**: nessun valore proviene dalla produzione. Riproduce header, formato numerico e relazioni fisiche tra le colonne (`n_el = TOTEM-W1 / P_in`, `n_th = P_th / P_in`, `P_in ∝ V_in`, `V_in = FT01 + FT02`).

Contenuto (20 righe dati a ~10 s, dalle 23:58:00 alle 00:01:09):

| Righe dati | Fase | Caratteristiche |
|---|---|---|
| 1–3 | Motore spento | `V_in = 0`, `P_in = 0` → `n_el = -Inf`, `n_th = Inf` |
| 4–5 | Avvio | potenza negativa durante il trascinamento → `n_el` negativo |
| 6–9 | Rampa | da ~4 a ~12 kW |
| 10–20 | Carico al 50 % | ~15 kW, `n_el` ≈ 0,25; passaggio di mezzanotte alla riga 14 |

Altre caratteristiche: `AP-02` = `-2370,37` su tutte le righe (sensore guasto); `ZY-FC02` = 5 (% H2, valore non presente in produzione); intervallo di campionamento con jitter 9–11 s.

Il file serve **solo a mostrare la struttura**: il tratto a carico costante dura ~110 s, meno di quanto richiesto da criteri di stazionarietà realistici (≥ 3 min). È normale che l'analisi eseguita sul campione non trovi punti stazionari: l'agente non deve allentare i criteri per farli comparire.

**Non** rigenerare né modificare questo file.

### 1.3 Correggere l'agente `programmer`

Riscrivere `.github/agents/programmer.agent.md` mantenendo il ruolo attuale (ricercatore senior, esperto di analisi dati e Python).

Frontmatter:

```yaml
---
name: programmer
description: Scrive funzioni di analisi dati in Python basandosi solo sulla struttura del dataset di esempio
tools: [vscode, read, edit, search, execute]
handoffs:
  - label: Passa al tester dei casi limite
    agent: edge-case-tester
    prompt: Scrivi ed esegui i test dei casi limite per il codice appena generato nel package analysis/.
    send: false
---
```

> Nota: rimuovere il tool `ms-python. python` (refuso). Se serve il tool dell'estensione Python, usare il nome esatto mostrato nel selettore tool di VS Code.

Comportamento richiesto (sostituisce i passi 1–8 attuali):

1. Leggere la struttura dei dati **solo** da `sampleResults/` (metadati, header, separatore, formato numerico, colonne utili).
2. Ragionare sugli step dell'analisi e descriverli brevemente prima di scrivere codice.
3. Scrivere il codice nel package `analysis/`, organizzato in **funzioni piccole e testabili**, con responsabilità separate:
   - lettura ed estrazione dei dati da un file;
   - individuazione dei tratti stazionari;
   - calcolo delle statistiche per livello di H2 e di carico;
   - generazione del grafico;
   - entry point CLI `python -m analysis --dataset-dir <dir> --output-dir <dir>`.
4. Verificare che il codice giri **esclusivamente** su `sampleResults/` (`--output-dir results/sample`).
5. **Mai** leggere o eseguire codice su `experimentalResults/`: a fine lavoro indicare all'utente il comando da lanciare sui dati di produzione.
6. Non scrivere test: è compito di `edge-case-tester`.
7. Fermarsi e chiedere chiarimenti se gli obiettivi non sono chiari; fermarsi dopo 10 iterazioni fallite.

**Accettazione:** frontmatter YAML valido; nessun riferimento all'elaborazione dell'"intero dataset"; vincoli sui dati espliciti.

### 1.4 Creare l'agente `edge-case-tester`

Creare `.github/agents/edge-case-tester.agent.md`.

Frontmatter:

```yaml
---
name: edge-case-tester
description: Scrive ed esegue test pytest sui casi limite delle funzioni di analisi dati
tools: [vscode, read, edit, search, execute]
handoffs:
  - label: Torna al programmer per correggere
    agent: programmer
    prompt: Correggi il codice in analysis/ in modo che i test falliti passino, senza modificare i test.
    send: false
---
```

Ruolo: ingegnere della qualità del software, esperto di testing in Python e di dati sperimentali "sporchi".

Comportamento richiesto:

1. Leggere il codice in `analysis/` e la struttura dei dati in `sampleResults/`.
2. Scrivere i test in `tests/` con **pytest**, generando i dati di input in modo **sintetico** (fixture con `tmp_path`, CSV costruiti in memoria). Non leggere `experimentalResults/` e non scrivere in `sampleResults/`.
3. Coprire almeno questi casi limite:
   - righe di metadati prima dell'header;
   - separatore `;` con virgola decimale;
   - `;` finale solo nella riga di header (colonna `Unnamed`);
   - nomi di colonna con spazi iniziali;
   - `Inf` / `-Inf` / valori mancanti in `n_el`;
   - passaggio di mezzanotte nella colonna `Time`;
   - valori sentinella dei sensori guasti (es. `-2370,37`);
   - file senza alcun tratto stazionario;
   - combinazioni H2/carico mancanti nel riepilogo e nel grafico;
   - nome file da cui non si ricava la percentuale di H2;
   - file vuoto o con solo l'header.
4. Eseguire `python -m pytest -q` e riportare una tabella: caso limite → esito → causa del fallimento.
5. **Non correggere il codice di produzione**: segnalare i difetti e proporre l'handoff al `programmer`.

**Accettazione:** frontmatter YAML valido; vincoli sui dati espliciti; elenco dei casi limite presente.

### 1.5 Aggiornare il prompt `generateCode`

Modificare `.github/prompts/generateCode.prompt.md`:

- aggiungere `agent: programmer` nel frontmatter;
- nella sezione **Vincoli** indicare che il dataset di riferimento per la struttura è `sampleResults/` e che la variabile di efficienza è `n_el`;
- aggiungere che il codice va organizzato nel package `analysis/` come descritto nell'agente;
- lasciare invariati contesto, output atteso (grafico con 7 riquadri) e regole di stile del grafico.

**Accettazione:** il prompt si può invocare con `/generateCode` e seleziona automaticamente l'agente `programmer`.

### 1.6 Creare il prompt `testEdgeCases`

Creare `.github/prompts/testEdgeCases.prompt.md` con `agent: edge-case-tester`, che chieda di testare il package `analysis/` sui casi limite elencati nella sezione 2 di questo documento ed eseguire pytest.

**Accettazione:** il prompt si può invocare con `/testEdgeCases`.

### 1.7 Dipendenze e file ignorati

- Creare `requirements.txt` con: `numpy`, `pandas`, `scipy`, `matplotlib`, `pytest`.
- Aggiungere a `.gitignore` la cartella di output `results/`.

**Accettazione:** `pip install -r requirements.txt` va a buon fine; `results/` è ignorata da git.

### 1.8 Rimuovere la soluzione di riferimento dal branch della demo

- Creare il branch `tutorial/soluzione-riferimento` contenente `exampleScript/` così com'è.
- Sul branch della demo, rimuovere `exampleScript/` (`git rm -r exampleScript`).

**Accettazione:** `exampleScript/` non è presente sul branch della demo ma è recuperabile dal branch `tutorial/soluzione-riferimento`.

---

## 4. Fase 2 – Prova generale (eseguita dal relatore)

1. ~~Generare il campione~~: già fatto (`sampleResults/prova_auto_struttura.csv`, sintetico).
2. Commit della preparazione su `main` (o un branch `tutorial/setup`).
3. Eseguire la demo completa e cronometrare ogni passo.
4. Salvare i risultati di ogni passo su branch di riserva, da usare se un agente è lento o si blocca dal vivo:
   - `tutorial/step-1-programmer` (codice in `analysis/`);
   - `tutorial/step-2-tester` (test in `tests/` + output di pytest).
5. Eseguire sui dati di produzione e salvare il grafico finale:
   ```bash
   python -m analysis --dataset-dir experimentalResults --output-dir results/production
   ```

---

## 5. Fase 3 – Scaletta del tutorial (15 minuti)

| Tempo | Passo | Chi | Cosa mostrare |
|---|---|---|---|
| 0:00–2:00 | Contesto | Relatore | Struttura del repo, `.github/copilot-instructions.md`, file `.agent.md` e `.prompt.md`, separazione `sampleResults/` vs `experimentalResults/`. |
| 2:00–7:00 | Agente 1 | `programmer` via `/generateCode` | L'agente legge solo il campione, ragiona sugli step, scrive `analysis/` e lo prova sul campione. |
| 7:00–12:00 | Agente 2 | `edge-case-tester` via handoff o `/testEdgeCases` | Test sintetici sui casi limite; almeno un test che fallisce (es. sensori guasti del file allo 0 %, mezzanotte). |
| 12:00–14:00 | Produzione | Relatore, a mano | Esecuzione su `experimentalResults/` e grafico finale. "La produzione la tocca solo l'umano." |
| 14:00–15:00 | Conclusioni | Relatore | Limiti: le istruzioni non sono una barriera di sicurezza; il codice generato va sempre rivisto. |

### Messaggi chiave

- Un dataset di esempio non è rappresentativo di tutta la produzione: per esempio nel file allo 0 % sono guasti più sensori (`AP-02`, `AP-03`, `AP-08`), nel campione solo `AP-02`. Per questo serve un agente di test.
- Agenti con **ruoli e tool limitati** producono risultati più controllabili di un unico agente generalista.
- Gli **handoff** rendono esplicito il passaggio di consegne senza togliere il controllo all'utente.
- La separazione dei dati tramite istruzioni è una **convenzione**: un agente con il tool `read` può comunque aprire qualsiasi file del workspace.

---

## 6. Estensioni opzionali (solo da citare, non da eseguire dal vivo)

- **`data-profiler`** (tool: `read`, `search`): legge il campione e produce `docs/DATA_SCHEMA.md` con colonne, unità di misura, formato e anomalie; diventa il contesto per gli altri agenti.
- **`reviewer`** (tool: `read`, `search`): revisione del codice e della sicurezza (validazione degli input, gestione dei percorsi, eccezioni), in linea con il tema Secure Coding.

---

## 7. Fuori scope per Copilot

- Scrivere il codice in `analysis/` o i test in `tests/`.
- Leggere o eseguire codice su `experimentalResults/`.
- Modificare o rigenerare `sampleResults/prova_auto_struttura.csv`.
- Fare commit o push senza richiesta esplicita dell'utente.
