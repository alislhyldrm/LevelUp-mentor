#!/usr/bin/env python
"""adv_val - adversarial validation. YEREL calisir, Kaggle'a hicbir sey gondermez.

    python tools/adv_val.py [--train data/train.csv] [--test data/test.csv] [--drop kol1,kol2]

Train ve test satirlarini ayirt etmeye calisan bir siniflandirici egitir (5 fold).
  AUC ~0.5  : test train ile ayni dagilimdan -> rastgele / stratified bolme savunulabilir
  AUC yuksek: dagilim kaymasi var -> CV test ayrimini taklit etmeli; en cok kayan
              kolonlar backlog'a (dusur / donustur / zaman-grup semasi)
Cikti core/cv_spec.md "Bu hipotezi destekleyen veri kaniti" satirina yazilir.

Hedef ve kimlik kolonu kx.json'dan (target, id_col) okunup dusurulur. AUC ~1 ve tek
kolon baskinsa: kimlik benzeri kolon olabilir (TRAPS #2, #4) - o kolonu --drop ile at.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser(description="train-vs-test siniflandiricisi (yerel)")
    ap.add_argument("--train", default=str(ROOT / "data" / "train.csv"))
    ap.add_argument("--test", default=str(ROOT / "data" / "test.csv"))
    ap.add_argument("--drop", default="", help="ek dusurulecek kolonlar, virgulle")
    ap.add_argument("--max-rows", type=int, default=200_000, help="her taraftan en fazla satir")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold

    cfg_path = ROOT / "kx.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    drop = {c for c in (cfg.get("target"), cfg.get("id_col")) if c}
    drop |= {c.strip() for c in args.drop.split(",") if c.strip()}

    tr, te = pd.read_csv(args.train), pd.read_csv(args.test)
    cols = [c for c in tr.columns if c in te.columns and c not in drop]
    if not cols:
        raise SystemExit("HATA: train ve test'te ortak kolon kalmadi.")
    rng = np.random.RandomState(42)
    if len(tr) > args.max_rows:
        tr = tr.iloc[rng.choice(len(tr), args.max_rows, replace=False)]
    if len(te) > args.max_rows:
        te = te.iloc[rng.choice(len(te), args.max_rows, replace=False)]

    X = pd.concat([tr[cols], te[cols]], ignore_index=True)
    y = np.r_[np.zeros(len(tr), dtype=int), np.ones(len(te), dtype=int)]
    cat = [c for c in cols if X[c].dtype == object or str(X[c].dtype) in ("category", "string", "str")]
    for c in cat:  # etiketsiz kodlama; hedef kullanilmaz
        X[c] = pd.Categorical(X[c].astype(str)).codes
    cat_mask = [c in cat for c in cols]

    print(f"train {len(tr)} + test {len(te)} satir, {len(cols)} kolon (dusurulen: {sorted(drop)})")
    oof = np.zeros(len(y))
    imp = np.zeros(len(cols))
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for k, (ti, vi) in enumerate(skf.split(X, y)):
        m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                           categorical_features=cat_mask, random_state=42)
        m.fit(X.iloc[ti], y[ti])
        oof[vi] = m.predict_proba(X.iloc[vi])[:, 1]
        if k == 0:  # kolon onemi tek fold'da: n_kolon x 3 tahmin, pahali degil
            ornek = vi if len(vi) <= 20_000 else rng.choice(vi, 20_000, replace=False)
            imp = permutation_importance(m, X.iloc[ornek], y[ornek], scoring="roc_auc",
                                         n_repeats=3, random_state=42).importances_mean

    auc = roc_auc_score(y, oof)
    print(f"\nADVERSARIAL AUC: {auc:.4f}")
    if auc < 0.55:
        print("  yorum: train ve test ayirt edilemiyor -> rastgele/stratified bolme savunulabilir")
    elif auc < 0.7:
        print("  yorum: hafif kayma -> asagidaki kolonlari kontrol et, CV semasini buna gore sec")
    else:
        print("  yorum: belirgin kayma -> CV test ayrimini taklit etmeli (zaman/grup?); kayan kolonlar backlog'a")

    sira = np.argsort(-imp)[: args.top]
    print(f"\nen cok kayan {len(sira)} kolon (permutation importance, AUC dususu):")
    for i in sira:
        print(f"  {cols[i]:30} {imp[i]:+.4f}")
    print("\nBunu core/cv_spec.md 'veri kaniti' satirina yaz. Kolon dusurme karari backlog'dan gecer.")


if __name__ == "__main__":
    main()
