# Fonti ISTAT — Provenienza dei dataset

Tutti i dati in questo repository sono estratti dal portale **I.Stat**
([esploradati.istat.it](https://esploradati.istat.it)) via la API
SDMX-JSON ufficiale. Ogni richiesta è associata a un *dataflow* con
identificativo stabile, che abbiamo conservato nella colonna `SOURCE` di
ogni CSV.

## Mappa CSV → dataflow ISTAT

| CSV | Dataflow(s) | Copertura temporale | Granularità territoriale |
|---|---|---|---|
| `eta-al-divorzio-coniugi.csv` | `27_385_DF_DCIS_DIVORDEMCONG_4` · `27_470_DF_DCIS_DIVORDEMCONG1_4` | 2008-oggi | Italia, 5 macroregioni, 22 regioni + 2 PA |
| `eta-al-divorzio-marito.csv` | `27_385_DF_DCIS_DIVORDEMCONG_5` · `27_470_DF_DCIS_DIVORDEMCONG1_5` | 2008-oggi | Italia, 5 macroregioni, 22 regioni + 2 PA |
| `eta-al-divorzio-moglie.csv` | `27_385_DF_DCIS_DIVORDEMCONG_6` · `27_470_DF_DCIS_DIVORDEMCONG1_6` | 2008-oggi | Italia, 5 macroregioni, 22 regioni + 2 PA |
| `eta-e-durata-del-divorzio.csv` | `24_447_DF_DCIS_SPOSI_3` | 2015-oggi | Italia (solo totale nazionale) |
| `coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv` | `27_814_DF_DCIS_DIVFIG_10` · `27_945_DF_DCIS_DIVFIG1_8` | 2008-oggi | Italia, 5 macroregioni, 22 regioni + 2 PA |
| `procedimenti-e-separazioni.csv` | `27_349_DF_DCIS_SEPARAZIND_1` · `27_474_DF_DCIS_SEPARAZIND1_1` | 2007-oggi | Italia, 5 macroregioni, 22 regioni + 2 PA |

### Indicatori per file

- **File età al divorzio** (`marito`, `moglie`, `coniugi`): l'indicatore
  può essere `divorzi concessi` (totale), `divorzi concessi dal
  tribunale` (giudiziali), `divorzi consensuali extragiudiziali`.
  Gli ultimi due sommano al primo.
- **`procedimenti-e-separazioni.csv`**: 9 indicatori distinti sulla
  separazione (durata media, tassi, percentuali di rito consensuale).
- **`eta-e-durata-del-divorzio.csv`**: `sposi` e `spose` — conteggio
  di uomini e donne divorziati/e al momento di un successivo matrimonio,
  disaggregati per età al matrimonio precedente, anno di cessazione e
  durata.
- **`coniuge-che-ha-presentato-la-domanda-*.csv`**: `divorzi concessi`
  (totale), `divorzi concessi dal tribunale`.

## Perché alcuni temi compaiono in due dataflow

ISTAT periodicamente ridisegna le serie statistiche per adeguarsi a
nuove classificazioni o per coprire rotture metodologiche. In questi
casi pubblica:

- una serie **storica legacy** (es. `DIVORDEMCONG_4`), che copre gli
  anni più vecchi ma non viene più aggiornata;
- una serie **corrente** (es. `DIVORDEMCONG1_4`), che parte da un
  anno di riferimento più recente e prosegue con la metodologia nuova.

Abbiamo conservato entrambe in un unico CSV e inserito il dataflow di
origine nella colonna `SOURCE` per permettere al lettore di filtrare
secondo le proprie esigenze (serie lunga ma con rottura metodologica,
vs serie corta ma omogenea).

## Verifica e aggiornamento

Per controllare se ISTAT ha pubblicato aggiornamenti:

1. Aprire [esploradati.istat.it](https://esploradati.istat.it) e cercare
   il dataflow (es. `DIVORDEMCONG1_4`).
2. Scaricare il JSON via SDMX API e sostituire il file corrispondente in
   `data/raw/`.
3. Eseguire `python3 scripts/istat_sdmx_to_csv.py`.
4. Verificare il diff sul CSV generato.

## Licenza originale ISTAT

ISTAT rilascia i propri dati sotto licenza Creative Commons Attribution
4.0 ([note legali ISTAT](https://www.istat.it/it/note-legali)). Questo
repository eredita la stessa licenza per la componente dati; vedere
`LICENSE` per il testo completo e l'attribuzione richiesta.
