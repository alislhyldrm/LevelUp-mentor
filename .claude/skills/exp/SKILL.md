---
name: exp
description: Tek bir deneyi baştan sona yürütür - backlog maddesini seçer, koşulacak kodu hazırlar, insana gösterir, insan Kaggle'da koşturur, dönen çıktıyı doğrular, parent ile fold fold karşılaştırır, kaydeder ve karar önerir. Kullan - "şunu dene", "B-03'ü koş", bir deney sonucu geldiğinde, deney kaydı güncellenmesi gerektiğinde.
---

# Deney döngüsü

Araç: `python tools/kx.py`. **İnsan karar verir ve koşturur, sen kodu yazar ve kaydedersin.**
Kaggle'a hiçbir şey göndermezsin; `kx.py` Kaggle CLI'yi hiç çağırmaz.

## Önce: deney açılabilir mi?

Dört satır yazılamıyorsa deney açılmaz:
hangi backlog maddesi · hangi hipotez (tek cümle) · hangi dayanak · tahmini kaç dakika.

Ana hat oturduktan sonra her deney **tek hipotez** taşır. Teknik olarak zorunlu birlikte
değişiklikler aynı deneyde kalır. Ana hat oturmadan önceki keşif deneyleri birden fazla
değişiklik içerebilir; `card.md`'de "keşif" işaretlenir ve karar kuralına girmez.

**Her koşu kendi onayı, kendi kaydı (K-08):** bir sonuca dayanan kod o sonuç kaydedildikten
sonra verilir. Paralel koşu yalnız insan isterse, aynı kayıtlı parent'tan ve eşzamanlı
limit içinde açılır (`CLAUDE.md`).

## Akış

1. **Aç.** `python tools/kx.py new EXP-0xx --parent EXP-0yy --note "<hipotez>"`
   Numara aralığı: Claude `EXP-0xx`/`EXP-1xx`, Codex `EXP-2xx` (`CODEX.md`).
   Tamam: klasör, `code.py`, `card.md`, `diff.md`, `output/` var.

2. **Kodu doldur.** `code.py` içindeki TODO'lar — **yalnız** `TEKNIKLER`, `hazirla`,
   `fold_hazirla`, `model_kur`, `egit`, `tahmin`. Kod yazmadan önce uygulanacak tekniğin
   kuralını `SOZLESME.md` §4'ten oku.
   Kurallar:
   - Fold bloğu ve metrik bloğu `core/folds_snippet.py` + `core/metric.py`'den aynen
     gömülüdür. **Bu bloklara dokunma.** Kod kendi fold'unu üretmez.
   - Fit edilen veya hedefe bakan her dönüşüm `fold_hazirla`'da; `hazirla` satır-içidir.
   - `TEKNIKLER` listesi her uygulanan tekniği tek satırla taşır (saf baseline'da boş).
   - Mod (FAST/FULL) ve seed açıkça yazılır. FAST tanımı `core/cv_spec.md`'de sabittir.
   - Çıktı bloğu ve `=== KX RESULT JSON ===` bloğu silinmez — kayıt bunlarla yapılır.
   Tamam: TODO kalmadı, `python -c "import ast; ast.parse(open(...).read())"` temiz.

3. **Riskliyse Codex'e incele.** Veri işleme, feature veya hedef değişkene dokunuyorsa
   `CODEX.md` Çağrı 2. Yalnız parametre değiştiyse atla.
   **GEÇERSİZ KILAR** çıkarsa kod insana verilmez, düzeltilir. Diğer iki kademe akışı
   durdurmaz; `card.md`'ye "Codex incelemesi" satırına yazılır.
   Tamam: kademe ve varsa en küçük düzeltme kayıtlı.

4. **Kodu insana ver.** `diff.md`'yi doldur (parent'a göre değişen satırlar) ve sohbette
   göster: ne değişti · neden · **uygulanan teknikler** (her biri: ne · neden · sızıntı
   nasıl önlendi) · tahmini süre · GPU gerekiyor mu.
   **Skor tek başına rapor değildir; insan neyin denendiğini kodda görmeden onay vermiş
   sayılmaz.** Uzun zincirlerde her adımı ayrı ayrı özetle, sona biriktirme.
   Tamam: `code.py` sohbete yapıştırıldı, `diff.md` dolu.

5. **İnsan koşturur.** Kaggle notebook editörü → kodu yapıştır → `Run All`; ya da yerelde
   `python experiments/EXP-0xx/code.py` (koşu yeri `/case` triyajında belli olur).
   Burada beklersin; sıradaki deney yalnız insan paralel koşu isterse açılır.
   Tamam: insan "koştu" dedi ve ekran çıktısını verdi.

