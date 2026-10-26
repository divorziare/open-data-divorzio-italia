# Metodologia di pulizia

## Formato originale (SDMX-JSON)

ISTAT pubblica i dati in formato **SDMX-JSON** — uno standard
internazionale per lo scambio di dati statistici. Il JSON è
multi-dimensionale:

- ogni cella è identificata da una combinazione di dimensioni
  (es. *territorio*, *età*, *indicatore*) + un periodo temporale;
- le *serie* sono raggruppate in un cubo; ogni chiave di serie è
  una stringa di indici separati da `:` che puntano ai valori di
  ciascuna dimensione;
- i valori delle dimensioni e delle etichette umane sono in un blocco
  separato (`structure.dimensions`).

Questo formato è pensato per macchine, non per giornalisti: leggerlo a
mano è praticamente impossibile.

## Trasformazione

`scripts/istat_sdmx_to_csv.py` appiattisce il cubo in un formato *tidy*
(una riga per osservazione):

1. Parsa il file SDMX-JSON.
2. Per ogni *serie*, risolve gli indici delle dimensioni nelle etichette
   umane italiane.
3. Per ogni *osservazione* nella serie, emette una riga CSV composta da:
   - una colonna per ogni dimensione della serie (es. *Territorio*,
     *Classe di età*);
   - subito dopo `Territorio`, due colonne derivate dal codice ISTAT
     dell'area: `Codice territorio` (es. `ITC4`) e `Livello territoriale`
     (vedi [Aggregazioni e livelli](#aggregazioni-e-livelli));
   - `TIME_PERIOD` — l'anno di riferimento;
   - `VALUE` — il valore numerico;
   - `OBS_STATUS` — eventuale flag ISTAT (es. "dato provvisorio",
     "dato non disponibile");
   - `SOURCE` — l'identificativo del dataflow ISTAT (utile per
     separare serie storiche legacy da serie correnti).
4. I dataflow con lo stesso nome (serie legacy + serie corrente) finiscono
   nello stesso CSV.

## Note sui valori

- I valori nulli o non disponibili sono rappresentati come stringa vuota
  (la colonna `OBS_STATUS` può contenere un flag che chiarisce il
  motivo). Nei dati attuali non ci sono valori mancanti e ISTAT non
  valorizza mai `OBS_STATUS`, che quindi è sempre vuota.
- I codici geografici e di classificazione sono sostituiti con le
  etichette umane ISTAT in italiano (es. "Italia", "15-19 anni",
  "divorzi concessi"); il solo codice conservato è `Codice territorio`.
- Il separatore è la virgola (`,`); i testi che contengono virgole sono
  racchiusi tra virgolette e le righe terminano con CRLF, secondo
  RFC 4180.
- Encoding: UTF-8 senza BOM.
- I decimali usano il punto (es. `86.3`) e compaiono solo nei tassi e
  nelle percentuali di `procedimenti-e-separazioni.csv`.

## Riproducibilità

La pipeline è deterministica: dato lo stesso contenuto in `data/raw/`, lo
script produce bit-per-bit gli stessi CSV. Non c'è pseudo-random
sampling, nessun join con fonti esterne, nessun arrotondamento oltre
quello già presente nei dati ISTAT. La CI di GitHub lo verifica ad ogni
push: rigenera i CSV e fallisce se differiscono da quelli committati.

Per ri-eseguire la pulizia:

```bash
python3 scripts/istat_sdmx_to_csv.py
```

Lo script richiede solo la libreria standard Python 3.9+.

## Aggregazioni e livelli

I CSV sono **cubi multi-dimensionali serializzati**: ogni riga è una
combinazione specifica di valori delle dimensioni. Questo significa che
la stessa cifra compare a più livelli di aggregazione.

### Territorio

| `Livello territoriale` | Aree | Codici |
|---|---|---|
| `nazionale` | Italia | `IT` |
| `ripartizione` | Nord-ovest, Nord-est, Centro, Sud, Isole | `ITC`, `ITD`, `ITE`, `ITF`, `ITG` |
| `regione` | le 20 regioni, Trentino-Alto Adige compreso | `ITC1` … `ITG2`, `ITDA` |
| `provincia autonoma` | Bolzano/Bozen, Trento | `ITD1`, `ITD2` |

- Le regioni sommano alla loro ripartizione, le ripartizioni sommano
  all'Italia, e Bolzano + Trento = Trentino-Alto Adige (`ITDA`).
- Sommare tutte le righe conta ogni divorzio almeno 3 volte (Italia +
  ripartizione + regione) e quelli del Trentino-Alto Adige 4 volte.
  Filtra sempre un solo livello.
- I codici sono quelli ISTAT, basati sulla vecchia classificazione
  europea NUTS 2006. Per unire i dati a una cartografia NUTS recente (es.
  Eurostat NUTS 2021) sostituisci il prefisso `ITD` con `ITH` e `ITE` con
  `ITI` (es. Veneto `ITD3` → `ITH3`, Lazio `ITE4` → `ITI4`). `ITDA` non
  esiste in NUTS, dove le unità di livello 2 sono le due province
  autonome.

### Indicatore e altre dimensioni

- **`Indicatore`** per i divorzi include `divorzi concessi` (il totale),
  `divorzi concessi dal tribunale` e `divorzi consensuali
  extragiudiziali`. Gli ultimi due sommano al primo. Per il totale filtra
  `Indicatore == 'divorzi concessi'` (ma vedi l'eccezione del file
  `coniuge-che-ha-presentato-…` in [`sources.md`](sources.md)).
- Le altre dimensioni hanno un livello di totale (`Totale`,
  `tutte le voci`, `totale`, o `15 anni e più` / `16 anni e più` per le
  classi d'età) che va scelto esplicitamente quando si vuole solo la riga
  aggregata.
- Molte dimensioni hanno un solo valore in tutto il file (sono fissate al
  totale nell'estrazione ISTAT): si possono ignorare, ma filtrarle non fa
  danni e protegge da future estrazioni più dettagliate.

## Additività e piccole discrepanze

Fino al 2012 tutte le somme tornano esattamente. **Dal 2013** i valori
pubblicati da ISTAT non sono perfettamente additivi: sommando le parti si
ottiene il totale pubblicato ±1–2 unità. È il comportamento tipico delle
tecniche di arrotondamento/perturbazione con cui gli istituti di
statistica tutelano la riservatezza nelle tabelle; ISTAT non lo documenta
nei metadati del dataflow.

| Identità | Scarto massimo |
|---|---|
| classi d'età → `15 anni e più` | ±3 |
| regioni → ripartizione → Italia (escluso il caso sotto) | ±2 |
| `dal tribunale` + `extragiudiziali` → `divorzi concessi` | ±1 |
| `marito` + `moglie` + `entrambi` → totale giudiziale | ±1 |
| 81 celle interne età × età → totale (file `coniugi`) | ±7 |
| totale nazionale, stesso indicatore e anno, tra file diversi | 0 |
| file `eta-e-durata-del-divorzio.csv` (tutte le identità) | 0 |
| conteggi di `procedimenti-e-separazioni.csv` | 0 |

Conseguenza pratica: **usa sempre il totale pubblicato** invece di
ricalcolarlo sommando le parti, e non sorprenderti se una quota calcolata
non somma esattamente a 100%.

## Anomalie note

- **Campania, 2016, file `eta-al-divorzio-marito.csv` e
  `eta-al-divorzio-moglie.csv`**: 26 divorzi giudiziali compaiono nel
  totale Italia ma in nessuna regione. Nei dataflow `DIVORDEMCONG1_5` e
  `DIVORDEMCONG1_6` la Campania ha 4.643 divorzi concessi dal tribunale,
  nel dataflow `DIVFIG1_8` (file `coniuge-che-ha-presentato-…`) 4.669;
  di conseguenza Sud e la somma delle regioni sono più bassi di 26 unità
  rispetto all'Italia (99.071 divorzi concessi). Il totale nazionale
  coincide in tutti i file. È un'incoerenza a monte, da segnalare a
  ISTAT; i CSV riportano i valori così come pubblicati.

## Validazione

`scripts/validate.py` verifica:

- la struttura: colonne finali attese, nessuna riga duplicata per
  combinazione di dimensioni + anno, `VALUE` numerico, `TIME_PERIOD`
  a 4 cifre, livelli territoriali noti;
- tutte le identità della tabella sopra, solo sugli indicatori di
  conteggio (tassi, percentuali e durate medie non sono sommabili).

Una somma di *n* celle è accettata se differisce dal totale al massimo di
2·√*n* unità (minimo 2): la tolleranza cresce con il numero di celle
perché le piccole discrepanze si accumulano. Le anomalie note sono
elencate in `KNOWN_ANOMALIES` nello script e riportate senza far
fallire la validazione; qualunque altra violazione la fa fallire.

## Limiti conosciuti

- **Rotture metodologiche**: ISTAT ha ridefinito diverse serie nel
  tempo. Quando esistono due dataflow sullo stesso tema, il CSV contiene
  entrambi. La colonna `SOURCE` identifica la serie di origine — è
  responsabilità dell'analista decidere se concatenare, confrontare o
  filtrare. In tutti i file la frattura è tra 2014 e 2015 (vedi
  [`sources.md`](sources.md)).
- **Aggiornamento manuale**: i file in `data/raw/` sono scaricati a mano
  dall'interfaccia I.Stat. Un futuro script di update automatico è
  pianificato.
- **Granularità provinciale**: i dataflow inclusi arrivano al livello
  regionale (più le due province autonome). Per dati a livello
  provinciale/comunale è necessario consultare direttamente I.Stat o le
  tavole specifiche ISTAT.
