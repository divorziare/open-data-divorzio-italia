# Fonti ISTAT — Provenienza dei dataset

Tutti i dati in questo repository sono estratti dal portale **I.Stat**
([esploradati.istat.it](https://esploradati.istat.it)) via la API
SDMX-JSON ufficiale. Ogni richiesta è associata a un *dataflow* con
identificativo stabile, che abbiamo conservato nella colonna `SOURCE` di
ogni CSV.

## Mappa CSV → dataflow ISTAT

| CSV | Dataflow | Anni | Ultimo aggiornamento ISTAT | Granularità territoriale |
|---|---|---|---|---|
| `eta-al-divorzio-coniugi.csv` | `27_385_DF_DCIS_DIVORDEMCONG_4` | 2008–2014 | 2022-07-26 | solo Italia |
| | `27_470_DF_DCIS_DIVORDEMCONG1_4` | 2015–2022 | 2025-02-24 | solo Italia |
| `eta-al-divorzio-marito.csv` | `27_385_DF_DCIS_DIVORDEMCONG_5` | 2008–2014 | 2022-07-26 | Italia, ripartizioni, regioni, PA |
| | `27_470_DF_DCIS_DIVORDEMCONG1_5` | 2015–2022 | 2025-02-24 | Italia, ripartizioni, regioni, PA |
| `eta-al-divorzio-moglie.csv` | `27_385_DF_DCIS_DIVORDEMCONG_6` | 2008–2014 | 2022-07-26 | Italia, ripartizioni, regioni, PA |
| | `27_470_DF_DCIS_DIVORDEMCONG1_6` | 2015–2022 | 2025-02-24 | Italia, ripartizioni, regioni, PA |
| `eta-e-durata-del-divorzio.csv` | `24_447_DF_DCIS_SPOSI_3` | 2015–2024 | 2026-01-19 | solo Italia |
| `coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv` | `27_814_DF_DCIS_DIVFIG_10` | 2008–2014 | 2022-07-27 | Italia, ripartizioni, regioni, PA |
| | `27_945_DF_DCIS_DIVFIG1_8` | 2015–2022 | 2025-02-24 | Italia, ripartizioni, regioni, PA |
| `procedimenti-e-separazioni.csv` | `27_349_DF_DCIS_SEPARAZIND_1` | 2007–2014 | 2022-02-28 | Italia, ripartizioni, regioni, PA |
| | `27_474_DF_DCIS_SEPARAZIND1_1` | 2015–2022 | 2025-02-24 | Italia, ripartizioni, regioni, PA |

I file in `data/raw/` sono stati estratti il 31/03/2026 (campo
`meta.prepared` dei JSON); l'ultimo aggiornamento ISTAT è l'annotazione
`LAST_UPDATE` di ciascun dataflow. "Regioni, PA" = 20 regioni più le
province autonome di Bolzano e Trento (vedi
[`methodology.md`](methodology.md#aggregazioni-e-livelli)).

## Indicatori e dimensioni per file

### Età al divorzio (`marito`, `moglie`, `coniugi`)

- `Indicatore`: `divorzi concessi` (totale). Dal 2015 anche `divorzi
  concessi dal tribunale` e `divorzi consensuali extragiudiziali`, che
  sommano al totale (a meno di ±1 unità).
- Classi d'età al divorzio: `15-24 anni`, `25-29 anni`, … `55-59 anni`,
  `60 anni e più`; il totale è `15 anni e più`.
- `marito` e `moglie` variano solo l'età del rispettivo coniuge;
  `coniugi` incrocia le due età (10 × 10 celle per anno e indicatore,
  totali compresi), ma solo a livello nazionale.

### `coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv`

- `Indicatore`: `divorzi concessi` nel dataflow 2008–2014, `divorzi
  concessi dal tribunale` nel dataflow 2015–2022. I divorzi
  extragiudiziali sono stati introdotti solo a fine 2014, quindi le due
  serie si possono accostare con cautela; un filtro su un solo valore di
  `Indicatore`, però, taglia metà degli anni.
- Valori del richiedente:
  - `tutte le voci` — tutti i divorzi dell'indicatore, consensuali
    compresi;
  - `totale divorzi aperti con rito giudiziale` — solo quelli con rito
    giudiziale (contenzioso);
  - `marito`, `moglie`, `entrambi` — scompongono il precedente (sommano
    al totale giudiziale a meno di ±1 unità).
- `Età dei figli affidati` vale `totale` nel primo dataflow e `fino a 17
  anni` nel secondo: è un'etichetta diversa per la stessa dimensione non
  disaggregata (`Con figli affidati` è `totale` in entrambi).

### `procedimenti-e-separazioni.csv`

Nove indicatori, non tutti presenti in entrambi i dataflow:

| Indicatore | Anni |
|---|---|
| `separazioni concesse` | 2007–2014 |
| `numero di separazioni esaurite con rito consensuale` | 2007–2014 |
| `separazioni esaurite con rito consensuale (valori percentuali)` | 2007–2014 |
| `separazioni concesse rispetto ai coniugati (valori per centomila)` | 2007–2022 |
| `tasso di separazione rispetto agli abitanti (valori per mille)` | 2007–2022 |
| `durata media del procedimento di separazione giudiziale (in giorni)` | 2007–2022 |
| `durata media del procedimento di separazione consensuale (in giorni)` | 2007–2022 |
| `durata media del procedimento di separazione consensuale in tribunale (in giorni)` | 2015–2022 |
| `durata media del procedimento di separazione consensuale extragiudiziale (in giorni)` | 2015–2022 |

Solo i primi due sono conteggi sommabili; gli altri sono tassi, quote o
medie e non vanno mai sommati tra territori. Dal 2015 la durata media
della separazione consensuale comprende anche le separazioni
extragiudiziali, molto più rapide: in ogni territorio e anno il valore sta
tra la durata in tribunale e quella extragiudiziale. Il calo rispetto al
2014 quindi non indica solo tribunali più veloci.

### `eta-e-durata-del-divorzio.csv`

Nonostante il nome (quello del dataflow ISTAT), il file non riguarda la
durata dei matrimoni finiti in divorzio: conta **le persone divorziate
che si risposano**, nell'anno del nuovo matrimonio (`TIME_PERIOD`).

- `Indicatore`: `sposi` (uomini) e `spose` (donne).
- `Età al matrimonio`: età al nuovo matrimonio; il totale è `16 anni e
  più`.
- `Anno di cessazione precedente matrimonio`: anno in cui è finito il
  matrimonio precedente; `tutte le voci` è il totale. Le voci `AAAA e
  precedenti` raccolgono gli anni più vecchi e compaiono solo insieme alla
  durata `19 anni e più`.
- `Durata vedovanza/divorzio`: anni trascorsi tra la fine del matrimonio
  precedente e il nuovo matrimonio; il totale è `totale`.
- Le celle anno di cessazione × durata formano un diagramma di Lexis: per
  ogni anno di matrimonio sommano esattamente al totale. Non esiste invece
  la riga `tutte le voci` × `19 anni e più`, quindi sommare le durate da 0
  a 18 anni non restituisce il totale.
- `Stato civile` è sempre `divorziata/o`. Nota ISTAT allegata alla serie:
  *"Tra i divorziati e le divorziate sono compresi i «già coniugati», cioè
  le persone che hanno ottenuto lo scioglimento del matrimonio ai sensi
  della legge 1 dicembre 1970 n. 888. Nel caso in cui non compaia in
  maniera esplicita la voce «già in unione civile (per scioglimento
  unione)», questo stato civile è compreso nella voce «divorziata/o»."*

## Perché alcuni temi compaiono in due dataflow

ISTAT periodicamente ridisegna le serie statistiche per adeguarsi a
nuove classificazioni o per coprire rotture metodologiche. In questi
casi pubblica:

- una serie **storica legacy** (es. `DIVORDEMCONG_4`), che copre gli
  anni più vecchi ma non viene più aggiornata;
- una serie **corrente** (es. `DIVORDEMCONG1_4`), che parte da un
  anno di riferimento più recente e prosegue con la metodologia nuova.

Per tutti i temi di questo repository la frattura cade tra il 2014 e il
2015, in corrispondenza dell'introduzione dei divorzi e delle separazioni
extragiudiziali (DL 132/2014, convertito dalla L. 162/2014) e del
«divorzio breve» (L. 55/2015). Le due serie non si sovrappongono: nessun
anno compare in entrambe.

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
4. Eseguire `python3 scripts/validate.py`.
5. Verificare il diff sul CSV generato.

## Licenza originale ISTAT

ISTAT rilascia i propri dati sotto licenza Creative Commons Attribution
4.0 ([note legali ISTAT](https://www.istat.it/it/note-legali)). Questo
repository eredita la stessa licenza per la componente dati; vedere
`LICENSE` per il testo completo e l'attribuzione richiesta.
