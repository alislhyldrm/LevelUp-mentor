# ensemble/ — model birleştirme

**Aşama:** 3 sonu (iterasyonlar bittikten sonra, final kapısından önce).

**Şu an boş.** Dolmaya başlaması için OOF dosyaları gerekir: her koşuda sohbete yalnız
ekran çıktısı gelir, OOF tahminleri Kaggle'daki koşunun çıktısında kalır. Ensemble
aşamasında insan en iyi 3–5 adayın `oof.parquet` + `test_preds.parquet` dosyalarını
indirip `experiments/EXP-xxx/output/` altına koyar.

**İçeriği:** `tools/blend.py` çıktıları — ağırlıklar, birleşik OOF skoru, birleşik
`submission.csv` ve hangi koşulardan üretildiği.

**Kural:** ağırlıklar hangi OOF setiyle hesaplandıysa, gönderilecek dosya **aynı
koşuların** tahminleriyle üretilir (`/final` kapısı madde 4).

**Kim yazar:** ajan üretir, kararı insan verir.
