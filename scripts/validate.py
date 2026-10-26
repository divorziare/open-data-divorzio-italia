#!/usr/bin/env python3
"""Sanity checks on the CSVs in data/csv/.

Two kinds of checks:

* structural (always hard failures): expected trailing columns, one row per
  combination of dimensions + year, numeric VALUE, known territory levels;
* accounting identities on count indicators: categories add up to their
  total, territories add up to their parent area, judicial + extrajudicial
  divorces add up to all divorces, and the same national total agrees across
  files.

From reference year 2013 onward ISTAT's published cells do not always add up
exactly: differences of one or two units, most likely from the rounding /
perturbation ISTAT applies to protect confidentiality. Since that noise
accumulates, an identity summing n cells is checked with a tolerance of
TOLERANCE * sqrt(n) units (at least TOLERANCE); anything beyond it is an error,
except the upstream anomalies listed in KNOWN_ANOMALIES.

Usage:
    python3 scripts/validate.py

Exits 1 if any check fails. Requires only Python 3.9+ stdlib.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = REPO_ROOT / "data" / "csv"

TOLERANCE = 2
TRAILING_COLUMNS = ["TIME_PERIOD", "VALUE", "OBS_STATUS", "SOURCE"]
TERRITORY_COLUMNS = ["Territorio", "Codice territorio", "Livello territoriale"]
TERRITORY_LEVELS = {"nazionale", "ripartizione", "regione", "provincia autonoma"}
AUTONOMOUS_PROVINCES_PARENT = {"ITD1": "ITDA", "ITD2": "ITDA"}

# Indicators that count events or people, hence can be summed. Rates, shares
# and average durations are excluded from every accounting identity.
COUNT_INDICATORS = {
    "divorzi concessi",
    "divorzi concessi dal tribunale",
    "divorzi consensuali extragiudiziali",
    "separazioni concesse",
    "numero di separazioni esaurite con rito consensuale",
    "sposi",
    "spose",
}

PETITION_FILE = "coniuge-che-ha-presentato-la-domanda-di-divorzio-con-rito-giudiziale.csv"
PETITION_COL = "Coniuge che ha presentato la domanda di divorzio con rito giudiziale"
HUSBAND_AGE = "Classe di età del marito al divorzio"
WIFE_AGE = "Classe di età della moglie al divorzio"
REMARRIAGE_FILE = "eta-e-durata-del-divorzio.csv"

# (file, column, total label, part labels; None = every other label)
CATEGORY_TOTALS = [
    ("eta-al-divorzio-marito.csv", HUSBAND_AGE, "15 anni e più", None),
    ("eta-al-divorzio-moglie.csv", WIFE_AGE, "15 anni e più", None),
    ("eta-al-divorzio-coniugi.csv", HUSBAND_AGE, "15 anni e più", None),
    ("eta-al-divorzio-coniugi.csv", WIFE_AGE, "15 anni e più", None),
    (PETITION_FILE, PETITION_COL, "totale divorzi aperti con rito giudiziale", ["entrambi", "marito", "moglie"]),
    (REMARRIAGE_FILE, "Età al matrimonio", "16 anni e più", None),
    (REMARRIAGE_FILE, "Anno di cessazione precedente matrimonio", "tutte le voci", None),
]

# (file, {column: total label}): the inner cells of a two-way table add up to
# its grand total. Covers tables whose margins are incomplete, such as the
# remarriage table where "19 anni e più" only exists per "anno e precedenti".
CROSS_TOTALS = [
    ("eta-al-divorzio-coniugi.csv", {HUSBAND_AGE: "15 anni e più", WIFE_AGE: "15 anni e più"}),
    (REMARRIAGE_FILE, {"Anno di cessazione precedente matrimonio": "tutte le voci",
                       "Durata vedovanza/divorzio": "totale"}),
]

# Same national total (per Indicatore and year) in every file:
# (file, filter on the grand-total row).
NATIONAL_TOTALS = [
    ("eta-al-divorzio-marito.csv", {HUSBAND_AGE: "15 anni e più"}),
    ("eta-al-divorzio-moglie.csv", {WIFE_AGE: "15 anni e più"}),
    ("eta-al-divorzio-coniugi.csv", {HUSBAND_AGE: "15 anni e più", WIFE_AGE: "15 anni e più"}),
    (PETITION_FILE, {PETITION_COL: "tutte le voci"}),
]

# Upstream inconsistencies beyond the tolerance, documented in
# docs/methodology.md ("Anomalie note"): reported, but not counted as errors.
# (file, parent territory code, year)
KNOWN_ANOMALIES = {
    # 26 judicial divorces of 2016 are in the Italy total of the DIVORDEMCONG1
    # dataflows but in no region: Campania is 26 short of the DIVFIG1 figure.
    ("eta-al-divorzio-marito.csv", "IT", 2016),
    ("eta-al-divorzio-moglie.csv", "IT", 2016),
}

DIVORCE_TOTAL = "divorzi concessi"
DIVORCE_PARTS = ["divorzi concessi dal tribunale", "divorzi consensuali extragiudiziali"]


class Identity(NamedTuple):
    """One accounting identity: `actual` (sum of n_parts cells) should equal `expected`."""

    where: str
    year: int
    expected: float
    actual: float
    n_parts: int
    known: bool = False

    @property
    def diff(self) -> float:
        return self.actual - self.expected

    @property
    def allowed(self) -> float:
        return max(TOLERANCE, TOLERANCE * math.sqrt(self.n_parts))


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def identity(self, name: str, results: list[Identity]) -> None:
        if not results:
            self.error(f"{name}: no identity could be checked (labels changed?)")
            return
        exact = [r for r in results if r.diff == 0]
        known = [r for r in results if r.diff != 0 and r.known]
        noisy = [r for r in results if r.diff != 0 and not r.known and abs(r.diff) <= r.allowed]
        too_big = [r for r in results if r.diff != 0 and not r.known and abs(r.diff) > r.allowed]
        line = f"  {name}: {len(results)} checked, {len(exact)} exact"
        if noisy:
            years = sorted({r.year for r in noisy})
            line += (f", {len(noisy)} within tolerance (years {years[0]}-{years[-1]},"
                     f" max |diff| {max(abs(r.diff) for r in noisy):g})")
        if known:
            line += f", {len(known)} known anomalies (max |diff| {max(abs(r.diff) for r in known):g})"
        print(line)
        for r in too_big[:10]:
            self.error(f"{name}: {r.where} {r.year}: expected {r.expected:g}, got {r.actual:g}"
                       f" (diff {r.diff:+g}, allowed ±{r.allowed:.1f})")
        if len(too_big) > 10:
            self.error(f"{name}: ... and {len(too_big) - 10} more")


def load(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (CSV_DIR / name).open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def dims_of(header: list[str]) -> list[str]:
    return header[: header.index("TIME_PERIOD")]


def check_structure(name: str, header: list[str], rows: list[dict[str, str]], report: Report) -> None:
    if header[-len(TRAILING_COLUMNS):] != TRAILING_COLUMNS:
        report.error(f"{name}: header must end with {TRAILING_COLUMNS}, got {header[-4:]}")
        return
    dims = dims_of(header)
    seen: set[tuple[str, ...]] = set()
    for i, r in enumerate(rows, start=2):
        key = tuple(r[c] for c in dims) + (r["TIME_PERIOD"],)
        if key in seen:
            report.error(f"{name}:{i}: duplicate row for {key}")
        seen.add(key)
        if not (r["TIME_PERIOD"].isdigit() and len(r["TIME_PERIOD"]) == 4):
            report.error(f"{name}:{i}: TIME_PERIOD {r['TIME_PERIOD']!r} is not a year")
        try:
            float(r["VALUE"])
        except ValueError:
            if r["VALUE"] or not r["OBS_STATUS"]:
                report.error(f"{name}:{i}: VALUE {r['VALUE']!r} is not numeric")
        if "Livello territoriale" in r and r["Livello territoriale"] not in TERRITORY_LEVELS:
            report.error(f"{name}:{i}: unknown territory level {r['Livello territoriale']!r}")


def count_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [r for r in rows if r["Indicatore"] in COUNT_INDICATORS and r["VALUE"]]


def group(rows: list[dict[str, str]], key_cols: list[str], by: str) -> dict[tuple, dict[str, float]]:
    """{key (without `by`) + year: {value of `by`: VALUE}}"""
    out: dict[tuple, dict[str, float]] = defaultdict(dict)
    for r in rows:
        k = tuple(r[c] for c in key_cols if c != by) + (r["TIME_PERIOD"],)
        out[k][r[by]] = float(r["VALUE"])
    return out


def check_category_totals(files: dict, report: Report) -> None:
    for name, col, total, parts in CATEGORY_TOTALS:
        header, rows = files[name]
        results = []
        for k, cells in group(count_rows(rows), dims_of(header), col).items():
            present = [v for label, v in cells.items() if label != total and (parts is None or label in parts)]
            if total in cells and present:
                results.append(Identity(" / ".join(k[:-1]), int(k[-1]), cells[total], sum(present), len(present)))
        report.identity(f"{name} [{col}] parts == '{total}'", results)


def check_cross_totals(files: dict, report: Report) -> None:
    for name, totals in CROSS_TOTALS:
        header, rows = files[name]
        other = [c for c in dims_of(header) if c not in totals]
        grand: dict[tuple, float] = {}
        inner: dict[tuple, float] = defaultdict(float)
        n_inner: dict[tuple, int] = defaultdict(int)
        for r in count_rows(rows):
            k = tuple(r[c] for c in other) + (r["TIME_PERIOD"],)
            flags = [r[c] == t for c, t in totals.items()]
            if all(flags):
                grand[k] = float(r["VALUE"])
            elif not any(flags):
                inner[k] += float(r["VALUE"])
                n_inner[k] += 1
        results = [Identity(" / ".join(k[:-1]), int(k[-1]), v, inner[k], n_inner[k])
                   for k, v in grand.items() if k in inner]
        report.identity(f"{name} inner cells == grand total", results)


def territory_parent(code: str) -> str | None:
    if code == "IT":
        return None
    if code in AUTONOMOUS_PROVINCES_PARENT:
        return AUTONOMOUS_PROVINCES_PARENT[code]
    return "IT" if len(code) == 3 else code[:3]


def check_territories(files: dict, report: Report) -> None:
    for name, (header, rows) in files.items():
        if "Codice territorio" not in header:
            continue
        key_cols = [c for c in dims_of(header) if c not in ("Territorio", "Livello territoriale")]
        results = []
        for k, cells in group(count_rows(rows), key_cols, "Codice territorio").items():
            children: dict[str, list[float]] = defaultdict(list)
            for code, v in cells.items():
                parent = territory_parent(code)
                if parent is not None:
                    children[parent].append(v)
            for parent, values in children.items():
                if parent in cells:
                    year = int(k[-1])
                    results.append(Identity(f"{parent} / " + " / ".join(k[:-1]), year, cells[parent], sum(values),
                                            len(values), (name, parent, year) in KNOWN_ANOMALIES))
        if results:
            report.identity(f"{name} sub-areas == parent area", results)


def check_divorce_split(files: dict, report: Report) -> None:
    for name, (header, rows) in files.items():
        if "Indicatore" not in header:
            continue
        results = []
        for k, cells in group(count_rows(rows), dims_of(header), "Indicatore").items():
            if DIVORCE_TOTAL in cells and all(p in cells for p in DIVORCE_PARTS):
                results.append(Identity(" / ".join(k[:-1]), int(k[-1]), cells[DIVORCE_TOTAL],
                                        sum(cells[p] for p in DIVORCE_PARTS), len(DIVORCE_PARTS)))
        if results:
            report.identity(f"{name} tribunale + extragiudiziali == totale", results)


def check_national_totals(files: dict, report: Report) -> None:
    by_key: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for name, flt in NATIONAL_TOTALS:
        _, rows = files[name]
        for r in count_rows(rows):
            if r.get("Codice territorio") != "IT" or any(r[c] != v for c, v in flt.items()):
                continue
            k = (r["Indicatore"], r["TIME_PERIOD"])
            if name in by_key[k]:
                report.error(f"{name}: several national grand-total rows for {k}")
            by_key[k][name] = float(r["VALUE"])
    results = []
    for (indicator, year), values in sorted(by_key.items()):
        reference = values.get(NATIONAL_TOTALS[0][0])
        for name, v in values.items():
            if reference is not None and name != NATIONAL_TOTALS[0][0]:
                results.append(Identity(f"{indicator} in {name}", int(year), reference, v, 1))
    report.identity("national totals agree across files", results)


def main() -> int:
    files = {p.name: load(p.name) for p in sorted(CSV_DIR.glob("*.csv"))}
    if not files:
        print(f"No CSV files in {CSV_DIR}", file=sys.stderr)
        return 1
    report = Report()

    print("Structure")
    for name, (header, rows) in files.items():
        check_structure(name, header, rows, report)
        print(f"  {name}: {len(rows):,} rows, {len(header)} columns")

    print(f"Accounting identities (tolerance ±{TOLERANCE}·√n for a sum of n cells)")
    check_category_totals(files, report)
    check_cross_totals(files, report)
    check_territories(files, report)
    check_divorce_split(files, report)
    check_national_totals(files, report)

    if report.errors:
        print(f"\n{len(report.errors)} error(s):", file=sys.stderr)
        for e in report.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
