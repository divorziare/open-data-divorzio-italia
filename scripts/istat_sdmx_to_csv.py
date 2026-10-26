#!/usr/bin/env python3
"""Convert ISTAT SDMX-JSON files to flat CSV.

ISTAT (Istituto Nazionale di Statistica) publishes data via SDMX-JSON on
the i.stat portal (esploradati.istat.it). Each response contains a
multi-dimensional cube where series are keyed by a colon-joined string of
dimension indices (e.g. "0:0:3:2"), and each series holds observations
keyed by a time-period index. This script flattens that structure into
tidy CSV rows with human-readable dimension labels.

Usage:
    python3 scripts/istat_sdmx_to_csv.py

Reads every `*.json` in `data/raw/` and writes one `.csv` per dataset name in
`data/csv/`. Column order is: all series dimensions (by name), TIME_PERIOD,
VALUE, OBS_STATUS, SOURCE. The territory dimension is followed by two derived
columns, `Codice territorio` (the ISTAT area code) and `Livello territoriale`
(nazionale, ripartizione, regione, provincia autonoma).

Requires only Python 3.9+ stdlib.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
CSV_DIR = REPO_ROOT / "data" / "csv"


def slugify(name: str) -> str:
    """Turn a human-readable dataset name into a short filename-safe slug."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\([^)]*\)", "", s)
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def build_index_maps(structure: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Return (series_dims, obs_dims). Each dim is a list of {id, name, values}."""
    series_dims = structure["dimensions"].get("series", [])
    obs_dims = structure["dimensions"].get("observation", [])
    return series_dims, obs_dims


def obs_status_label(obs_value: list, attrs_spec: list[dict]) -> str:
    """Resolve the OBS_STATUS attribute of one observation to its human label.

    An observation is `[value, attr_0, attr_1, ...]`, where `attr_i` indexes the
    values of the i-th entry of `structure.attributes.observation`.
    """
    for pos, a in enumerate(attrs_spec):
        if a.get("id") != "OBS_STATUS":
            continue
        if len(obs_value) <= pos + 1 or obs_value[pos + 1] is None:
            return ""
        try:
            return a["values"][int(obs_value[pos + 1])].get("name", "")
        except (ValueError, IndexError, KeyError):
            return ""
    return ""


TERRITORY_DIM = "REF_AREA"
TERRITORY_EXTRA_COLUMNS = ["Codice territorio", "Livello territoriale"]
# Bolzano/Bozen and Trento: together they make up Trentino-Alto Adige (ITDA),
# so they must never be summed with it.
AUTONOMOUS_PROVINCES = {"ITD1", "ITD2"}


def territory_level(code: str) -> str:
    """Classify an ISTAT REF_AREA code (NUTS 2006-based: ITD = Nord-est, ITE = Centro)."""
    if code == "IT":
        return "nazionale"
    if code in AUTONOMOUS_PROVINCES:
        return "provincia autonoma"
    if re.fullmatch(r"IT[A-Z]", code):
        return "ripartizione"
    if re.fullmatch(r"IT[A-Z][0-9A-Z]", code):
        return "regione"
    raise ValueError(f"Unknown territory code {code!r}: extend territory_level()")


DATAFLOW_RE = re.compile(r"\(IT1,([^)]+)\)")


def extract_dataflow_id(filename: str) -> str:
    """Pull the SDMX dataflow id from ISTAT's filename convention.

    Example: 'Età al divorzio - marito (IT1,27_470_DF_DCIS_DIVORDEMCONG1_5,1.0).json'
    → '27_470_DF_DCIS_DIVORDEMCONG1_5'
    """
    m = DATAFLOW_RE.search(filename)
    if not m:
        return Path(filename).stem
    parts = m.group(1).split(",")
    return parts[0] if parts else Path(filename).stem


def parse(path: Path) -> tuple[str, list[str], list[list[str]]]:
    """Parse one SDMX-JSON file into (dataset_name, header, rows)."""
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)

    structure = payload["data"]["structure"]
    datasets = payload["data"]["dataSets"]
    if not datasets:
        raise ValueError(f"No dataSets in {path.name}")
    dataset = datasets[0]

    series_dims, obs_dims = build_index_maps(structure)
    obs_attrs_spec = structure.get("attributes", {}).get("observation", [])
    if not obs_dims:
        raise ValueError(f"No observation dimensions in {path.name}")
    time_dim = obs_dims[0]
    time_values = [v.get("id", "") for v in time_dim["values"]]

    header: list[str] = []
    for d in series_dims:
        header.append(d["name"])
        if d["id"] == TERRITORY_DIM:
            header.extend(TERRITORY_EXTRA_COLUMNS)
    header += ["TIME_PERIOD", "VALUE", "OBS_STATUS"]
    dataflow_id = extract_dataflow_id(path.name)
    rows: list[list[str]] = []

    for series_key, series in dataset.get("series", {}).items():
        idx_parts = series_key.split(":")
        series_labels: list[str] = []
        for dim, idx_str in zip(series_dims, idx_parts):
            try:
                dim_value = dim["values"][int(idx_str)]
            except (ValueError, IndexError, KeyError):
                dim_value = {}
            series_labels.append(dim_value.get("name", ""))
            if dim["id"] == TERRITORY_DIM:
                code = dim_value.get("id", "")
                series_labels.extend([code, territory_level(code)])

        for time_idx_str, obs_value in series.get("observations", {}).items():
            try:
                time_label = time_values[int(time_idx_str)]
            except (ValueError, IndexError):
                time_label = ""
            value = obs_value[0] if obs_value else ""
            status = obs_status_label(obs_value, obs_attrs_spec)
            rows.append(series_labels + [str(time_label), str(value) if value is not None else "", status])

    # Attach SOURCE dataflow id as the final column of every row.
    header = header + ["SOURCE"]
    rows = [r + [dataflow_id] for r in rows]
    return structure.get("name") or path.stem, header, rows


def main() -> int:
    if not RAW_DIR.is_dir():
        print(f"Raw directory not found: {RAW_DIR}", file=sys.stderr)
        return 1
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files in {RAW_DIR}", file=sys.stderr)
        return 1

    # Group files by output slug: paired dataflows (old methodology + current)
    # share the same human-readable dataset name, so they go into one CSV with
    # a SOURCE column identifying the dataflow.
    groups: dict[str, list[tuple[str, list[str], list[list[str]]]]] = {}
    for f in files:
        try:
            name, header, rows = parse(f)
        except Exception as exc:
            print(f"[{f.name}] FAILED: {exc}", file=sys.stderr)
            return 2
        slug = slugify(name)
        groups.setdefault(slug, []).append((name, header, rows))

    for slug, entries in groups.items():
        # Use the widest header across paired sources so a column missing in
        # one dataflow still produces empty cells, not misalignment.
        canonical_header = max((h for _, h, _ in entries), key=len)
        out_path = CSV_DIR / f"{slug}.csv"
        total = 0
        with out_path.open("w", newline="", encoding="utf-8") as outfh:
            writer = csv.writer(outfh)
            writer.writerow(canonical_header)
            for _, header, rows in entries:
                col_map = {col: header.index(col) if col in header else None for col in canonical_header}
                for r in rows:
                    writer.writerow(["" if col_map[c] is None else r[col_map[c]] for c in canonical_header])
                    total += 1
        print(f"{out_path.name}: {total:,} rows from {len(entries)} dataflow(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
