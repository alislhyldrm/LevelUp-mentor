#!/usr/bin/env python
"""blend — OOF uzerinde ensemble olcumu.

    python tools/blend.py EXP-011 EXP-012 EXP-015

Once ESIT AGIRLIKLI karisimi olcer, sonra sinirli (<=200 adim) agirlik aramasi yapar.

KURAL (asiri uyum panzehiri):
  Agirlik aramasi yapilan OOF skoru BAGIMSIZ DOGRULAMA SAYILMAZ.
  Ensemble ancak en iyi tek modeli FOLD BAZINDA da geciyorsa kabul edilir.

Gereken: core/folds.csv  ->  id, fold, y   (y = gercek hedef)
         core/metric.py  ->  score(y_true, y_pred), GREATER_IS_BETTER
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "core"))


def die(msg: str) -> None:
    print(f"HATA: {msg}", file=sys.stderr)
    sys.exit(1)


def load_truth() -> pd.DataFrame:
    p = ROOT / "core" / "folds.csv"
    if not p.exists():
        die("core/folds.csv yok.")
    df = pd.read_csv(p)
    for col in ("fold", "y"):
        if col not in df.columns:
            die(f"core/folds.csv icinde '{col}' kolonu yok. Sozlesme: id, fold, y")
    return df.rename(columns={df.columns[0]: "id"})


def load_oof(exp_id: str, id_col: str) -> pd.Series:
    p = ROOT / "experiments" / exp_id / "output" / "oof.parquet"
    if not p.exists():
        die(f"{exp_id}: oof.parquet yok. Once `kx.py fetch`.")
    df = pd.read_parquet(p)
    if "id" not in df.columns:
        die(f"{exp_id}: oof.parquet'te 'id' kolonu yok.")
    pred_cols = [c for c in df.columns if c not in ("id", "fold")]
    if len(pred_cols) != 1:
        die(f"{exp_id}: {len(pred_cols)} tahmin kolonu var; bu arac tek kolonlu OOF bekler.")
    return df.set_index("id")[pred_cols[0]]


def fold_scores(score, y: pd.Series, p: pd.Series, folds: pd.Series) -> list[float]:
    return [float(score(y[folds == f].values, p[folds == f].values)) for f in sorted(folds.unique())]


def main() -> None:
    ap = argparse.ArgumentParser(description="OOF ensemble olcumu. Submit yapmaz.")
    ap.add_argument("exps", nargs="+", help="EXP-011 EXP-012 ...")
    ap.add_argument("--steps", type=int, default=200, help="agirlik arama adimi (varsayilan 200)")
    args = ap.parse_args()

    try:
        from metric import GREATER_IS_BETTER, score  # type: ignore
    except ImportError as exc:
        die(f"core/metric.py yuklenemedi: {exc}")

    truth = load_truth().set_index("id")
    preds = pd.DataFrame({e: load_oof(e, "id") for e in args.exps})
    common = preds.dropna().index.intersection(truth.index)
    if len(common) == 0:
        die("OOF'lar ile folds.csv arasinda ortak id yok. Hizalama bozuk.")
    if len(common) < len(truth):
        print(f"UYARI: {len(truth) - len(common)} satir disarida kaldi (FAST kosu karisiyor olabilir).")

    P = preds.loc[common]
    y = truth.loc[common, "y"]
    f = truth.loc[common, "fold"]
    sign = 1.0 if GREATER_IS_BETTER else -1.0

    print(f"\n{len(common)} satir, {len(args.exps)} model, {f.nunique()} fold\n")

    print("-- Tek modeller --")
    singles = {}
    for e in args.exps:
        s = float(score(y.values, P[e].values))
        singles[e] = (s, fold_scores(score, y, P[e], f))
        print(f"  {e:10} {s:.6f}")
    best_exp = max(singles, key=lambda e: singles[e][0] * sign)
    best_s, best_folds = singles[best_exp]
    print(f"  en iyi tek: {best_exp} ({best_s:.6f})")

    eq = P.mean(axis=1)
    eq_s = float(score(y.values, eq.values))
    eq_folds = fold_scores(score, y, eq, f)
    print(f"\n-- Esit agirlikli --\n  {eq_s:.6f}  ({(eq_s - best_s) * sign:+.6f} vs en iyi tek)")

    # sinirli arama: simplex uzerinde rastgele ornekleme
    rng = np.random.default_rng(42)
    n = len(args.exps)
    best_w, best_w_s = np.ones(n) / n, eq_s
    for _ in range(max(0, args.steps)):
        w = rng.dirichlet(np.ones(n))
        s = float(score(y.values, (P.values * w).sum(axis=1)))
        if s * sign > best_w_s * sign:
            best_w, best_w_s = w, s
    bl = pd.Series((P.values * best_w).sum(axis=1), index=P.index)
    bl_folds = fold_scores(score, y, bl, f)

    print(f"\n-- Aranan agirliklar ({args.steps} adim) --")
    for e, w in zip(args.exps, best_w):
        print(f"  {e:10} {w:.3f}")
    print(f"  skor {best_w_s:.6f}  ({(best_w_s - best_s) * sign:+.6f} vs en iyi tek)")
    print("  NOT: bu skor bagimsiz dogrulama DEGILDIR - agirlik ayni OOF'ta arandi.")

    print(f"\n-- Fold bazinda: ensemble vs {best_exp} --")
    print("  fold |   tek   |  esit   | aranan")
    verdict_eq = verdict_w = True
    for i, (b, e_, w_) in enumerate(zip(best_folds, eq_folds, bl_folds)):
        print(f"  {i:>4} | {b:.6f} | {e_:.6f} | {w_:.6f}")
        verdict_eq &= (e_ - b) * sign > 0
        verdict_w &= (w_ - b) * sign > 0

    print("\n-- KARAR --")
    if verdict_eq:
        print(f"  KABUL: esit agirlikli karisim {best_exp}'i her fold'da geciyor. Once bunu kullan.")
    elif verdict_w:
        print(f"  KOSULLU: aranan agirlik her fold'da geciyor ama esit agirlikli gecmiyor.")
        print("  Agirlik ayni OOF'ta arandigi icin asiri uyum riski var. Tercihen esit agirlikta kal.")
    else:
        print(f"  RED: ensemble {best_exp}'i her fold'da gecmiyor. Tek model korunur.")
    print("  Karari insan verir.")


if __name__ == "__main__":
    main()
