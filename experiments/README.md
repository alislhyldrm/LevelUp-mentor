# experiments/ — deney kayıtları

**Aşama:** 2 (baseline ve iterasyonlar). Her koşu **bir klasör**.

| Dosya | Ne işe yarar | Kim yazar |
|---|---|---|
| `EXP_SUMMARY.md` | Tüm deneyler tek tabloda, deney başına tek satır | `kx.py kayit` + ajan (Karar sütunu) |
| `EXP-xxx/code.py` | Kaggle'a yapıştırılan **tam kod** | ajan |
| `EXP-xxx/diff.md` | Parent'a göre değişen satırlar — koşudan önce insana gösterilen şey | ajan |
| `EXP-xxx/card.md` | Hipotez · dayanak · sonuç · karar · atlanan doğrulama · ürün etkisi · ders | ajan, kararı insan verir |
| `EXP-xxx/output/` | `run_log.txt` (yapıştırılan ekran çıktısı), `result.json`, indirilmişse `oof.parquet` vb. | insan + araç |

**Neden kod ve çıktı aynı yerde:** 12. deneyde bir şey bozulduğunda en iyi skora dönüp
farkı satır satır görebilmek için. Kayıt olmadan geri dönüş yoktur.

**Ne zaman sabitlenir:** sonucu alınmış deney klasörü **değiştirilmez**; yeni deney
açılır (`CLAUDE.md` kural 4). Hiçbir OOF/test tahmini silinmez, RED çıkanlar da kalır.
