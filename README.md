# Open Data — Divorzio in Italia

Dataset aperti sul divorzio in Italia, derivati dalle statistiche ufficiali
ISTAT. Pubblichiamo **CSV puliti, documentati e pronti all'uso** per
giornalisti, ricercatori, studenti e sviluppatori che lavorano su temi di
diritto di famiglia, demografia e politiche sociali.

Il formato nativo ISTAT (SDMX-JSON) è pensato per macchine: navigarlo a
mano è quasi impossibile. Qui troverai gli stessi dati in CSV tidy, una
riga per osservazione, con etichette umane in italiano.

> Fonte: **ISTAT — Istituto Nazionale di Statistica**
> ([esploradati.istat.it](https://esploradati.istat.it)).
> Licenza dati: **CC BY 4.0** (vedi `LICENSE`).

## Dati disponibili

| File | Di cosa parla | Righe |
|---|---|---|
| [`data/csv/eta-al-divorzio-coniugi.csv`](data/csv/eta-al-divorzio-coniugi.csv) | Età combinata dei due coniugi al divorzio | ~3.100 |
| [`data/csv/eta-al-divorzio-marito.csv`](data/csv/eta-al-divorzio-marito.csv) | Età del marito al divorzio, per classe | ~8.700 |
| [`data/csv/eta-al-divorzio-moglie.csv`](data/csv/eta-al-divorzio-moglie.csv) | Età della moglie al divorzio, per classe | ~8.700 |
| [`data/csv/eta-e-durata-del-divorzio.csv`](data/csv/eta-e-durata-del-divorzio.csv) | Età al matrimonio × durata matrimonio → divorzio | ~15.300 |
| [`data/csv/coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv`](data/csv/coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv) | Chi ha depositato la domanda (marito, moglie, congiunto) | ~2.100 |
| [`data/csv/procedimenti-e-separazioni.csv`](data/csv/procedimenti-e-separazioni.csv) | Procedimenti di separazione e durata media | ~2.900 |

Tutti i CSV hanno la stessa struttura di base:

- una colonna per ogni **dimensione** della serie (territorio, classe
  d'età, stato civile, …) — in italiano;
- `TIME_PERIOD` — l'anno;
- `VALUE` — il valore numerico;
- `OBS_STATUS` — eventuale flag ISTAT (es. provvisorio, non disponibile);
- `SOURCE` — identificativo del dataflow ISTAT (permette di separare
  serie storiche legacy da serie correnti — vedi
  [`docs/sources.md`](docs/sources.md)).

## Quick start

### Python (stdlib)

```python
import csv
from pathlib import Path

path = Path('data/csv/eta-al-divorzio-marito.csv')
with path.open(encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        if row['TIME_PERIOD'] == '2022' and row['Classe di età del marito al divorzio'] == '45-49 anni':
            print(row['VALUE'])
```

### Python (pandas)

```python
import pandas as pd

df = pd.read_csv('data/csv/eta-al-divorzio-marito.csv')
df['TIME_PERIOD'] = df['TIME_PERIOD'].astype(int)

# Solo la serie corrente (metodologia post-2017)
df_curr = df[df['SOURCE'] == '27_470_DF_DCIS_DIVORDEMCONG1_5']

# Divorzi totali per anno
totali = df_curr[df_curr['Classe di età del marito al divorzio'] == '15 anni e più']\
    .groupby('TIME_PERIOD')['VALUE'].sum()
print(totali)
```

### R

```r
df <- read.csv("data/csv/eta-al-divorzio-marito.csv", encoding = "UTF-8")
head(df)
```

### CLI

```bash
# Quanti divorzi totali nel 2022, serie corrente?
csvgrep -c 'SOURCE' -m '27_470_DF_DCIS_DIVORDEMCONG1_5' \
        data/csv/eta-al-divorzio-marito.csv \
  | csvgrep -c 'TIME_PERIOD' -m '2022' \
  | csvgrep -c 'Classe di età del marito al divorzio' -m '15 anni e più' \
  | csvstat -c 'VALUE' --sum
```

Vedi anche [`notebooks/esempio-analisi.ipynb`](notebooks/esempio-analisi.ipynb)
per esempi più ampi.

## Rigenerare i CSV dai JSON originali

I file SDMX-JSON originali, scaricati dal portale I.Stat, sono in
[`data/raw/`](data/raw/). Per rigenerare i CSV:

```bash
python3 scripts/istat_sdmx_to_csv.py
```

Lo script richiede solo **Python 3.9+** (nessuna dipendenza esterna).
Dettagli in [`docs/methodology.md`](docs/methodology.md).

## Aggiornamenti

ISTAT aggiorna le serie annualmente (di solito nel quarto trimestre).
Quando escono nuovi dati:

1. Scaricare il JSON aggiornato da
   [esploradati.istat.it](https://esploradati.istat.it).
2. Sostituire il file in `data/raw/`.
3. Eseguire `python3 scripts/istat_sdmx_to_csv.py`.
4. Aprire una PR con diff dei CSV.

Per essere avvisato degli aggiornamenti: metti una ⭐ al repo o attiva
le "Release notifications" su GitHub.

## Come citare

Se usi questi dati in un articolo o ricerca, la forma di citazione
richiesta è:

> Fonte: ISTAT, via **divorziare.it / open-data-divorzio-italia**
> (github.com/divorziare/open-data-divorzio-italia).
> Licenza CC BY 4.0.

Il repository include anche un file [`CITATION.cff`](CITATION.cff)
leggibile dai gestori di citazioni accademiche (Zotero, GitHub "Cite
this repository", Zenodo).

## Licenze

- **Dati** (`data/`): **CC BY 4.0** — vedi [`LICENSE`](LICENSE).
  ISTAT rilascia i dati originali sotto la stessa licenza.
- **Codice** (`scripts/`, `notebooks/`): **MIT** — vedi
  [`LICENSE-CODE`](LICENSE-CODE).

## Contribuire

Questo è un repository curato. Contributi benvenuti se:

- ISTAT pubblica nuove serie rilevanti (diritto di famiglia) →
  aggiungi il JSON a `data/raw/` e apri una PR.
- Trovi errori nei CSV → apri una issue con l'osservazione specifica
  (dataflow, anno, dimensione).
- Vuoi proporre un nuovo formato di output (Parquet, TSV, JSON-LD per
  schema.org Dataset) → apri una issue per discutere.

Niente PR che modificano i valori dei dati: se un valore sembra sbagliato
il problema è a monte (ISTAT) e va segnalato a loro.

## Chi siamo

Il repository è mantenuto da **Legalium S.r.l. STA**, società dietro
[divorziare.it](https://www.divorziare.it), piattaforma italiana per il
divorzio online. Abbiamo raccolto questi dati per uso interno e li
pubblichiamo perché pensiamo che siano più utili a tutti aperti che
chiusi.

Per segnalazioni editoriali, collaborazioni o dati aggiuntivi:
[contatti](https://www.divorziare.it/contatti).
