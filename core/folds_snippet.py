"""FOLD SOZLESMESI - D-01'de sabitlenir, sonra DEGISMEZ.

Kaggle'a hicbir sey yuklenmedigi icin garanti "ayni dosyayi okumak" degil,
"ayni kodu calistirip ayni parmak izini uretmek"tir:

  yerelde  : tools/make_folds.py  -> core/folds.csv + parmak izi -> core/cv_spec.md
  Kaggle'da: bu dosyanin metni code.py'ye AYNEN gomulur (kx.py new gomer)

Notebook parmak izini ekrana basar. Yerel parmak iziyle esitse fold'lar birebir
aynidir; degilse `kx.py kayit` sonucu kayda ALMAZ.

Bu dosya elle duzenlenirse butun gecmis sonuclar karsilastirilamaz hale gelir.
Sadece kanitlanmis bir kusur icin degisir; degisirse yeni CV surumu acilir
(CLAUDE.md kural 1).
"""
import hashlib

import numpy as np

# --- D-01'de sabitlenen degerler ------------------------------------------
FOLD_SEED = 42
N_FOLDS = 5
FOLD_SCHEME = "StratifiedKFold(shuffle=True)"   # grup/zaman varsa /case degistirir
# --------------------------------------------------------------------------


def make_folds(X, y, groups=None):
    """Satir sirasiyla ayni uzunlukta fold dizisi dondurur (0..N_FOLDS-1)."""
    from sklearn.model_selection import StratifiedKFold

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_SEED)
    fold = np.full(len(y), -1, dtype=np.int64)
    for k, (_, vi) in enumerate(skf.split(X, y)):
        fold[vi] = k
    if (fold < 0).any():
        raise RuntimeError("fold atanmamis satir var")
    return fold


def fold_fingerprint(fold) -> str:
    """Fold dizisinin 12 haneli parmak izi. Yerel ve Kaggle ayni olmali."""
    return hashlib.md5(np.asarray(fold, dtype=np.int64).tobytes()).hexdigest()[:12]
