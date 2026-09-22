#!/usr/bin/env python
"""core/folds.csv'yi YERELDE uretir. Kaggle'a hicbir sey gondermez.

D-01 (CV + metrik onayi) alindiktan SONRA bir kez calistirilir:

    python tools/make_folds.py --target <hedef_kolon> [--pos <pozitif_etiket>]

Cikti: core/folds.csv  (id, fold, y)  + ekrana fold parmak izi.
Parmak izi core/cv_spec.md'ye yazilir; her Kaggle kosusu ayni izi basmalidir.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "core"))

FOLDS_PATH = ROOT / "core" / "folds.csv"
DEFAULT_TRAIN = ROOT / "data" / "train.csv"


def main() -> None:
    p = argparse.ArgumentParser(description="core/folds.csv uret (yerel, Kaggle'a gitmez)")
    p.add_argument("--train", default=str(DEFAULT_TRAIN))
    p.add_argument("--target", required=True, help="hedef kolon adi")
    p.add_argument("--id", default="id", help="kimlik kolonu (varsayilan: id)")
    p.add_argument("--pos", help="pozitif sinif etiketi (ornek: Yes). Sayisal hedefte bos birak")
    p.add_argument("--force", action="store_true", help="mevcut folds.csv'nin uzerine yaz")
    args = p.parse_args()

    import pandas as pd
    from folds_snippet import FOLD_SCHEME, FOLD_SEED, N_FOLDS, fold_fingerprint, make_folds

    if FOLDS_PATH.exists() and not args.force:
        print(f"HATA: {FOLDS_PATH} zaten var. Fold'lar D-01'den sonra SABITTIR "
              f"(CLAUDE.md kural 1). Gercekten degisecekse --force ve yeni CV surumu.",
              file=sys.stderr)
        sys.exit(1)

    train = pd.read_csv(args.train)
    if args.target not in train.columns:
        sys.exit(f"HATA: '{args.target}' kolonu {args.train} icinde yok.")
    if args.id not in train.columns:
        sys.exit(f"HATA: '{args.id}' kolonu {args.train} icinde yok.")

    raw = train[args.target]
    if args.pos is not None:
        y = (raw.astype(str).str.strip().str.lower() == args.pos.strip().lower()).astype(int)
        if y.sum() == 0:
            sys.exit(f"HATA: '{args.pos}' hicbir satirda yok. Etiketler: {sorted(raw.unique())[:10]}")
    else:
        y = raw

    X = train.drop(columns=[c for c in (args.target, args.id) if c in train.columns])
    fold = make_folds(X, y.values)
    fp = fold_fingerprint(fold)

    out = pd.DataFrame({args.id: train[args.id], "fold": fold, "y": y.values})
    FOLDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(FOLDS_PATH, index=False)

    print(f"{FOLDS_PATH} yazildi: {len(out)} satir, {N_FOLDS} fold, sema={FOLD_SCHEME}, seed={FOLD_SEED}")
    print(f"fold dagilimi: {out['fold'].value_counts().sort_index().tolist()}")
    print(f"hedef orani  : {float(y.mean()):.5f}")
    print(f"\nFOLD PARMAK IZI: {fp}")
    print("Bunu core/cv_spec.md'ye yaz. Her Kaggle kosusu ayni izi basmali.")


if __name__ == "__main__":
    main()
