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

| File | Di cosa parla | Anni | Territorio | Righe |
|---|---|---|---|---|
| [`eta-al-divorzio-coniugi.csv`](data/csv/eta-al-divorzio-coniugi.csv) | Divorzi per classe d'età del marito × classe d'età della moglie (tabella incrociata) | 2008–2022 | solo Italia | 3.100 |
| [`eta-al-divorzio-marito.csv`](data/csv/eta-al-divorzio-marito.csv) | Divorzi per classe d'età del marito | 2008–2022 | Italia, ripartizioni, regioni | 8.680 |
| [`eta-al-divorzio-moglie.csv`](data/csv/eta-al-divorzio-moglie.csv) | Divorzi per classe d'età della moglie | 2008–2022 | Italia, ripartizioni, regioni | 8.680 |
| [`eta-e-durata-del-divorzio.csv`](data/csv/eta-e-durata-del-divorzio.csv) | Divorziati e divorziate che si risposano: età al nuovo matrimonio, anno di fine del matrimonio precedente, anni trascorsi da allora | 2015–2024 | solo Italia | 15.340 |
| [`coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv`](data/csv/coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv) | Divorzi con rito giudiziale per coniuge che ha presentato la domanda (marito, moglie, entrambi) | 2008–2022 | Italia, ripartizioni, regioni | 2.100 |
| [`procedimenti-e-separazioni.csv`](data/csv/procedimenti-e-separazioni.csv) | Separazioni: numero (fino al 2014), tassi e durata media dei procedimenti | 2007–2022 | Italia, ripartizioni, regioni | 2.912 |

"Regioni" comprende anche le province autonome di Bolzano e Trento. I file
sono in `data/csv/`. Il dettaglio di dataflow, indicatori e copertura è in
[`docs/sources.md`](docs/sources.md).

Tutti i CSV hanno la stessa struttura di base:

