"""FOLD SOZLESMESI - D-01'de sabitlenir, sonra DEGISMEZ.

Kaggle'a hicbir sey yuklenmedigi icin garanti "ayni dosyayi okumak" degil,
"ayni kodu calistirip ayni parmak izini uretmek"tir:

  yerelde  : tools/make_folds.py  -> core/folds.csv + parmak izi -> core/cv_spec.md
  Kaggle'da: bu dosyanin metni code.py'ye AYNEN gomulur (kx.py new gomer)

Notebook parmak izini ekrana basar. Yerel parmak iziyle esitse fold'lar birebir
aynidir; degilse `kx.py kayit` sonucu kayda ALMAZ.

Bu dosya elle duzenlenirse butun gecmis sonuclar karsilastirilamaz hale gelir.
Sadece kanitlanmis bir kusur icin degisir; degisirse yeni CV surumu acilir
(CLAUDE.md kural 1). /case yalniz asagidaki sabitleri secer, fonksiyonlara dokunmaz.
"""
import hashlib

import numpy as np

# --- D-01'de sabitlenen degerler ------------------------------------------
FOLD_SEED = 42
N_FOLDS = 5
FOLD_SCHEME = "stratified"
#   stratified       : siniflandirma, satirlar birbirinden bagimsiz (varsayilan)
#   kfold            : regresyon / dengeli hedef, satirlar bagimsiz
#   stratified_reg   : regresyon; hedef N_BINS quantile kutusuyla tabakalanir
#   group            : ayni varlik (GROUP_COL) iki tarafa dusmez
#   stratified_group : group + sinif orani korunur (sklearn; surum farkini parmak izi yakalar)
#   time             : TIME_COL'a gore sirali bloklar; egitim yalniz gecmisten, ilk blok hep egitimde
N_BINS = 10          # yalniz stratified_reg
GAP = 0              # yalniz time: validasyondan hemen onceki kac zaman adimi egitimden atilir
# --------------------------------------------------------------------------

SEMALAR = ("stratified", "kfold", "stratified_reg", "group", "stratified_group", "time")


def make_folds(X, y, groups=None, times=None):
    """Satir sirasiyla ayni uzunlukta fold dizisi dondurur (0..N_FOLDS-1).

    X yalniz uzunluk icindir; fold'lar y / groups / times'tan belirlenir.
    time semasinda ilk blok -1 alir: hic validasyon olmaz, hep egitimde kalir.
    """
    if FOLD_SCHEME not in SEMALAR:
        raise ValueError(f"FOLD_SCHEME={FOLD_SCHEME!r} bilinmiyor. Secenekler: {SEMALAR}")
    y = np.asarray(y)
    n = len(y)
    bos = np.zeros((n, 1))
    fold = np.full(n, -1, dtype=np.int64)
    splits = None

    if FOLD_SCHEME == "stratified":
        from sklearn.model_selection import StratifiedKFold

        splits = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_SEED).split(bos, y)
    elif FOLD_SCHEME == "kfold":
        from sklearn.model_selection import KFold

        splits = KFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_SEED).split(bos)
    elif FOLD_SCHEME == "stratified_reg":
        from sklearn.model_selection import StratifiedKFold

        yf = y.astype(float)
        sinir = np.quantile(yf, np.linspace(0, 1, N_BINS + 1)[1:-1])
        kutu = np.searchsorted(sinir, yf, side="right")
        splits = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_SEED).split(bos, kutu)
    elif FOLD_SCHEME == "group":
        # sklearn'e bagli degil: esit boyutlu gruplarda siralama surumden surume kaymasin.
        g = _grup(groups, n)
        uniq, inv, sayi = np.unique(g, return_inverse=True, return_counts=True)
        sira = np.random.RandomState(FOLD_SEED).permutation(len(uniq))
        sira = sira[np.argsort(-sayi[sira], kind="stable")]   # buyuk grup once
        yuk = np.zeros(N_FOLDS)
        gfold = np.empty(len(uniq), dtype=np.int64)
        for gi in sira:                                       # en hafif fold'a ata
            k = int(np.argmin(yuk))
            gfold[gi] = k
            yuk[k] += sayi[gi]
        fold = gfold[np.asarray(inv).ravel()]
    elif FOLD_SCHEME == "stratified_group":
        from sklearn.model_selection import StratifiedGroupKFold

        g = _grup(groups, n)
        splits = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_SEED).split(bos, y, g)
    elif FOLD_SCHEME == "time":
        if times is None or len(times) != n:
            raise ValueError("time semasi TIME_COL ister (siralanabilir: sayi veya ISO tarih)")
        # Bloklar tekil zaman degerleri uzerinden: ayni zaman damgasi iki tarafa bolunmez.
        uniq, inv = np.unique(np.asarray(times), return_inverse=True)
        blok = np.empty(len(uniq), dtype=np.int64)
        for b, parca in enumerate(np.array_split(np.arange(len(uniq)), N_FOLDS + 1)):
            blok[parca] = b - 1
        fold = blok[np.asarray(inv).ravel()]

    if splits is not None:
        for k, (_, vi) in enumerate(splits):
            fold[vi] = k
    alt_sinir = -1 if FOLD_SCHEME == "time" else 0
    if (fold < alt_sinir).any():
        raise RuntimeError("fold atanmamis satir var")
    return fold


def egitim_maskesi(fold, k, times=None):
    """k. fold'un egitim satirlari. time disindaki semalarda: fold != k.

    time: yalniz gecmis (fold < k; -1 blogu hep dahil). GAP > 0 ise validasyonun
    ilk zaman adimindan onceki GAP adim da egitimden atilir.
    """
    fold = np.asarray(fold)
    if FOLD_SCHEME != "time":
        return fold != k
    maske = fold < k
    if GAP > 0:
        adim = np.asarray(np.unique(np.asarray(times), return_inverse=True)[1]).ravel()
        maske &= adim < adim[fold == k].min() - GAP
    return maske


def _grup(groups, n):
    if groups is None or len(groups) != n:
        raise ValueError(f"{FOLD_SCHEME} semasi GROUP_COL ister")
    return np.asarray(groups).astype(str)


def fold_fingerprint(fold) -> str:
    """Fold dizisinin 12 haneli parmak izi. Yerel ve Kaggle ayni olmali."""
    return hashlib.md5(np.asarray(fold, dtype=np.int64).tobytes()).hexdigest()[:12]
