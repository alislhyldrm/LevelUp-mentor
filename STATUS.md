# STATUS — Level Up AI / ROKETSAN Aşama 1 (araç tespiti, D-FINE)
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ (1) Colab sekmesini **açık tut**; EXP-001 koşuyor, ≈11,3 sa (25 Eyl 23:5x başladı).
  Kopar ise: hücre 1 → hücre 2 (otomatik `-r last.pth` ile devam eder, Drive'da checkpoint var).
  (2) Karar bekleyen: **60 epoch bütçesi yeterli mi?** Repo sıfırdan tarifi 220 epoch = ≈41 sa.
  (3) Açık: Kaggle Rules (Colab'da eğitim izni, ağırlığı Kaggle'a taşıma, submission formatı).

## Şu an
Faz: baseline koşuyor | Ana hat: yok (EXP-001 ilk) | Son kontrol: 25 Eyl, koşu 1,5 dk'da, süreç ÇALIŞIYOR
Colab'da koşan: EXP-001 (T4) · Kaggle'da koşan: yok (K-01 — Kaggle'a hiçbir şey gönderilmedi)

## Sıradaki 3 iş
1. EXP-001 bitince hücre 4 → KX RESULT → `card.md` + `log/RUNS.md` güncelle
2. EXP-002 gürültü koşusu (aynı kod, yalnız `SEED` farklı) — ama ≈11,3 sa daha, bütçe insana sorulacak
3. OOF hata analizi + `log/BACKLOG.md` → ✋Onay 2

## Bu oturumda ne oldu
- **D-05 (insan): Objects365 ön-eğitimli ağırlık YASAK** → EXP-001 sıfırdan eğitime çevrildi.
- **Codex Çağrı 1 + 1b koştu** (`gpt-6-astra`; varsayılan `gpt-6-sol` ChatGPT hesabıyla desteklenmiyor).
  1b dört "GEÇERSİZ KILAR" bulgusu verdi; hepsi repoda doğrulandı ve düzeltildi.
- **Taslakta bulunan ve düzeltilen hatalar:** `epoches`→`epochs` (yoksa 60 değil 220 epoch koşardı) ·
  `HGNetv2.pretrained` repo varsayılanı `True` → D-03 ihlali olurdu, artık `assert False` ·
  `pgrep -f 'train.py -c'` kendi kabuğunu eşleştiriyordu · `ev.stats[0]` maxDets=300'de −1 döner ·
  SMOKE ilk-N örneklemesi → sınıf garantili örnekleme · 640→960 regex yerine yapılandırılmış override.
- **GPU ölçüldü: Tesla T4 15,6 GB, 2 CPU çekirdeği, 13,6 GB RAM.** 2 çekirdek dataloader'ı sınırlıyor
  (val'de veri bekleme %44). Bellek 6,9/15,4 GB → batch 16'ya yer var, denenmedi.
- **SMOKE geçti:** 256/128 görüntü, 2 epoch, DOĞRULA satırı tam (num_classes 4, 960 üç yerde,
  pretrained False, epochs 2). Hız ölçüldü: eğitim 0,912 sn/adım, val 0,538 sn/adım (batch 8).
- **Tam koşu başladı:** D-FINE-S sıfırdan, 960, batch 8, 60 epoch, lr 1,414e-4 (sqrt ölçekleme).
  11,3 dk/epoch → ≈11,3 sa. Her epoch `last.pth` Drive'a yazılıyor.
- Bölme parmak izi doğrulandı: train 5175/132.989 `3214f3fa7f9abfe8`, val 1294/32.343 `209e9c83a27b935c`,
  kesişim 0, kategori sırası car/van/truck/bus.
- `maxDets=300` gerekçesi düzeltildi: COCO sınırı görüntü**×sınıf** başına; val'de 7 çift 100'ü aşıyor.

## Önceki oturum
- D-01 (CV %80/%20 stratified seed 42), D-02 (koşuyu ajan yapar), D-03 (dış veri yasak), D-04 (Codex adımı).
- EDA bitti (`data/eda_split.py`), split JSON yazıldı, zip Drive'a yüklendi, Colab MCP kuruldu.
- Ana EDA bulgusu: kutuların %38'i <32² → 960-1280 giriş gerekli, 640 yetmez.

## Öncesi
- Resmi PDF kaydı; Aşama 1 = drone araç tespiti, mAP@0.5, 4 sınıf; 5/gün, toplam 10, final 2.
- Kurulum ve prova (K-01…K-09), `test_kx.py` 45/45.

## Sabitlenen kararlar
- K-01…K-09 (`log/DECISIONS.md`): Kaggle'a gönderim yok · her koşu kendi onayı · zorunlu submission yok ·
  tek ortak hesap · fold parmak izi · gece kuyruğu yok · gürültü tabanı.
- D-00: 200 px² altı araç hedeflenmez (çıktıda filtrelenmiyor, oranı ölçülüyor).
- D-01: tek bölme %80/%20 stratified seed 42; ana skor val mAP@0.5. D-02: koşuyu ajan yapar (Colab MCP).
- D-03: dış veri kesinlikle yasak. **D-05: Obj365 ağırlığı yasak → sıfırdan eğitim** (ImageNet backbone de).

## Denendi, işe yaramadı
- (yok — ilk baseline henüz bitmedi)

## Aktif riskler
- **60 epoch, repo sıfırdan tarifinin %27'si** → model eksik eğitilmiş olacak. LR milestone 51'de düşüyor,
  koşuyu sonradan uzatmak LR açısından bedava değil.
- **`kx.py kayit` koşturulamıyor.** Altyapı tablo şemasında: `core/cv_spec.md` boş, `kx.json`
  `main_score: cv_mean`, `validate_output` `fold_scores`/`cv_oof`/`fold_fingerprint` bekliyor.
  EXP-001 elle `card.md` + `RUNS.md`'de tutuluyor. Tespit için yeniden kurulmalı.
- **Yakın-kopya sızıntısı dışlanmadı** (Codex Çağrı 1): `eda_split.py` yalnız numara farkı ≤2 ve aynı
  çözünürlükteki komşulara bakıyor. D-01 değişmiyor (kural 1), kontrol backlog'a girer.
- **Skor "geçici yerel AP50"** — resmi scorer'ın interpolasyonu/tespit sınırı/ignore kuralı bilinmiyor.
- **En iyi checkpoint AP50:95'e göre seçiliyor**, ana skorumuz AP50. Çakışmayabilir, ölçülmedi.
- **Colab oturumu kopabilir**; checkpoint Drive'da, devam yolu hücre 2'de hazır.
- **Veri kaynağı:** Evren verisinin Kaggle train'i mi ek veri mi olduğu bilinmiyor.
- Sınıf dengesizliği: bus kutuların %3,4'ü.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. Küçük nesne baskın (%38 <32²) → çözünürlük kararı skoru belirler (hipotez, ölçülmedi).
2. 2 CPU çekirdeği 960 çözünürlükte dataloader'ı sınırlıyor (val'de %44 veri bekleme) — ölçüldü.
3. —

## Yarışma öncesi kontrol listesi
- [ ] Kaggle Data/Rules okundu, ENGEL satırları kapandı
- [x] Colab GPU tipi ölçüldü (T4 15,6 GB, 2 CPU)
- [x] D-01 onaylandı, split JSON yazıldı, zip Drive'da, parmak izi koşuda doğrulanıyor
