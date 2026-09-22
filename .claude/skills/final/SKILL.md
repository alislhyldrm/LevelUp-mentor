---
name: final
description: Final teslim kapısı - aday submission'ı sabit 6 maddelik kontrol listesinden geçirir, her maddeyi GEÇTİ/KALDI/DOĞRULANAMADI olarak kanıtla cevaplar. Kullanım - /final <EXP veya dosya>
disable-model-invocation: true
argument-hint: "<EXP-xxx veya submission yolu>"
---

# Final teslim kapısı

23. saatte, uykusuzken en olası felaket "yanlış model fikri" değildir; **yanlış sürümü
seçmek**, satır sırasının kayması, ensemble ağırlıklarının farklı bir OOF setinden
gelmesi, modelin temiz oturumda yüklenmemesi. Sıfır yaratıcılık gerektiren, sabit
listeyle yakalanan hatalar.

**Sabit liste. Serbest inceleme değil.** "Bir kontrol et" demek yorgunken işe yaramaz.

## Kural

> Her madde `GEÇTİ / KALDI / DOĞRULANAMADI` olarak cevaplanır.
> **`KALDI` veya `DOĞRULANAMADI` bulunan aday final için önerilemez.**
> Kanıt olarak dosya yolu, EXP kimliği, koşu/versiyon bilgisi veya kontrol sonucu yazılır.

Kanıt üretilemiyorsa cevap `DOĞRULANAMADI`'dır — "muhtemelen doğru" değil.

## Kontrol listesi

| # | Madde | Kanıt nereden |
|---|---|---|
| 1 | Seçilen dosya hangi EXP, mod, seed ve Kaggle koşu/versiyonundan geldi? | `result.json` + `card.md` |
| 2 | Submission satır sayısı ve ID sırası örnek submission ile birebir aynı mı? | dosyaları karşılaştır, çıktıyı yaz |
| 3 | Tahmin kolonları ve varsa sınıf sırası doğru mu? | `sample_submission` + `artifacts/meta.json` |
| 4 | Ensemble ağırlıkları hangi OOF setiyle hesaplandı; bu OOF'lar submission üreten **aynı model koşularına** mı ait? | `ensemble/` kaydı + her modelin `kernel_version` |
| 5 | Ürün için korunacak model temiz oturumda yüklenip örnek girdiden tahmin üretebildi mi? | yeni süreçte çalıştır, çıktıyı yapıştır |
| 6 | Code competition ise inference notebook'u **internet kapalıyken** temiz oturumda uçtan uca tamamlandı mı? | Kaggle koşu kaydı |

**4. madde en tehlikelisi:** aynı deney adı altında sonradan yeniden çalıştırılmış
modellerin OOF'u ile farklı test tahminlerini karıştırmak sessiz ama ölümcül bir hatadır.
Yalnız EXP numarası değil, **koşu kimliği / Kaggle versiyonu** da eşleşmeli.

## Akış

1. Adayı belirle: `python tools/kx.py board` → en iyi aday, veya insanın verdiği dosya.
2. Altı maddeyi **sırayla** cevapla. Kanıtı komut çıktısıyla göster, hafızadan yazma.
3. Paralel olarak `CODEX.md` Çağrı 5'i tetikle — aynı altı madde, bağımsız ikinci göz.
   İki sonuç çelişirse madde `DOĞRULANAMADI` sayılır ve elle kontrol edilir.
4. Sonucu tablo olarak ver:

       | # | Madde | Sonuç | Kanıt |
       |---|---|---|---|

5. **Karar:**
   - Hepsi `GEÇTİ` → "Bu dosya final aday olarak gönderilebilir" + tek satır gerekçe.
   - Bir tanesi bile değilse → **öneri yok.** Hangi madde, ne eksik, düzeltmek kaç dakika.
6. İnsan gönderdikten sonra `log/SUBMISSIONS.md`'ye satır düş (final aday sütunu dolu).

## Sınır

Submit etme. Bu kapı bir öneri kapısıdır; gönderimi insan yapar.
Zaman kalmadıysa kapıyı atlama — **atlanmış kapı geçmiş kapı değildir**, bunu açıkça söyle.
