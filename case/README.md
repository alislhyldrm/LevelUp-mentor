# case/ — yarışma case'i

**Aşama:** 1 (case geldiği an, ilk 10 dakika). `/case` skill'i doldurur.

| Dosya | Ne işe yarar | Kim yazar |
|---|---|---|
| `CASE.md` | 10 satırlık triyaj + görev + ürün bölümü + jüri kriterleri + açık engeller | ajan, insanın verdiği metinden |
| `TRAPS.md` | Veri tipine göre tuzak listesi. Doldurulmaz, **taranır** | hazır referans |
| `pages/` | Yarışma sayfalarının ham metni | insan yapıştırır, ajan kaydeder |

**Kural:** çelişkide hakem `pages/` altındaki ham metindir, `CASE.md` özeti değil.
Bilinmeyen satır tahminle doldurulmaz; "ENGEL — bilinmiyor + nasıl öğrenilecek" yazılır.

**Ne zaman sabitlenir:** sabitlenmez. Yeni resmi bilgi geldikçe yalnız etkilenen bölüm
güncellenir. Metrik, veri veya kapsam değişirse `core/cv_spec.md` sürümlenir.
