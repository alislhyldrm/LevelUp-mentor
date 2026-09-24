# DECISIONS

İnsanın verdiği kararlar. Tek satır, geri dönülmez kabul edilir.
Yalnız sona ekleme; eski karar değiştirilmez, onu iptal eden yeni karar yazılır.

## Kuruluş kararları (yarışma öncesi)

Bunlar yarışma günü numaralandırmasının dışındadır; `D-01` yarışma günü alınacak
ilk karardır (CV şeması + metrik + ana skor).

| K | Tarih | Karar | Gerekçe |
|---|---|---|---|
| K-01 | 22 Eyl 2026 | **Kaggle'a hiçbir şey gönderilmez.** Ne notebook push, ne dataset yükleme, ne submission. Kaggle'dan yalnız yarışma verisi indirilir | Gönderilen her şeyin insan kontrolünden geçmesi; provada onaysız koşu yaşandı |
| K-02 | 22 Eyl 2026 | **Koşuyu insan yapar.** Ajan tek hücrelik kodu verir, insan Kaggle notebook'una yapıştırıp çalıştırır, ekran çıktısını sohbete verir | Her koşulan kodun insan tarafından görülmesi |
| K-03 | 22 Eyl 2026 | **Tek koşu, tek onay.** Bir koşunun sonucu kaydedilmeden sıradaki kod verilmez | Art arda onaysız koşu birikmesini engellemek |
| K-04 | 22 Eyl 2026 | **Akışta zorunlu submission yok.** Baseline gönderilmez; gönderim kararı insanın, takım değerlendirmesiyle | Gönderim hakları sınırlı, baseline'dan yüksek skor beklenmiyor |
| K-05 | 22 Eyl 2026 | **Tek ortak Kaggle hesabı**, 6 kişilik takım aynı hesaptan çalışır | Takım kararı. Risk bildirildi: Kaggle "kişi başına tek hesap" der; GPU kotası ve eşzamanlı koşu limiti paylaşılır |
| K-06 | 22 Eyl 2026 | **Fold garantisi parmak iziyle.** Dataset yüklenmediği için `core/folds_snippet.py` her koda aynen gömülür; koşu fold parmak izi basar, tutmazsa sonuç kayda girmez | K-01'in teknik sonucu |
| K-07 | 22 Eyl 2026 | **Gece kuyruğu ve nöbet düzeni yok.** Akışta ayrı bir gece aşaması bulunmaz; deney döngüsü tek akıştır | Sistemi tek kişi işletiyor |
| K-08 | 24 Eyl 2026 | **K-03'ü günceller: her koşu kendi onayı, kendi kaydı.** Paralel koşu yalnız insan isterse; aynı anda en çok ölçülen eşzamanlı limit (ölçülmediyse 2), aynı kayıtlı parent'tan, birbirinin sonucuna dayanmadan. Bir sonuca dayanan kod o sonuç kaydedildikten sonra verilir | Sıralı döngüde FULL koşu sürerken hat boşta kalıyordu; onay zaten kod başına veriliyor |
| K-09 | 24 Eyl 2026 | **Gürültü tabanı.** `EXP-001`'den sonra `EXP-002` = aynı kod, yalnız model `SEED` farklı; `kx.py gurultu` tabanı `kx.json` `noise_floor`'a yazar, `cmp` tabanın içindeki farka KABUL önermez | İki özdeş koşunun farkı bilinmeden 5 fold'luk KABUL/RED kararı gürültüye göre verilebiliyordu |

## Yarışma günü kararları

| D | Saat | Karar | Gerekçe |
|---|---|---|---|
| | | | |