6. **Çıktıyı kaydet.** Kaggle koşusunda ekran çıktısını
   `experiments/EXP-0xx/output/run_log.txt`'ye yaz (yerel koşuda dosyalar zaten
   `output/`'ta), sonra `python tools/kx.py kayit EXP-0xx`.
   - `run_log.txt` içindeki `=== KX RESULT JSON ===` bloğundan `result.json` üretilir.
   - **Fold parmak izi** yereldeki `core/folds.csv` ile karşılaştırılır. Tutmazsa sonuç
     kayda **girmez** — koşu başka fold'larla eğitilmiş demektir.
   - OOF/submission dosyaları inmediyse ilgili kontroller "atlandı" olarak raporlanır;
     bunları `card.md`'deki "Atlanan doğrulama" satırına yaz, sessizce geçme.
   - Koşu hatası veya eksik çıktı fikre RED yazdırmaz; "koşmadı" olarak kaydedilir.
   Tamam: `EXP_SUMMARY.md` ve `log/RUNS.md`'ye satır düştü.

7. **Karşılaştır.** `python tools/kx.py cmp EXP-0xx`
   Çıktı: ana skor farkı, **diğer skor farkı** (bilgi amaçlı, otomatik öneriyi etkilemez),
   fold fold farklar, fold farklarının standart sapması, öneri.
   `cv_mean` ve `cv_oof` zıt yöne işaret ederse araç UYARI basar — ikisine de bak,
   `card.md`'ye hangisinin neden tercih edildiğini yaz.
   Karar kuralı `CLAUDE.md`'de. **"BELİRSİZ" yok.** KABUL / HAVUZ / RED.
   CV'de beklenmedik büyük sıçrama varsa önce sızıntı araştır.
   Tamam: öneri insana sunuldu, kararı insan verdi.

8. **Kaydet.** `card.md`'yi doldur (Uygulanan teknikler, Sonuç, Karar, Atlanan doğrulama,
   Ders, Codex incelemesi, Ürün etkisi) ve `EXP_SUMMARY.md`'deki **Karar sütununu aynı anda** güncelle.
   `STATUS.md`'yi tam yeniden yazma; yalnız `Şu an`, `Bu oturumda ne oldu` ve
   `İnsandan sıradaki eylem` bölümlerini güncelle. KABUL ise `Şu an`'daki ana hat
   satırı da değişir. RED/HAVUZ çıkan deney aynı anda `Denendi, işe yaramadı`'ya
   tek satır düşer (detay: `EXP_SUMMARY.md`). KABUL ise: ürüne izi tek satır +
   global istatistikten türeyen feature varsa uyarı notu.
   Tamam: `card.md`, `EXP_SUMMARY.md`, `STATUS.md` üçü de tutarlı.

## Sabit kurallar
- Sonucu alınmış deney klasörü değiştirilmez, yeni deney açılır.
- Hiçbir OOF/test tahmini silinmez. RED çıkanlar da ensemble havuzunda kalır.
- HAVUZ çıkan deney **farklı seed ile tekrar koşulmaz** — yeni bilgiye göre çok pahalı.
- Fark küçükse daha basit/hızlı model korunur.
- Kaggle'a gönderme. Gönderim kararı insanın; sonrasında `log/SUBMISSIONS.md`'ye yaz.
- Model yalnız skora göre kurulmaz: `card.md`'deki "Ürün etkisi" satırı boş bırakılmaz.
  Yarışma dosyasının toplu istatistiğinden türeyen feature (global mean, target encoding)
  varsa, gerçek kullanımda nasıl üretileceği oraya tek satır yazılır.

## İlk baseline'dan hemen sonra
**Önce gürültü koşusu:** `EXP-002` = `EXP-001` kodu, yalnız `SEED` farklı, `card.md`'de
"keşif: gürültü tabanı". Kaydından sonra `python tools/kx.py gurultu EXP-002`; taban
`kx.json`'a yazılır ve sonraki her `cmp` onu kullanır.

**Hata analizi beş deney beklemez.** Kısa bir OOF hata analizi yap; amaç fikir listesi
üretmek değil, bir sonraki deneyi değiştirecek **tek bulgu** aramaktır. Bulguyu
`log/BACKLOG.md`'ye dayanak olarak yaz. Bu analiz OOF dosyasını gerektirir — insandan
`oof.parquet`'i indirmesini iste (tek seferlik, her koşuda değil).
