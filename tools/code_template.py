# =============================================================================
# __EXP_ID__   parent: __PARENT__   owner: __OWNER__
# Hipotez: __NOTE__
# Kaggle notebook adi (tek hesap - cakismayi onler): __SLUG__
#
# KULLANIM: bu dosyanin TAMAMINI Kaggle notebook'undaki ilk hucreye yapistir,
# Run All. Bitince ekran ciktisinin TAMAMINI sohbete yapistir.
# Kaggle'a bu koddan baska hicbir sey gitmez; submit yok.
# =============================================================================
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

EXP_ID = "__EXP_ID__"
PARENT = "__PARENT__"
OWNER = "__OWNER__"
MODE = "FULL"          # FAST | FULL  - FAST tanimi core/cv_spec.md'de sabit
SEED = 42
NOTE = "__NOTE__"

TARGET = "__TARGET__"
IDCOL = "__IDCOL__"
POS_LABEL = "__POS_LABEL__"   # sayisal hedefte bos birak

t0 = time.time()


# --- veri: /kaggle/input yolu sabit degil, rglob ile bulunur -----------------
def bul(ad: str) -> Path:
    for p in Path("/kaggle/input").rglob(ad):
        return p
    raise FileNotFoundError(f"{ad} /kaggle/input altinda bulunamadi")


train = pd.read_csv(bul("train.csv"))
test = pd.read_csv(bul("test.csv"))
samp = pd.read_csv(bul("sample_submission.csv"))
print(f"train {train.shape}  test {test.shape}  sample {samp.shape}")

if POS_LABEL:
    y = (train[TARGET].astype(str).str.strip().str.lower() == POS_LABEL.strip().lower()).astype(int).values
else:
    y = train[TARGET].values


# === FOLD SOZLESMESI - core/folds_snippet.py'den AYNEN gomuldu, ELLEME ======
__FOLD_SNIPPET__
# === FOLD SOZLESMESI SONU ===================================================


# === METRIK - core/metric.py'den AYNEN gomuldu, ELLEME ======================
__METRIC_SNIPPET__
# === METRIK SONU ============================================================


# --- DENEYIN TEK DEGISEN YERI ------------------------------------------------
# Parent'a gore farkin TAMAMI bu fonksiyonun icindedir. Fold dongusu,
# metrik ve cikti blogu deneyden deneye degismez - boylece skor farki
# gercekten hipotezden gelir.
def hazirla(tr: pd.DataFrame, te: pd.DataFrame):
    """Girdi: ham train/test. Cikti: (X, Xte, kategorik kolon adlari)."""
    X = tr.drop(columns=[c for c in (TARGET, IDCOL) if c in tr.columns])
    Xte = te.drop(columns=[c for c in (TARGET, IDCOL) if c in te.columns])

    # TODO(deney): feature degisiklikleri buraya

    cat = [c for c in X.columns if X[c].dtype == object]
    for c in cat:  # train+test ayni kategori sirasi - yoksa kodlama kayar
        kats = pd.Categorical(pd.concat([X[c], Xte[c]]).astype(str)).categories
        X[c] = pd.Categorical(X[c].astype(str), categories=kats)
        Xte[c] = pd.Categorical(Xte[c].astype(str), categories=kats)
    return X, Xte, cat


def model_kur(cat_idx):
    """TODO(deney): model ailesi ve hiperparametreler."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    return HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.06, early_stopping=True,
        validation_fraction=0.1, categorical_features=cat_idx, random_state=SEED,
    )


def tahmin(m, X):
    """Metrigin bekledigi tahmin. Ikili siniflandirmada olasilik."""
    return m.predict_proba(X)[:, 1]
# -----------------------------------------------------------------------------


X, Xte, cat = hazirla(train, test)
cat_idx = [X.columns.get_loc(c) for c in cat]
print(f"kolon: {X.shape[1]}  kategorik: {cat}")

fold = make_folds(X, y)
FP = fold_fingerprint(fold)
print(f"FOLD PARMAK IZI: {FP}   ({N_FOLDS} fold, seed {FOLD_SEED}, {FOLD_SCHEME})")

if MODE == "FAST":
    # FAST tanimi core/cv_spec.md'de SABIT: ayni alt kume, ayni validation satirlari.
    rng = np.random.RandomState(SEED)
    alt = rng.rand(len(y)) < 0.25
else:
    alt = np.ones(len(y), dtype=bool)

oof = np.full(len(y), np.nan)
tp = np.zeros(len(Xte))
fold_scores = []
for k in range(N_FOLDS):
    tr_i = (fold != k) & alt
    va_i = (fold == k) & alt
    m = model_kur(cat_idx)
    m.fit(X[tr_i], y[tr_i])
    oof[va_i] = tahmin(m, X[va_i])
    tp += tahmin(m, Xte) / N_FOLDS
    s = float(score(y[va_i], oof[va_i]))
    fold_scores.append(s)
    print(f"  fold {k}: {s:.6f}   ({time.time() - t0:.0f} sn)")

kapsam = ~np.isnan(oof)
cv_mean = float(np.mean(fold_scores))
cv_oof = float(score(y[kapsam], oof[kapsam]))
print(f"\ncv_mean {cv_mean:.6f} | cv_oof {cv_oof:.6f}")

# --- cikti sozlesmesi (core/cv_spec.md) --------------------------------------
W = Path("/kaggle/working")
pd.DataFrame({IDCOL: train[IDCOL], "fold": fold, "y": y, "pred": oof}).to_parquet(W / "oof.parquet", index=False)
pd.DataFrame({IDCOL: test[IDCOL], "pred": tp}).to_parquet(W / "test_preds.parquet", index=False)

sub = samp.copy()
sub_col = [c for c in samp.columns if c != IDCOL][0]
sub[sub_col] = sub[IDCOL].map(pd.Series(tp, index=test[IDCOL]))   # id ile eslestir, POZISYONEL DEGIL
assert sub[sub_col].notna().all(), "submission: id eslesmedi"
sub.to_csv(W / "submission.csv", index=False)

result = {
    "exp_id": EXP_ID, "parent": PARENT, "owner": OWNER, "mode": MODE, "seed": SEED,
    "fold_scores": fold_scores, "cv_mean": cv_mean, "cv_oof": cv_oof,
    "n_folds_done": len(fold_scores), "n_rows_oof": int(kapsam.sum()),
    "fold_fingerprint": FP, "runtime_min": round((time.time() - t0) / 60, 1), "note": NOTE,
}
(W / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("cikti dosyalari:", sorted(p.name for p in W.iterdir() if p.is_file()))

# --- sohbete yapistirilacak blok - kx.py kayit bunu okur ---------------------
print("\n=== KX RESULT JSON ===")
print(json.dumps(result))
print("=== KX RESULT SONU ===")
