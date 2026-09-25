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
| D-00 | 25 Eyl | **200 px²'den küçük araçlar kasıtlı olarak tespit edilmez** (hedeflenmez; eğitim/çıktıda ayrı ele alınması veriyi görünce netleşir) | BD s.3: bu araçlar etiketsiz ve puanı etkilemiyor |
| D-01 | 25 Eyl | **CV: tek bölme, %80 train / %20 val**, platformun train+valid'i birleştirilip görüntü düzeyinde iterative stratification (4 sınıf varlık + kutu sayısı), seed 42 (`data/eda_split.py`). Val 1294/6469. Ana skor: val mAP@0.5 (COCO, 4 sınıf ortalaması). Sekans izi yok → gruplar tekil | İnsan: "val %20, her class eşit oranda"; "kodları koş" |
| D-02 | 25 Eyl | **K-02'yi iptal eder: koşuyu ajan yapar**, Colab MCP üzerinden (Google AI Pro Colab). Kod yine insana gösterilir; K-01 (Kaggle'a gönderim yok) geçerli | İnsan: "MCP kur, kodları koş, CLAUDE.md'deki kuralı sil" |
| D-03 | 25 Eyl | **Dış veri kümesi kesinlikle yasak.** Yalnız yarışmanın (Evren'de etiketlenen) verisi kullanılır. Objects365/COCO ön-eğitimli ağırlığın bu yasağa girip girmediği açık soru → insana sorulur, cevap gelmeden uzun koşu yok | İnsan: "ayrı bir veri kümesi kullanamayız, kesinlikle yasak" |
| D-04 | 25 Eyl | **EXP-001 Codex adımı yeni oturumda** (CODEX.md Çağrı 1 + 1b); mevcut `experiments/EXP-001/code.py` taslaktır, Codex incelemesinden önce uzun koşu yok | İnsan: "Codex adımı yeni oturumda olmalı" |
| D-05 | 25 Eyl | **Objects365 ön-eğitimli ağırlık YASAK** (D-03'ün açık sorusu kapandı). EXP-001 sıfırdan eğitime çevrildi: `HGNetv2.pretrained: False`, `-t` yok, base config `dfine_hgnetv2_s_custom.yml`. ImageNet backbone de dış ağırlık sayıldı. Model M→S, epoch planı ölçülen süreye göre 60 | İnsan: "Object 365 yasak" |
