# CV sözleşmesi

> Bu dosya D-01'de doldurulur ve ondan sonra **sabittir.** Sadece kanıtlanmış bir kusur
> (sızıntı, gruplama ihlali) için değişir; değişirse yeni CV sürümü açılır.

## Ana validation şeması
- Fold sayısı:
- Bölme mantığı (grup / zaman / stratified / IID):
- Gruplama anahtarı:
- Zaman sütunu ve gap:
- Test-ayrım hipotezi (test seti nasıl oluşturulmuş):
- Bu hipotezi destekleyen veri kanıtı:

## Ana skor
- `cv_mean` (fold ortalaması) mı, `cv_oof` (birleşik OOF üzerinden tek hesap) mı:
- Metrik yönü (büyük iyi / küçük iyi):
- Gerekçe:

İkisi de her koşuda `result.json`'a yazılır. Sıralama ve karar **hep ana skorla** yapılır.

## Duyarlılık kontrolü (alternatif şema)
- Alternatif şema:
- Neden ana seçilmedi:
- İki şemada model sıralaması değişiyor mu:
- Validation belirsizliği (varsa):

Sıralama değişiyorsa bu belirsizlik ancak bir gönderimle sınanabilir — akışta zorunlu
gönderim yoktur, karar insanındır. Sınanana kadar belirsizlik `STATUS.md`'de açık kalır.

## FAST modu — tek sabit tanım
`FAST = True` tek başına yetmez. FAST'ın tek bir sabit tanımı vardır:
- Aynı eğitim alt kümesi:
- Aynı validation satırları:
- Aynı iterasyon bütçesi:

FAST sonuçları yalnız FAST ile karşılaştırılır. FAST'ta zayıf çıkan fikir kesin elenmiş
sayılmaz; daha uzun eğitim isteyen fikirler için not düşülür.

## `core/` sözleşmesi

| Dosya | İçerik |
|---|---|
| `folds_snippet.py` | Fold üretim kodu + parmak izi fonksiyonu. **Tek doğruluk kaynağı** |
| `folds.csv` | `id, fold, y` — `tools/make_folds.py` üretir. Yerelde kalır; `blend.py` hedefi buradan alır |
| `metric.py` | `score(y_true, y_pred) -> float` + `GREATER_IS_BETTER`. Tek fonksiyon, tek sabit |
| `cv_spec.md` | bu dosya |

**Bu klasör Kaggle'a yüklenmez.** Kaggle koşusunda fold ve metrik, `folds_snippet.py` ve
`metric.py`'nin metni `code.py`'ye **aynen gömülerek** uygulanır (`kx.py new` gömer).
Garanti dosya paylaşımı değil, **fold parmak izi eşitliğidir**:

- Yerel parmak izi (`tools/make_folds.py` basar): `TODO — D-01'den sonra buraya yazılır`
- Her koşu aynı izi ekrana basar. Tutmazsa `kx.py kayit` sonucu **kayda almaz**.

`core/metric.py` şu an ROC AUC şablonudur — `/case` bunu resmi metrikle değiştirir.

## Çıktı sözleşmesi
Her koşu `/kaggle/working/` altına yazar:

| Dosya | İçerik |
|---|---|
| `oof.parquet` | `id` kolonu + tahmin kolon(lar)ı. Kimliksiz `.npy` yasak. Çok sınıflıysa kolon adları sınıf adlarıdır |
| `test_preds.parquet` | Aynı format, test kimlikleriyle |
| `submission.csv` | Yarışmanın istediği tam format |
| `result.json` | `{exp_id, parent, owner, kernel_slug, kernel_version, mode, seed, fold_scores[], cv_mean, cv_oof, n_folds_done, n_rows_oof, runtime_min, note}` |
| `artifacts/` | Eğitilmiş ağırlık + ön işleme nesneleri + kolon/sınıf sırası + paket sürümleri |

`kx.py kayit` bunları otomatik doğrular: fold parmak izi tutuyor mu, id kolonu var mı, satır sayısı
`folds.csv` ile eşleşiyor mu, NaN/tekrar var mı, `n_folds_done` tam mı.
Biri tutmazsa sonuç kayda girmez.
