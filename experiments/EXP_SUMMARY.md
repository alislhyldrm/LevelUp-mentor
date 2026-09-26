# EXP_SUMMARY

Tüm deneyler tek tabloda. `kx.py kayit` doğrulamayı geçen her sonucu buraya yazar.
**Karar sütununu `cmp`'den sonra elle doldur** — araç doldurmaz.
Doğrulamayı geçmeyen sonuç **kayda girmez.**

> **Tespit uyarlaması:** `kx.py kayit` bu satırları yazamadı — doğrulayıcı tablo şeması
> (`cv_mean`/`cv_oof`/`fold_scores`/`n_folds_done`/`mode`) bekliyor, tespit sonucu tek holdout.
> Satırlar ELLE yazıldı. Bkz. `EXP-001/card.md` → "Atlanan doğrulama".

| EXP | owner | parent | mod | ana skor (AP50) | AP50:95 | AP50@100 | epoch | dk | karar | bölme izi |
|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | Claude | — | FULL | **0,59512** | 0,42258 | 0,59206 | 60/60 | 268 | ana hat (ilk baseline) | val `209e9c83a27b935c` |

Ana skorun `cv_mean` mi `cv_oof` mu olduğu `core/cv_spec.md` + D-01'de sabitlenir.
FAST sonuçları yalnız FAST ile karşılaştırılır, "tam CV" diye sunulmaz.
