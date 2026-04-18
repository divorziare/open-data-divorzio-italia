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

### Due avvisi critici sui filtri

1. **`Territorio` non è sempre `Italia`**. I dataset includono 5
   macroregioni (Nord-ovest, Nord-est, Centro, Sud, Isole) e 22 regioni
   + 2 province autonome. Per il totale nazionale filtra sempre
   `Territorio == 'Italia'`, altrimenti stai sommando Italia + ogni
   regione e stai gonfiando il totale di ~3x.

2. **`Indicatore` è spesso decomposto**. Per i divorzi i valori sono:
   `divorzi concessi` (il totale), `divorzi concessi dal tribunale`
   (giudiziali), `divorzi consensuali extragiudiziali`. Gli ultimi due
   sommano al primo. Per la serie "totale" filtra sempre
   `Indicatore == 'divorzi concessi'`, altrimenti raddoppi.

La combinazione dei due sbagli produce sovrastime fino a **6x** il valore
reale. Esempi corretti qui sotto.

## Quick start

### Totale divorzi in Italia, anno per anno (pandas)

```python
import pandas as pd

df = pd.read_csv('data/csv/eta-al-divorzio-marito.csv')

# Riga "grand total" per anno: Italia + totale di ogni dimensione.
mask = (
    (df['Territorio'] == 'Italia') &
    (df['Indicatore'] == 'divorzi concessi') &
    (df['Luogo di nascita del marito'] == 'Totale') &
    (df['Luogo di nascita della moglie'] == 'Totale') &
    (df['Luogo di residenza del marito'] == 'Totale') &
    (df['Luogo di residenza della moglie'] == 'Totale') &
    (df['Classe di età del marito al divorzio'] == '15 anni e più') &
    (df['Classe di età della moglie al divorzio'] == '15 anni e più') &
    (df['Classe di età del marito al matrimonio'] == '15 anni e più') &
    (df['Classe di età della moglie al matrimonio'] == '15 anni e più') &
    (df['Anno di matrimonio'] == 'tutte le voci')
)
serie = df[mask].sort_values('TIME_PERIOD').set_index('TIME_PERIOD')['VALUE']
print(serie)
# 2008    54351
# 2009    54456
# ...
# 2022    82596
```

### Distribuzione per regione (2022)

```python
df_2022 = df[
    (df['TIME_PERIOD'] == 2022) &
    (df['Indicatore'] == 'divorzi concessi') &
    (df['Territorio'] != 'Italia') &
    (~df['Territorio'].isin(['Nord-ovest', 'Nord-est', 'Centro', 'Sud', 'Isole'])) &
    (df['Luogo di nascita del marito'] == 'Totale') &
    (df['Luogo di nascita della moglie'] == 'Totale') &
    (df['Luogo di residenza del marito'] == 'Totale') &
    (df['Luogo di residenza della moglie'] == 'Totale') &
    (df['Classe di età del marito al divorzio'] == '15 anni e più') &
    (df['Classe di età della moglie al divorzio'] == '15 anni e più') &
    (df['Classe di età del marito al matrimonio'] == '15 anni e più') &
    (df['Classe di età della moglie al matrimonio'] == '15 anni e più') &
    (df['Anno di matrimonio'] == 'tutte le voci')
]
print(df_2022[['Territorio', 'VALUE']].sort_values('VALUE', ascending=False))
```

### Durata media procedimento di separazione (stdlib, no pandas)

```python
import csv
from pathlib import Path

with Path('data/csv/procedimenti-e-separazioni.csv').open(encoding='utf-8') as fh:
    rows = list(csv.DictReader(fh))

durata_giudiziale = {
    int(r['TIME_PERIOD']): int(r['VALUE'])
    for r in rows
    if r['Territorio'] == 'Italia'
    and r['Indicatore'] == 'durata media del procedimento di separazione giudiziale (in giorni)'
    and r['VALUE']
}
for anno, giorni in sorted(durata_giudiziale.items()):
    print(f'{anno}: {giorni} giorni')
```

### R

```r
df <- read.csv("data/csv/procedimenti-e-separazioni.csv", fileEncoding = "UTF-8")
italia_giud <- subset(df,
  Territorio == "Italia" &
  Indicatore == "durata media del procedimento di separazione giudiziale (in giorni)")
plot(italia_giud$TIME_PERIOD, italia_giud$VALUE, type = "l",
     xlab = "Anno", ylab = "Giorni")
```

### CLI (csvkit)

```bash
# Durata media procedimento giudiziale Italia, ogni anno
csvgrep -c 'Territorio' -m 'Italia' data/csv/procedimenti-e-separazioni.csv \
  | csvgrep -c 'Indicatore' -r 'giudiziale' \
  | csvcut -c 'TIME_PERIOD,VALUE'
```

Installa csvkit con `pip install csvkit`. Vedi anche
[`notebooks/esempio-analisi.ipynb`](notebooks/esempio-analisi.ipynb) per
esempi più ampi.

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
