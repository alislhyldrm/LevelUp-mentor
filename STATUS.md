# STATUS — <yarışma> | Cuma 12:00 → Cumartesi 12:00
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ Case gelince yarışma sayfalarının metnini (Overview · Data · Evaluation · Rules)
  sohbete yapıştır. `/case` oradan başlar. Hazırlık tarafında bekleyen iş yok.

## Şu an
Faz: HAZIR — case bekleniyor | Ana hat: yok | Son güncelleme: —
Kaggle'da koşan: yok

## Sıradaki 3 iş
1. `/case` → triyaj → veri indir → `core/` kur → ✋Onay 1 (CV + metrik)
2. Baseline (Codex Çağrı 1b ile birlikte) → insan koşturur → skor
3. OOF hata analizi + `log/BACKLOG.md` → ✋Onay 2 → `/exp` döngüsü

## Bu oturumda ne oldu
- (case henüz gelmedi)

## Önceki oturum
- (yok)

## Öncesi
- (yok)

## Sabitlenen kararlar
- K-01…K-07 (`log/DECISIONS.md`): Kaggle'a gönderim yok · koşuyu insan yapar · tek koşu
  tek onay · zorunlu submission yok · tek ortak hesap · fold parmak izi · gece kuyruğu yok.
- D-01 henüz alınmadı (CV şeması + metrik + ana skor).

## Denendi, işe yaramadı
- (yok)

## Aktif riskler
- **OOF dosyaları yerele gelmiyor.** Her koşuda yalnız ekran çıktısı kaydediliyor;
  `blend.py`, ensemble ve HAVUZ kararı OOF dosyasını gerektirir. İlk hata analizinde
  ve ensemble aşamasında insanın `oof.parquet` indirmesi gerekir.
- **Tek ortak hesap** (K-05): GPU kotası ve eşzamanlı koşu limiti paylaşılıyor,
  ikisi de ölçülmedi.
- `core/metric.py` ROC AUC şablonu, `core/cv_spec.md` boş — ikisi de `/case` doldurur.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. —  2. —  3. —

## Yarışma öncesi kontrol listesi
- [ ] `kaggle competitions download` çalışıyor, hesap ve telefon doğrulaması tamam
- [ ] Kalan GPU kotası ve eşzamanlı koşu limiti ölçülmüş, buraya yazılmış
- [ ] `python tools/kx.py board` ve `python tools/test_kx.py` çalışıyor
- [ ] Yarışma açılır açılmaz kural kabulünü yapacak kişi belli
- [ ] Codex CLI cevap veriyor
