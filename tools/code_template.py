# =============================================================================
# __EXP_ID__   parent: __PARENT__   owner: __OWNER__
# Hipotez: __NOTE__
# Kaggle notebook adi (tek hesap - cakismayi onler): __SLUG__
#
# KULLANIM: bu dosyanin TAMAMINI Kaggle notebook'undaki ilk hucreye yapistir,
# Run All. Bitince ekran ciktisinin TAMAMINI sohbete yapistir.
# Yerel kosu da ayni kodla olur: `python experiments/__EXP_ID__/code.py`
# (veri repo data/ altindan okunur, cikti bu klasorun output/ altina yazilir).
# Kaggle'a bu koddan baska hicbir sey gitmez; submit yok.
#
# Degisebilen yerler YALNIZ: TEKNIKLER, hazirla, fold_hazirla, model_kur, egit, tahmin.
# Fold ve metrik bloklari core/'dan aynen gomuludur - dokunulursa sonuc kayda girmez.
# Teknik kurallari: SOZLESME.md
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
SEED = 42              # yalniz model rastgeleligi; fold ve FAST alt kumesi FOLD_SEED'e bagli
NOTE = "__NOTE__"
KUCULT = False         # True: float64->float32, int kucultme (buyuk veride bellek)

TARGET = "__TARGET__"
IDCOL = "__IDCOL__"
POS_LABEL = "__POS_LABEL__"   # sayisal hedefte bos birak
GROUP_COL = "__GROUP_COL__"   # group / stratified_group semasinda dolu (core/cv_spec.md)
TIME_COL = "__TIME_COL__"     # time semasinda dolu

# Uygulanan teknikler - her satir: ne . neden . sizinti kurali nasil korundu.
# Saf baseline'da bos kalir. Liste kosu basinda ve result.json'da gorunur.
TEKNIKLER = [
    # "fold-ici target encoding (kat_a) . yuksek kardinalite . fold_hazirla'da, yalniz egitim fold'unda fit",
]

t0 = time.time()
print(f"{EXP_ID} (parent {PARENT}) - {NOTE}")
print("Uygulanan teknikler:")
for _t in TEKNIKLER or ["(yok - saf baseline)"]:
    print(f"  - {_t}")


# --- ortam: Kaggle'da /kaggle/input, yerelde repo data/ ----------------------
if Path("/kaggle/input").exists():
    GIRDI, W = Path("/kaggle/input"), Path("/kaggle/working")
else:
    _burasi = Path(__file__).resolve().parent          # experiments/EXP-xxx
    GIRDI, W = _burasi.parents[1] / "data", _burasi / "output"
W.mkdir(parents=True, exist_ok=True)


def bul(ad: str) -> Path:
    """Yol sabit degil (Kaggle'da ic ice dizin olabilir) - rglob ile bulunur."""
    bulunan = sorted(GIRDI.rglob(ad))
    if not bulunan:
        raise FileNotFoundError(f"{ad} {GIRDI} altinda bulunamadi")
    if len(bulunan) > 1:
        print(f"UYARI: {ad} icin {len(bulunan)} eslesme, ilki kullaniliyor: {bulunan[0]}")
    return bulunan[0]


train = pd.read_csv(bul("train.csv"))
test = pd.read_csv(bul("test.csv"))
samp = pd.read_csv(bul("sample_submission.csv"))
print(f"train {train.shape}  test {test.shape}  sample {samp.shape}  "
      f"bellek {(train.memory_usage(deep=True).sum() + test.memory_usage(deep=True).sum()) / 1e9:.2f} GB")

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


# --- DENEYIN DEGISEN YERLERI -------------------------------------------------
# Parent'a gore farkin TAMAMI asagidaki bes fonksiyonun ve TEKNIKLER'in icindedir.
# Fold dongusu, metrik ve cikti blogu deneyden deneye degismez - boylece skor
# farki gercekten hipotezden gelir.
def hazirla(tr: pd.DataFrame, te: pd.DataFrame):
    """Fold DISI, bir kez calisir. Cikti: (X, Xte, kategorik kolon adlari).

    YALNIZ satir-ici donusumler (oran, tarih parcasi, metin uzunlugu...) ve hedefe
    bakmayan islemler. Hedefe bakan veya bir istatistik ogrenen (fit eden) her sey
    fold_hazirla'ya gider. train+test ortak istatistik (frekans vb.) burada olabilir;
    card.md 'Urun etkisi'ne not dusulur.
    """
    X = tr.drop(columns=[c for c in (TARGET, IDCOL) if c in tr.columns])
    Xte = te.drop(columns=[c for c in (TARGET, IDCOL) if c in te.columns])

    # TODO(deney): satir-ici feature degisiklikleri buraya

    cat = [c for c in X.columns if X[c].dtype == object]
    for c in cat:  # train+test ayni kategori sirasi - yoksa kodlama kayar
        kats = pd.Categorical(pd.concat([X[c], Xte[c]]).astype(str)).categories
        X[c] = pd.Categorical(X[c].astype(str), categories=kats)
        Xte[c] = pd.Categorical(Xte[c].astype(str), categories=kats)
    return X, Xte, cat


