# STATUS — <yarışma> | Cuma 12:00 → Cumartesi 12:00
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ Takım arkadaşlarına `SOZLESME.md`'yi ver, her birine bir yüzlük ata (`kx.json` →
  `owners`, ör. `"3": "ay"`). Case gelince Overview · Data · Evaluation · Rules metnini
  sohbete yapıştır; `/case` oradan başlar.

## Şu an
Faz: HAZIR — case bekleniyor | Ana hat: yok | Son güncelleme: 24 Eyl
Kaggle'da koşan: yok

## Sıradaki 3 iş
1. `/case` → triyaj (11 satır, koşu yeri dahil) → veri indir → `adv_val.py` → `core/` kur → ✋Onay 1
2. Baseline (Codex Çağrı 1b ile) → insan koşturur → gürültü koşusu `EXP-002` → `kx.py gurultu`
3. OOF hata analizi + `log/BACKLOG.md` → ✋Onay 2 → `/exp` döngüsü

## Bu oturumda ne oldu
- Şablon: `fold_hazirla` / `egit` kancaları (fold içi fit), `TEKNIKLER` listesi, Kaggle +
  yerel ortam, `KUCULT`, FAST alt kümesi artık `FOLD_SEED`'e bağlı (hata düzeltmesi).
- Fold şemaları: stratified (parmak izi değişmedi) · kfold · stratified_reg · group ·
  stratified_group · time (+GAP). `make_folds.py --group/--time`.
- `kx.py`: takım yüzlükleri (`owners`), `gurultu` komutu, `cmp` gürültü tabanı.
- `blend.py --rank` + iki gizli hata (y kolonu, id adı) düzeltildi. `adv_val.py` eklendi.
- `SOZLESME.md`: takım kodu şartları + teknik kuralları. K-08, K-09 kaydedildi.
- `python tools/test_kx.py` 45/45.
- `AGENTS.md`: Codex koordinatör modu (Claude limiti dolarsa devralır, `STATUS.md`'den).

## Önceki oturum
- Kurulum ve prova (K-01…K-07).

## Öncesi
- (yok)

## Sabitlenen kararlar
- K-01…K-09 (`log/DECISIONS.md`): Kaggle'a gönderim yok · koşuyu insan yapar · her koşu
  kendi onayı, paralel koşu insan isterse (K-08, K-03'ü günceller) · zorunlu submission
  yok · tek ortak hesap · fold parmak izi · gece kuyruğu yok · gürültü tabanı (K-09).
- D-01 henüz alınmadı (CV şeması + metrik + ana skor).

## Denendi, işe yaramadı
- (yok)

## Aktif riskler
- **OOF dosyaları Kaggle koşusunda yerele gelmiyor.** Ensemble ve hata analizi için insanın
  `oof.parquet` indirmesi gerekir. Yerel koşuda bu risk yok — koşu yeri `/case`'te belli olur.
- **Tek ortak hesap** (K-05): GPU kotası ve eşzamanlı koşu limiti paylaşılıyor,
  ikisi de ölçülmedi. Paralel koşu limiti ölçülene kadar 2.
- `core/metric.py` ROC AUC şablonu, `core/cv_spec.md` boş — ikisi de `/case` doldurur.
- Çok sınıflı hedef: şablon ve `blend.py` tek tahmin kolonu varsayıyor.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. —  2. —  3. —

## Yarışma öncesi kontrol listesi
- [ ] `kaggle competitions download` çalışıyor, hesap ve telefon doğrulaması tamam
- [ ] Kalan GPU kotası ve eşzamanlı koşu limiti ölçülmüş, buraya yazılmış
- [ ] `python tools/kx.py board` ve `python tools/test_kx.py` çalışıyor
- [ ] `SOZLESME.md` takıma verildi, `kx.json` `owners` dolu
- [ ] Yarışma açılır açılmaz kural kabulünü yapacak kişi belli
- [ ] Codex CLI cevap veriyor
