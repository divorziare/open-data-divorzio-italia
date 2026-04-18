# Changelog

Tutti i cambiamenti notevoli a questo dataset sono documentati qui.
Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).

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
