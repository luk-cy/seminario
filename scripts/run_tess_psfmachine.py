#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import lightkurve as lk
import pandas as pd
import psfmachine as pm


def parse_tics(path: Path):
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def parse_sectors(raw: str):
    if raw.lower() == "all":
        return None
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def export_lightcurves(lcs, outdir: Path):
    exported = 0
    for idx, lc in enumerate(lcs):
        df = lc.to_pandas()
        if df.empty:
            continue
        csv_path = outdir / f"lc_{idx:03d}.csv"
        df.to_csv(csv_path)
        exported += 1
    return exported


def process_tic(tic: str, sectors, cadence: str, output_dir: Path):
    tic_dir = output_dir / f"TIC_{tic}"
    tic_dir.mkdir(parents=True, exist_ok=True)

    query = lk.search_targetpixelfile(
        f"TIC {tic}",
        mission="TESS",
        cadence=cadence,
        sector=sectors,
    )
    if len(query) == 0:
        raise RuntimeError("No se encontraron TPFs para el criterio dado")

    tpfs = query.download_all()
    if tpfs is None or len(tpfs) == 0:
        raise RuntimeError("No se pudieron descargar TPFs")

    machine = pm.TPFMachine.from_TPFs(tpfs)
    machine.fit_lightcurves(sap=True)

    exported = export_lightcurves(machine.lcs, tic_dir)

    log = {
        "tic": tic,
        "n_tpfs": len(tpfs),
        "n_lcs_exportadas": exported,
        "cadence": cadence,
        "sectors": sectors if sectors is not None else "all",
    }
    (tic_dir / "log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Ejecuta PSFMachine para una lista de TICs TESS")
    ap.add_argument("--tic-file", required=True, type=Path)
    ap.add_argument("--sectors", default="all", help="'all' o lista CSV, ej. 70,71")
    ap.add_argument("--cadence", default="short", choices=["short", "long", "fast"])
    ap.add_argument("--output-dir", default="outputs", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    tics = parse_tics(args.tic_file)
    if args.limit:
        tics = tics[: args.limit]

    sectors = parse_sectors(args.sectors)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for tic in tics:
        try:
            process_tic(tic, sectors=sectors, cadence=args.cadence, output_dir=args.output_dir)
            print(f"[OK] TIC {tic}")
        except Exception as exc:
            err_dir = args.output_dir / f"TIC_{tic}"
            err_dir.mkdir(parents=True, exist_ok=True)
            (err_dir / "error.txt").write_text(str(exc))
            print(f"[ERROR] TIC {tic}: {exc}")


if __name__ == "__main__":
    main()
