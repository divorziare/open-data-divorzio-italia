# Changelog

Tutti i cambiamenti notevoli a questo dataset sono documentati qui.
Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).

## [0.2.0] — 2026-10-26

I valori sono invariati: tolte le due colonne nuove, i CSV coincidono byte
per byte con quelli della 0.1.0.

### Aggiunto
- Colonne `Codice territorio` (codice ISTAT, es. `ITC4`) e `Livello
  territoriale` (`nazionale`, `ripartizione`, `regione`, `provincia
  autonoma`) subito dopo `Territorio` nei 5 CSV con dimensione
  territoriale. Permettono di selezionare un solo livello senza elencare
  i nomi e di evitare il doppio conteggio del Trentino-Alto Adige
  (regione + province autonome di Bolzano e Trento).
- `scripts/validate.py`: controlli di struttura e circa 20.000 identità
  contabili (classi d'età, gerarchia territoriale, giudiziali +
  extragiudiziali, coerenza dei totali tra file), con tolleranza per le
  piccole discrepanze ISTAT.
- CI GitHub Actions: rigenera i CSV da `data/raw/`, verifica che
  coincidano con quelli committati ed esegue la validazione.
- Documentazione delle discrepanze ±1–2 presenti dal 2013, dell'anomalia
  Campania 2016 (26 divorzi nel totale Italia ma in nessuna regione) e
  della rottura di serie del 2015.
- Notebook: quote marito/moglie/entrambi tra i richiedenti del divorzio
  giudiziale e distribuzione per regione.

### Corretto
- README: `eta-e-durata-del-divorzio.csv` descriveva età e durata dei
  matrimoni finiti in divorzio; in realtà conta i divorziati che si
  risposano, per età al nuovo matrimonio e anni trascorsi dalla fine del
  precedente.
- README e `docs/sources.md`: copertura reale (2008–2022, 2007–2022,
  2015–2024) invece di "oggi"; `eta-al-divorzio-coniugi.csv` è solo
  nazionale; le aree sono 20 regioni + 2 province autonome, non "22
  regioni + 2 province autonome".
- README: l'esempio "Distribuzione per regione" contava due volte il
  Trentino-Alto Adige; l'esempio csvkit (`-r 'giudiziale'`) mescolava la
  durata della separazione giudiziale con quella consensuale
  extragiudiziale.
- README: nel file `coniuge-che-ha-presentato-…` l'indicatore passa da
  `divorzi concessi` a `divorzi concessi dal tribunale` nel 2015, quindi
  il filtro consigliato su `divorzi concessi` scartava gli anni 2015–2022.
- `docs/sources.md`: copertura per indicatore di
  `procedimenti-e-separazioni.csv` (il numero di separazioni si ferma al
  2014).
- `CITATION.cff`: l'abstract citava dati sui figli coinvolti nei divorzi
  giudiziali, che il repository non contiene.
- Script di conversione: `OBS_STATUS` veniva letto dalla prima posizione
  degli attributi dell'osservazione invece che da quella dichiarata nella
  struttura (nessun effetto sui dati attuali, dove il flag è sempre
  vuoto).

## [0.1.0] — 2026-04-18

### Aggiunto
- Primo rilascio pubblico.
- CSV puliti per 6 temi ISTAT:
  - Età al divorzio (coniugi, marito, moglie)
  - Età e durata del divorzio
  - Coniuge che ha presentato la domanda (rito giudiziale)
  - Procedimenti e separazioni
- Script di conversione SDMX-JSON → CSV (`scripts/istat_sdmx_to_csv.py`),
  stdlib only.
- Notebook di esempio (`notebooks/esempio-analisi.ipynb`).
- Documentazione: `README.md`, `docs/sources.md`, `docs/methodology.md`.
- Licenza CC BY 4.0 per i dati, MIT per il codice.
- `CITATION.cff` per attribuzione accademica.
