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
   - `TIME_PERIOD` — l'anno di riferimento;
   - `VALUE` — il valore numerico;
   - `OBS_STATUS` — eventuale flag ISTAT (es. "dato provvisorio",
     "dato non disponibile");
   - `SOURCE` — l'identificativo del dataflow ISTAT (utile per
     separare serie storiche legacy da serie correnti).

## Note sui valori

- I valori nulli o non disponibili sono rappresentati come stringa vuota
  (la colonna `OBS_STATUS` può contenere un flag che chiarisce il
  motivo).
- I codici geografici e di classificazione sono sostituiti con le
  etichette umane ISTAT in italiano (es. "Italia", "15-19 anni",
  "divorzi concessi").
- Il separatore è la virgola (`,`); i testi che contengono virgole sono
  racchiusi tra virgolette secondo RFC 4180.
- Encoding: UTF-8 senza BOM.

## Riproducibilità

La pipeline è deterministica: dato lo stesso contenuto in `data/raw/`, lo
script produce bit-per-bit gli stessi CSV. Non c'è pseudo-random
sampling, nessun join con fonti esterne, nessun arrotondamento oltre
quello già presente nei dati ISTAT.

Per ri-eseguire la pulizia:

```bash
python3 scripts/istat_sdmx_to_csv.py
```

Lo script richiede solo la libreria standard Python 3.9+.

## Aggregazioni e livelli

I CSV sono **cubi multi-dimensionali serializzati**: ogni riga è una
combinazione specifica di valori delle dimensioni. Questo significa che
la stessa cifra compare a più livelli di aggregazione. Due punti critici
per l'analista:

- **`Territorio`** contiene Italia, 5 macroregioni (Nord-ovest, Nord-est,
  Centro, Sud, Isole) e 22 regioni + 2 province autonome. Sommare tutti
  i valori conta lo stesso divorzio 3 volte (Italia + macroregione +
  regione). Per il totale nazionale filtra `Territorio == 'Italia'`.
- **`Indicatore`** per i divorzi include `divorzi concessi` (il totale),
  `divorzi concessi dal tribunale` (giudiziali) e
  `divorzi consensuali extragiudiziali`. Gli ultimi due sommano al
  primo. Per il totale filtra `Indicatore == 'divorzi concessi'`.
- Le altre dimensioni hanno un livello di totale (`Totale`,
  `tutte le voci`, o `15 anni e più` per le classi d'età) che va scelto
  esplicitamente quando si vuole solo la riga aggregata.

## Limiti conosciuti

- **Rotture metodologiche**: ISTAT ha ridefinito diverse serie nel
  tempo. Quando esistono due dataflow sullo stesso tema, il CSV contiene
  entrambi. La colonna `SOURCE` identifica la serie di origine — è
  responsabilità dell'analista decidere se concatenare, confrontare o
  filtrare.
- **Aggiornamento manuale**: i file in `data/raw/` sono scaricati a mano
  dall'interfaccia I.Stat. Un futuro script di update automatico è
  pianificato (vedi `CHANGELOG.md`).
- **Granularità provinciale**: i dataflow inclusi arrivano al livello
  regionale. Per dati a livello provinciale/comunale è necessario
  consultare direttamente I.Stat o le tavole specifiche ISTAT.