def fold_hazirla(Xtr: pd.DataFrame, ytr, Xva: pd.DataFrame, Xte: pd.DataFrame):
    """Fold ICI, her fold'da calisir. Cikti: (Xtr, Xva, Xte).

    Fit edilen / hedefe bakan her donusum burada ve YALNIZ Xtr, ytr ile fit edilir:
    target encoding, scaler, hedefe gore feature secimi, oversampling (yalniz Xtr'ye).
    Xva ve Xte'ye yalniz transform uygulanir. Girdiler kopyadir.
    """
    # TODO(deney): fold-ici donusumler buraya (yoksa oldugu gibi birak)
    return Xtr, Xva, Xte


def model_kur(cat_idx):
    """TODO(deney): model ailesi ve hiperparametreler."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    return HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.06, early_stopping=True,
        validation_fraction=0.1, categorical_features=cat_idx, random_state=SEED,
    )


def egit(m, Xtr, ytr, Xva, yva, Xte):
    """Egitim. Varsayilan: m.fit(Xtr, ytr).

    Early stopping, DL egitim dongusu, fold-ici pseudo-label burada (SOZLESME.md).
    Xva/yva early stopping'e verilirse bu tum deneylerde ayni kalir; Xte'nin
    etiketi yoktur, yalniz fold modelinin kendi tahminiyle etiketlenebilir.
    """
    m.fit(Xtr, ytr)
    return m


def tahmin(m, X):
    """Metrigin bekledigi tahmin. Ikili siniflandirmada olasilik."""
    return m.predict_proba(X)[:, 1]
# -----------------------------------------------------------------------------


def kucult(df: pd.DataFrame) -> pd.DataFrame:
    """Bellek: float64 -> float32, tam sayilar en kucuk tipe. Kategorik/metin dokunulmaz."""
    for c in df.columns:
        t = df[c].dtype
        if t == "float64":
            df[c] = df[c].astype("float32")
        elif t.kind in "iu":
            df[c] = pd.to_numeric(df[c], downcast="integer" if t.kind == "i" else "unsigned")
    return df


X, Xte, cat = hazirla(train, test)
if KUCULT:
    X, Xte = kucult(X), kucult(Xte)
print(f"kolon: {X.shape[1]}  kategorik: {cat}")

groups = train[GROUP_COL].values if GROUP_COL else None
times = train[TIME_COL].values if TIME_COL else None
fold = make_folds(X, y, groups=groups, times=times)
FP = fold_fingerprint(fold)
print(f"FOLD PARMAK IZI: {FP}   ({N_FOLDS} fold, seed {FOLD_SEED}, {FOLD_SCHEME})")

if MODE == "FAST":
    # FAST tanimi core/cv_spec.md'de SABIT: ayni alt kume, ayni validation satirlari.
    # Alt kume FOLD_SEED'e bagli - model SEED'i degisince alt kume degismez.
    rng = np.random.RandomState(FOLD_SEED)
    alt = rng.rand(len(y)) < 0.25
else:
    alt = np.ones(len(y), dtype=bool)

oof = np.full(len(y), np.nan)
tp = np.zeros(len(Xte))
fold_scores = []
for k in range(N_FOLDS):
    tr_i = egitim_maskesi(fold, k, times) & alt
    va_i = (fold == k) & alt
    Xtr, Xva, Xte_k = fold_hazirla(X[tr_i].copy(), y[tr_i], X[va_i].copy(), Xte.copy())
    cat_idx = [Xtr.columns.get_loc(c) for c in cat if c in Xtr.columns]
    m = egit(model_kur(cat_idx), Xtr, y[tr_i], Xva, y[va_i], Xte_k)
    oof[va_i] = tahmin(m, Xva)
    tp += tahmin(m, Xte_k) / N_FOLDS
    s = float(score(y[va_i], oof[va_i]))
    fold_scores.append(s)
    print(f"  fold {k}: {s:.6f}   ({time.time() - t0:.0f} sn)")

kapsam = ~np.isnan(oof)
cv_mean = float(np.mean(fold_scores))
cv_oof = float(score(y[kapsam], oof[kapsam]))
print(f"\ncv_mean {cv_mean:.6f} | cv_oof {cv_oof:.6f}")

# --- cikti sozlesmesi (core/cv_spec.md) --------------------------------------
# OOF yalniz tahmin edilen satirlari icerir (FAST alt kumesi / time semasinin ilk blogu disarida).
pd.DataFrame({IDCOL: train[IDCOL], "fold": fold, "y": y, "pred": oof})[kapsam].to_parquet(
    W / "oof.parquet", index=False)
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
    "teknikler": TEKNIKLER,
}
(W / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("cikti dosyalari:", sorted(p.name for p in W.iterdir() if p.is_file()))

# --- sohbete yapistirilacak blok - kx.py kayit bunu okur ---------------------
print("\n=== KX RESULT JSON ===")
print(json.dumps(result))
print("=== KX RESULT SONU ===")
