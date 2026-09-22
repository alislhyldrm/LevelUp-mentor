---
name: case
description: Yarışma case'ini alır, ham sayfaları kaydeder, 10 dakikalık triyajı çıkarır, case'i insana anlatır ve Onay 1'i (CV + metrik) hazırlar. Kullan - case metni/URL'i/PDF'i paylaşıldığında, yarışma sayfaları güncellendiğinde, "case geldi" dendiğinde.
---

# Case

Çıktı: `case/pages/` (ham) + `case/CASE.md` (triyaj) + D-01 önerisi.
Hedef, ilk 10 dakikada kod yazmaya değil, **neyi ölçtüğümüzü bilmeye** varmak.

## Akış

1. **Al ve ham kaydet.**
   - URL verildiyse WebFetch dene. **30 saniyede gelmezse veya login duvarına takılırsa
     bırak**, yapıştırma iste — Kaggle yarışma sayfaları genelde login arkasındadır.
   - PDF/görüntü verildiyse Read ile oku.
   - Gelen her parçayı **özetlemeden** `case/pages/<kaynak>-<HHMM>.md` altına yaz.
     Çelişkide ham metin hakemdir. Overview, Data, Evaluation, Rules ayrı dosyalardır.
   Tamam: her kaynağın ham metni diskte, yolu biliniyor.

2. **Triyaj — `case/CASE.md` ilk tablosu.** 10 satırın hepsi cevaplanır veya
   "bilinmiyor + nasıl öğrenilecek" yazılır. Tahmin etme.
   Özellikle: **code competition mı**, metrik ve yönü, submission formatı,
   günlük gönderim limiti, internet/süre kısıtı, kural kabulü yapıldı mı.
   Tamam: 10 satır dolu; bilinmeyenler engel olarak işaretli.

3. **Ürün bölümü (15 dk, Onay 1'i bekletmez).** `CASE.md` "Ürün bölümü" dört satırı:
   kullanıcı kim · tahmin hangi kararı destekliyor · gerçek kullanımda hangi girdiler
   olacak · model nerede başarısız olur. **Kod yazma, sadece bu dört satır.**
   Tamam: dört satır dolu.

4. **Veriyi indir.** `kaggle competitions download -c <slug>`. 403 alırsan insana
   "yarışma kurallarını siteden kabul et" de. Veri inerken 5. adım paralel yürür.
   Tamam: dosyalar diskte, boyutları `CASE.md`'de.

5. **Codex çağrısı #1 — metrik + validation denetimi.** `CODEX.md` Çağrı 1.
   **20 dakika sert sınır, EDA ile paralel.** Codex senin öneriyi görmeden kendi
   validation önerisini yazar. Sen kendi önerini ayrı hazırla.
   Çakışma çıkarsa hakem veri kanıtıdır — anlatım gücü değil.
   Tamam: iki öneri ve veri kanıtları elde; çatışma varsa `CODEX.md` kuralı uygulandı.

6. **`core/` sözleşmesini kur.** `core/folds.csv` (satır kimliği + `fold`),
   `core/metric.py` (`score(y_true, y_pred)` + `GREATER_IS_BETTER`), `core/cv_spec.md`
   (ana şema, ana skor, duyarlılık şeması, FAST tanımı). Sonra Kaggle'a
   `hackathon-core` dataset'i olarak yükle, slug'ı `kx.json`'a yaz.
   Tamam: `cv_spec.md` boş alan bırakmadan dolu; dataset Kaggle'da.

7. **Case'i insana anlat.** Özet kod değildir. Beş başlık:
   ne isteniyor · nasıl ölçülüyor · ilk 3 risk · ilk hamle önerisi ·
   ne bilmiyoruz ve nasıl öğreniriz.
   Tamam: insan case'i okumadan ne olduğunu anladı.

8. **✋ Onay 1.** Tek soru sor: CV şeması + metrik + ana skor (`cv_mean` mi `cv_oof` mu).
   Onay gelince `log/DECISIONS.md`'ye D-01 olarak yaz, `STATUS.md`'yi güncelle.
   Tamam: D-01 kayıtlı. Bundan sonra fold ve metrik **sabittir** (CLAUDE.md kural 1).

## Sonra
`log/BACKLOG.md` kurulur (`CODEX.md` Çağrı 4 ile birlikte), `/exp` döngüsü başlar.
**13:30 hedefi, 15:00 sert sınırı: ilk geçerli submission.** Bu olmadan derin feature
işine geçilmez; gerekirse daha basit tahminle gönder.

## Yeni resmi bilgi geldiğinde
Yalnız etkilenen bölümleri güncelle. Metrik, veri, ayrım veya kapsam değiştiyse
`cv_spec.md` sürümlenir ve mevcut en iyi aday yeni sürümde yeniden ölçülür.
Eski ve yeni sözleşmenin skorları aynı tabloda sıralanmaz.
