---
name: exp
description: Tek bir deneyi baştan sona yürütür - backlog maddesini seçer, notebook'u hazırlar, Kaggle'da koşturur, çıktıyı indirip doğrular, parent ile fold fold karşılaştırır, kaydeder ve karar önerir. Kullan - "şunu dene", "B-03'ü koş", bir deney sonucu geldiğinde, deney kaydı güncellenmesi gerektiğinde.
---

# Deney döngüsü

Araç: `python tools/kx.py`. İnsan karar verir, sen yürütürsün ve kaydedersin.

## Önce: deney açılabilir mi?

Dört satır yazılamıyorsa deney açılmaz:
hangi backlog maddesi · hangi hipotez (tek cümle) · hangi dayanak · tahmini kaç dakika.

Ana hat oturduktan sonra her deney **tek hipotez** taşır. Teknik olarak zorunlu birlikte
değişiklikler aynı deneyde kalır. Ana hat oturmadan önceki keşif deneyleri birden fazla
değişiklik içerebilir; `card.md`'de "keşif" işaretlenir ve karar kuralına girmez.

Push etmeden önce `python tools/kx.py board` — kota ve eşzamanlı koşu limiti ortak kaynaktır.

## Akış

1. **Aç.** `python tools/kx.py new EXP-0xx --parent EXP-0yy --note "<hipotez>"`
   Numara aralığı: Claude `EXP-0xx`/`EXP-1xx`, Codex `EXP-2xx` (`CODEX.md`).
   Tamam: klasör, notebook, `card.md`, `kernel-metadata.json` var.

2. **Notebook'u doldur.** Şablonun TODO'ları. Kurallar:
   - Fold `hackathon-core/folds.csv`'den, metrik `hackathon-core/metric.py`'den okunur.
     Notebook **kendi fold'unu üretmez.**
   - Fit edilen her dönüşüm fold **içinde** fit edilir.
   - Her fold bitince skor basılır ve ara çıktı diske yazılır.
   - Mod (FAST/FULL) ve seed açıkça yazılır. FAST tanımı `core/cv_spec.md`'de sabittir.
   - Çıktılar sözleşmeye uyar; `artifacts/` hücresi silinmez.
   Tamam: TODO kalmadı, mod ve tahmini süre aralığı `card.md`'de.

3. **Riskliyse Codex'e incele.** Veri işleme, feature veya hedef değişkene dokunuyorsa
   `CODEX.md` Çağrı 2. Yalnız parametre değiştiyse atla.
   **GEÇERSİZ KILAR** çıkarsa push durur, düzeltilir. Diğer iki kademe push'u durdurmaz;
   `card.md`'ye "Codex incelemesi" satırına yazılır.
   Tamam: kademe ve varsa en küçük düzeltme kayıtlı.

4. **Koştur.** `python tools/kx.py push EXP-0xx [--gpu] [--internet]`
   GPU gerektirmeyen her şey CPU'da koşar. Uzun gece koşusundan önce aynı notebook'un
   kısa bir denemesi başarıyla bitmiş olmalı.
   Tamam: `log/RUNS.md`'ye satır düştü.

5. **İzle.** `python tools/kx.py status EXP-0xx`. "İzliyorum" deme; son kontrol saatini yaz.
   Tamam: `STATUS.md`'de son kontrol saati güncel.

6. **İndir ve doğrula.** `python tools/kx.py fetch EXP-0xx`
   Doğrulama başarısızsa **sonuç kayda girmez.** Yeni deney açma, hatayı düzelt.
   Koşu hatası veya eksik çıktı fikre RED yazdırmaz; "koşmadı" olarak kaydedilir.
   Tamam: `EXP_SUMMARY.md`'ye satır düştü.

7. **Karşılaştır.** `python tools/kx.py cmp EXP-0xx`
   Çıktı: ana skor farkı, fold fold farklar, fold farklarının standart sapması, öneri.
   Karar kuralı `CLAUDE.md`'de. **"BELİRSİZ" yok.** KABUL / HAVUZ / RED.
   CV'de beklenmedik büyük sıçrama varsa önce sızıntı araştır.
   Tamam: öneri insana sunuldu, kararı insan verdi.

8. **Kaydet.** `card.md`'yi doldur (Sonuç, Karar, Ders, Codex incelemesi).
   `STATUS.md`'yi güncelle — en üst satır her zaman "insandan sıradaki eylem".
   KABUL ise: ürüne izi tek satır + global istatistikten türeyen feature varsa uyarı notu.
   Tamam: `card.md`, `EXP_SUMMARY.md`, `STATUS.md` üçü de tutarlı.

## Sabit kurallar
- Sonucu alınmış deney klasörü değiştirilmez, yeni deney açılır.
- Hiçbir OOF/test tahmini silinmez. RED çıkanlar da ensemble havuzunda kalır.
- HAVUZ çıkan deney **farklı seed ile tekrar koşulmaz** — yeni bilgiye göre çok pahalı.
- Fark küçükse daha basit/hızlı model korunur.
- Submit etme. Öner; insan gönderdikten sonra `log/SUBMISSIONS.md`'ye yaz.

## İlk baseline'dan hemen sonra
**Hata analizi beş deney beklemez.** Kısa bir OOF hata analizi yap; amaç fikir listesi
üretmek değil, bir sonraki deneyi değiştirecek **tek bulgu** aramaktır. Bulguyu
`log/BACKLOG.md`'ye dayanak olarak yaz.