- una colonna per ogni **dimensione** della serie (territorio, classe
  d'età, stato civile, …) — in italiano;
- dove c'è il territorio, due colonne derivate subito dopo `Territorio`:
  - `Codice territorio` — codice ISTAT dell'area (`IT`, `ITC`, `ITC1`, …);
  - `Livello territoriale` — `nazionale`, `ripartizione`, `regione` o
    `provincia autonoma`;
- `TIME_PERIOD` — l'anno;
- `VALUE` — il valore numerico;
- `OBS_STATUS` — flag ISTAT sull'osservazione (es. provvisorio); nei dati
  attuali ISTAT non lo valorizza mai, quindi è sempre vuoto;
- `SOURCE` — identificativo del dataflow ISTAT (permette di separare
  serie storiche legacy da serie correnti — vedi
  [`docs/sources.md`](docs/sources.md)).

Molte colonne hanno un solo valore in tutto il file (es. `Frequenza` è
sempre `annuale`, `Luogo di nascita del marito` sempre `Totale`): sono
dimensioni del cubo ISTAT fissate al totale nell'estrazione.

### Avvisi prima di usare i dati

1. **`Territorio` non è sempre `Italia`**. I file territoriali includono
   l'Italia, 5 ripartizioni (Nord-ovest, Nord-est, Centro, Sud, Isole), 20
   regioni e le 2 province autonome di Bolzano e Trento. Sommare tutto
   conta ogni divorzio almeno 3 volte, e il Trentino-Alto Adige 4 volte
   (regione + le sue due province). Filtra sempre per `Livello
   territoriale`: `nazionale` per il totale, `regione` per le 20 regioni
   (che sommano all'Italia), `provincia autonoma` solo se ti servono
   Bolzano e Trento separate.

2. **`Indicatore` è spesso decomposto**. Per i divorzi i valori sono:
   `divorzi concessi` (il totale), `divorzi concessi dal tribunale`
   (giudiziali), `divorzi consensuali extragiudiziali`. Gli ultimi due
   sommano al primo. Per la serie "totale" filtra sempre
   `Indicatore == 'divorzi concessi'`, altrimenti raddoppi. **Eccezione**:
   nel file `coniuge-che-ha-presentato-…` l'indicatore è `divorzi
   concessi` fino al 2014 e `divorzi concessi dal tribunale` dal 2015;
   filtrando su `divorzi concessi` perdi gli anni 2015–2022.

3. **Le somme tornano a meno di 1–2 unità**. Dal 2013 i valori pubblicati
   da ISTAT non sono perfettamente additivi: sommando le classi d'età, le
   regioni o i due tipi di divorzio si ottiene il totale ±1–2 (fino a ±7
   sommando le 81 celle interne della tabella incrociata età × età). Usa
   sempre il totale pubblicato invece di ricalcolarlo. C'è anche
   un'anomalia più grande nel 2016, documentata in
   [`docs/methodology.md`](docs/methodology.md#anomalie-note).

4. **Il 2015 è una rottura di serie**. Cambia il dataflow ISTAT (colonna
   `SOURCE`) e, soprattutto, cambia la legge: dal 2015 si contano i
   divorzi extragiudiziali (DL 132/2014) ed entra in vigore il «divorzio
   breve» (L. 55/2015). Il passaggio da 52 mila divorzi nel 2014 a 82 mila
   nel 2015 riflette queste riforme. Per le separazioni, il numero
   assoluto è disponibile solo fino al 2014; dal 2015 ci sono solo tassi e
   durate.

La combinazione dei primi due sbagli produce sovrastime fino a **6x** il
valore reale. Esempi corretti qui sotto.

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

`Livello territoriale == 'regione'` restituisce le 20 regioni, che sommano
al totale Italia. Escludere solo Italia e ripartizioni non basta: restano
anche Bolzano e Trento, e il Trentino-Alto Adige viene contato due volte.

```python
df_2022 = df[
    (df['TIME_PERIOD'] == 2022) &
    (df['Indicatore'] == 'divorzi concessi') &
    (df['Livello territoriale'] == 'regione') &
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
print(df_2022[['Territorio', 'Codice territorio', 'VALUE']].sort_values('VALUE', ascending=False))
assert df_2022['VALUE'].sum() == 82596  # = totale Italia 2022
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
csvgrep -c 'Livello territoriale' -m 'nazionale' data/csv/procedimenti-e-separazioni.csv \
  | csvgrep -c 'Indicatore' -m 'separazione giudiziale' \
  | csvcut -c 'TIME_PERIOD,VALUE'
```

`-m` cerca una sottostringa: `-r 'giudiziale'` catturerebbe anche la
durata della separazione consensuale *extra*giudiziale, mescolando due
serie.

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

## Validare i dati

```bash
python3 scripts/validate.py
```

Controlla la struttura dei CSV (nessuna riga duplicata, valori numerici,
livelli territoriali noti) e circa 20.000 identità contabili: classi
d'età che sommano al totale, regioni che sommano alla ripartizione e
all'Italia, giudiziali + extragiudiziali = totale, stesso totale nazionale
in tutti i file. Le piccole discrepanze dovute a ISTAT sono tollerate e
riportate; tutto il resto fa fallire lo script.

Ad ogni push e pull request la CI di GitHub
([`.github/workflows/validate.yml`](.github/workflows/validate.yml))
rigenera i CSV da `data/raw/`, verifica che coincidano con quelli
committati ed esegue la validazione.

## Aggiornamenti

ISTAT aggiorna le serie annualmente (di solito nel quarto trimestre).
Quando escono nuovi dati:

1. Scaricare il JSON aggiornato da
   [esploradati.istat.it](https://esploradati.istat.it).
2. Sostituire il file in `data/raw/`.
3. Eseguire `python3 scripts/istat_sdmx_to_csv.py`.
4. Eseguire `python3 scripts/validate.py`.
5. Aprire una PR con diff dei CSV.

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
